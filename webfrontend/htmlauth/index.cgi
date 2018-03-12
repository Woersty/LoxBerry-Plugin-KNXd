#!/usr/bin/perl

# Copyright 2016 Christian Woerstenfeld, git@loxberry.woerstenfeld.de
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/perl

# Copyright 2018 Wörsty (git@loxberry.woerstenfeld.de)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

use LoxBerry::System;
use LoxBerry::Web;
use LoxBerry::Log;
use MIME::Base64;
use List::MoreUtils 'true','minmax';
use HTML::Entities;
use CGI::Carp qw(fatalsToBrowser);
use CGI qw/:standard/;
use Config::Simple '-strict';
use warnings;
use strict;
no  strict "refs"; 
#use Data::Dumper;
use HTML::Entities;
use URI::Escape;

# Variables
my $maintemplatefilename 		= "knxd.html";
my $errortemplatefilename 		= "error.html";
my $successtemplatefilename 	= "success.html";
my $helptemplatefilename		= "help.html";
my $pluginconfigfile 			= "knxd.cfg";
my $languagefile 				= "language.ini";
my $logfile 					= "knxd.log";
my $template_title;
my $no_error_template_message	= "<b>KNXd:</b> The error template is not readable. We must abort here. Please try to reinstall the plugin.";
my $version 					= LoxBerry::System::pluginversion();
my $helpurl 					= "http://www.loxwiki.eu/display/LOXBERRY/KNXd";
my @pluginconfig_strings 		= ('KNXD_GAD_DAT','KNXD_GAD_TIM','KNXD_GAD_QUERY','KNXD_GAD_QUERY_USE','KNXD_OPTS');
my @lines						= [];	
my $log 						= LoxBerry::Log->new ( name => 'KNXd', filename => $lbplogdir ."/". $logfile, append => 1 );
my $plugin_cfg 					= new Config::Simple($lbpconfigdir . "/" . $pluginconfigfile);
my %Config 						= $plugin_cfg->vars() if ( $plugin_cfg );
our $error_message				= "";


##########################################################################
# Variables
##########################################################################
our %query;
our $template_title;
our @help;
our $helptext="";
our $installfolder;
our $saveformdata=0;
our $message;
our $nexturl;
our $do;
our @known_urls;
our @url_cfg_data;
our $url_info;
our $url_note;
our $url_id;
our $url_use;
our $url_use_hidden; 
our $url_select="";
our $url_numbers=0;
our @config_params;
our $url_count_id;
our $pluginconfigdir;
our @language_strings;
our @plugin_config_strings;
our $wgetbin;
our $configured_urls="";
our $error=""; 
our $KNXD_GAD_QUERY;
our $HTTP_HOST=$ENV{'HTTP_HOST'};
our $SERVER_PORT=$ENV{'SERVER_PORT'};
my %knx;


# Logging
my $plugin = LoxBerry::System::plugindata();

LOGSTART "New admin call."      if $plugin->{PLUGINDB_LOGLEVEL} eq 7;
$LoxBerry::System::DEBUG 	= 1 if $plugin->{PLUGINDB_LOGLEVEL} eq 7;
$LoxBerry::Web::DEBUG 		= 1 if $plugin->{PLUGINDB_LOGLEVEL} eq 7;
$log->loglevel($plugin->{PLUGINDB_LOGLEVEL});

LOGDEB "Init CGI and import names in namespace R::";
my $cgi 	= CGI->new;
$cgi->import_names('R');

$R::test if 0; # Prevent errors
if ( $R::test ) 
{
	LOGDEB "KNXd status request";
	&test;
}

if ( $R::delete_log )
{
	LOGDEB "Oh, it's a log delete call. ".$R::delete_log;
	LOGWARN "Delete Logfile: ".$logfile;
	my $logfile = $log->close;
	system("/bin/date > $logfile");
	$log->open;
	LOGSTART "Logfile restarted.";
	print "Content-Type: text/plain\n\nOK";
	exit;
}
else 
{
	LOGDEB "No log delete call. Go ahead";
}

LOGDEB "Get language";
my $lang	= lblanguage();
LOGDEB "Resulting language is: " . $lang;

LOGDEB "Check, if filename for the errortemplate is readable";
stat($lbptemplatedir . "/" . $errortemplatefilename);
if ( !-r _ )
{
	LOGDEB "Filename for the errortemplate is not readable, that's bad";
	$error_message = $no_error_template_message;
	LoxBerry::Web::lbheader($template_title, $helpurl, $helptemplatefilename);
	print $error_message;
	LOGCRIT $error_message;
	LoxBerry::Web::lbfooter();
	LOGCRIT "Leaving KNXd Plugin due to an unrecoverable error";
	exit;
}

LOGDEB "Filename for the errortemplate is ok, preparing template";
my $errortemplate = HTML::Template->new(
		filename => $lbptemplatedir . "/" . $errortemplatefilename,
		global_vars => 1,
		loop_context_vars => 1,
		die_on_bad_params=> 0,
		associate => $cgi,
		%htmltemplate_options,
		debug => 1,
		);
LOGDEB "Read error strings from " . $languagefile . " for language " . $lang;
my %ERR = LoxBerry::System::readlanguage($errortemplate, $languagefile);

LOGDEB "Check, if filename for the successtemplate is readable";
stat($lbptemplatedir . "/" . $successtemplatefilename);
if ( !-r _ )
{
	LOGDEB "Filename for the successtemplate is not readable, that's bad";
	$error_message = $ERR{'ERRORS.ERR_SUCCESS_TEMPLATE_NOT_READABLE'};
	&error;
}
LOGDEB "Filename for the successtemplate is ok, preparing template";
my $successtemplate = HTML::Template->new(
		filename => $lbptemplatedir . "/" . $successtemplatefilename,
		global_vars => 1,
		loop_context_vars => 1,
		die_on_bad_params=> 0,
		associate => $cgi,
		%htmltemplate_options,
		debug => 1,
		);
LOGDEB "Read success strings from " . $languagefile . " for language " . $lang;
my %SUC = LoxBerry::System::readlanguage($successtemplate, $languagefile);

LOGDEB "Check, if filename for the maintemplate is readable, if not raise an error";
$error_message = $ERR{'ERRORS.ERR_MAIN_TEMPLATE_NOT_READABLE'};
stat($lbptemplatedir . "/" . $maintemplatefilename);
&error if !-r _;
LOGDEB "Filename for the maintemplate is ok, preparing template";
my $maintemplate = HTML::Template->new(
		filename => $lbptemplatedir . "/" . $maintemplatefilename,
		global_vars => 1,
		loop_context_vars => 1,
		die_on_bad_params=> 0,
		%htmltemplate_options,
		debug => 1
		);
LOGDEB "Read main strings from " . $languagefile . " for language " . $lang;
my %L = LoxBerry::System::readlanguage($maintemplate, $languagefile);

LOGDEB "Check if plugin config file is readable";
if (!-r $lbpconfigdir . "/" . $pluginconfigfile) 
{
	LOGWARN "Plugin config file not readable.";
	LOGDEB "Check if config directory exists. If not, try to create it. In case of problems raise an error";
	$error_message = $ERR{'ERRORS.ERR_CREATE_CONFIG_DIRECTORY'};
	mkdir $lbpconfigdir unless -d $lbpconfigdir or &error; 
	LOGDEB "Try to create a default config";
	$error_message = $ERR{'ERRORS.ERR_CREATE CONFIG_FILE'};
	open my $configfileHandle, ">", $lbpconfigdir . "/" . $pluginconfigfile or &error;
		print $configfileHandle "KNXD_GAD_QUERY_USE=0\n";
		print $configfileHandle "VERSION=\"$version\"\n";
		print $configfileHandle "KNXD_GAD_DAT=\n";
		print $configfileHandle "KNXD_GAD_TIM=\n";
		print $configfileHandle "KNXD_GAD_QUERY=\n";
		print $configfileHandle "KNXD_GAD_DAT_TIM_USE_CB=0\n";
		print $configfileHandle "KNXD_GAD_QUERY_USE_CB=0\n";
		print $configfileHandle "KNXD_OPTS=miniserver\n";
	close $configfileHandle;
	LOGWARN "Default config created. Display error anyway to force a page reload";
	$error_message = $ERR{'ERRORS.ERR_NO_CONFIG_FILE'};
	&error; 
}

LOGDEB "Parsing valid config variables into the maintemplate";
foreach my $config_value (@pluginconfig_strings)
{
	${$config_value} = $Config{'default.' . $config_value};
	if (defined ${$config_value} && ${$config_value} ne '') 
	{
		LOGDEB "Set config variable: " . $config_value . " to " . ${$config_value};
  		$maintemplate->param($config_value	, ${$config_value} );
	}                                  	                             
	else
	{
		LOGINF "Config variable: " . $config_value . " missing or empty.";     
  		$maintemplate->param($config_value	, "");
	}	                                                                
}    
$maintemplate->param( "LBPPLUGINDIR" , $lbpplugindir);

$R::saveformdata if 0; # Prevent errors
LOGDEB "Is it a save call?";
if ( $R::saveformdata ) 
{
	LOGDEB "Yes, is it a save call";
	foreach my $parameter_to_write (@pluginconfig_strings)
	{
	    while (my ($config_variable, $value) = each %R::) 
	    {
			if ( $config_variable eq $parameter_to_write )
			{
				${$value} =~ s/\~+$//g;
				$plugin_cfg->param($config_variable, ${$value});		
				LOGDEB "Setting configuration variable [$config_variable] to value (${$value}) ";
			}
		}
	}
	$plugin_cfg->param('KNXD_GAD_DAT_TIM_USE_CB', $R::KNXD_GAD_DAT_TIM_USE_CB );		
	$plugin_cfg->param('KNXD_GAD_QUERY_USE_CB', $R::KNXD_GAD_QUERY_USE_CB );		
 
	$plugin_cfg->param('VERSION', $version);		
	LOGDEB "Write config to file";
	$error_message = $ERR{'ERRORS.ERR_SAVE_CONFIG_FILE'};
	$plugin_cfg->save() or &error; 

  $message = $ERR{'ERRORS.TXT_ERROR1_CONFIG_SAVED'};
			use IO::Socket::INET;
			
			# auto-flush on socket
			$| = 1;
			
			# create a connecting socket
			my $socket = new IO::Socket::INET (
			PeerHost => '0.0.0.0',
			PeerPort => '5679',
			Proto => 'tcp',
			);
			if ( $socket )
			{
				# data to send to a server
				my $req = 'ReStArT_KnXd';
				my $size = $socket->send($req);
				
				# notify server that request has been sent
				shutdown($socket, 1);
				
				# receive a response of up to 1024 characters from server
				my $response = "";
				$socket->recv($response, 1024);
				$message = $ERR{'ERRORS.'.$response};
				
				$socket->close();
			}
			else
			{
	      $error_message = $ERR{'ERRORS.TXT_ERROR1_CONFIG_SAVED'};
	      &error;
			}


	LOGDEB "Set page title, load header, parse variables, set footer, end";
	$template_title = $SUC{'SAVE.MY_NAME'};
	LoxBerry::Web::lbheader($template_title, $helpurl, $helptemplatefilename);
	$successtemplate->param('SAVE_ALL_OK'		, $SUC{'SAVE.SAVE_ALL_OK'});
	$successtemplate->param('SAVE_MESSAGE'		, $message);
	$successtemplate->param('SAVE_BUTTON_OK' 	, $SUC{'SAVE.SAVE_BUTTON_OK'});
	$successtemplate->param('SAVE_NEXTURL'		, $ENV{REQUEST_URI});
	print $successtemplate->output();
	LoxBerry::Web::lbfooter();
	LOGDEB "Leaving KNXd Plugin after saving the configuration.";
	exit;
}
else
{
	LOGDEB "No, not a save call";
}
LOGDEB "Call default page";

&defaultpage;

#####################################################
# Subs
#####################################################

sub defaultpage 
{
	LOGDEB "Sub defaultpage";
	LOGDEB "Set page title, load header, parse variables, set footer, end";

	$template_title = $L{'KNXD.MY_NAME'};
	LoxBerry::Web::lbheader($template_title, $helpurl, $helptemplatefilename);
	$maintemplate->param( "HTTP_HOST"		, $ENV{HTTP_HOST});
	$maintemplate->param( "HTTP_PATH"		, "/plugins/" . $lbpplugindir);
	$maintemplate->param( "VERSION"			, $version);
	$maintemplate->param( "LOGLEVEL" 		, $L{"KNXD.LOGLEVEL".$plugin->{PLUGINDB_LOGLEVEL}});
	$lbplogdir =~ s/$lbhomedir\/log\///; # Workaround due to missing variable for Logview
	$maintemplate->param( "LOGFILE" , $lbplogdir . "/" . $logfile );
	LOGDEB "Check for pending notifications for: " . $lbpplugindir . " " . $L{'KNXD.MY_NAME'};
	my $notifications = LoxBerry::Log::get_notifications_html($lbpplugindir, $L{'KNXD.MY_NAME'});
	LOGDEB "Notifications are:\n".encode_entities($notifications) if $notifications;
	LOGDEB "No notifications pending." if !$notifications;
    $maintemplate->param( "NOTIFICATIONS" , $notifications);


	foreach my $knx_parameter_to_process ('KNXD_GAD_DAT_TIM_USE_CB','KNXD_GAD_QUERY_USE_CB')
	{
		if ( int($plugin_cfg->param($knx_parameter_to_process)) eq 1 ) 
		{
			$knx{$knx_parameter_to_process} = 1; 
		    $knx{$knx_parameter_to_process. "_script"} = '$("#'.$knx_parameter_to_process . '_checkbox'.'").prop("checked", 1);';
		}
		else
		{
			$knx{$knx_parameter_to_process} = 0; 
		    $knx{$knx_parameter_to_process. "_script"}  = '	$("#'.$knx_parameter_to_process . '_checkbox").prop("checked", 0);';
		}
		$knx{$knx_parameter_to_process. "_script"}  = $knx{$knx_parameter_to_process. "_script"} . '
		$("#'.$knx_parameter_to_process . '_checkbox").on("change", function(event) 
		{ 
			if ( $("#'.$knx_parameter_to_process . '_checkbox").is(":checked") ) 
			{ 
				$("#'.$knx_parameter_to_process.'").val(1); 
				$("label[for=\''.$knx_parameter_to_process . '_checkbox\']" ).removeClass( "ui-checkbox-off" ).addClass( "ui-checkbox-on" );
			} 
			else 
			{ 
				$("#'.$knx_parameter_to_process .'").val(0); 
				$("label[for=\''.$knx_parameter_to_process . '_checkbox\']" ).removeClass( "ui-checkbox-on" ).addClass( "ui-checkbox-off" );
			}
		});
		$("#'.$knx_parameter_to_process . '_checkbox").trigger("change");';
	
		
		LOGDEB "Set special parameter " . $knx_parameter_to_process . " to " . $knx{$knx_parameter_to_process} ;
		$maintemplate->param( ${knx_parameter_to_process}. "_script"   , $knx{$knx_parameter_to_process. "_script"} );
		$maintemplate->param( ${knx_parameter_to_process}              , $knx{$knx_parameter_to_process}	 );
		$maintemplate->param( ${knx_parameter_to_process} . "_checkbox", $knx{$knx_parameter_to_process. "_checkbox"} );
	}
	



    print $maintemplate->output();
	LoxBerry::Web::lbfooter();
	LOGDEB "Leaving KNXd Plugin normally";
	exit;
}

sub error 
{
	LOGDEB "Sub error";
	LOGERR $error_message;
	LOGDEB "Set page title, load header, parse variables, set footer, end with error";
	$template_title = $ERR{'ERRORS.MY_NAME'} . " - " . $ERR{'ERRORS.ERR_TITLE'};
	LoxBerry::Web::lbheader($template_title, $helpurl, $helptemplatefilename);
	$errortemplate->param('ERR_MESSAGE'		, $error_message);
	$errortemplate->param('ERR_TITLE'		, $ERR{'ERRORS.ERR_TITLE'});
	$errortemplate->param('ERR_BUTTON_BACK' , $ERR{'ERRORS.ERR_BUTTON_BACK'});
	print $errortemplate->output();
	LoxBerry::Web::lbfooter();
	LOGDEB "Leaving KNXd Plugin with an error";
	exit;
}

#####################################################
# Test-Sub to check if KNXd Control Server is up
#####################################################

	sub test
	{
			LOGDEB "Open socket to KNXd Control Server...";
			print "Content-Type: text/html\n\n";
			use IO::Socket::INET;
			# auto-flush on socket
			$| = 1;
			# create a connecting socket
			my $socket = new IO::Socket::INET (
			PeerHost => '0.0.0.0',
			PeerPort => '5679',
			Proto => 'tcp',
			);
			if ( $socket )
			{
				LOGINF "Socket to KNXd Control Server opened...";
				# data to send to a server
				my $req = 'StAtUs_KnXd';
				my $size = $socket->send($req);
				
				# notify server that request has been sent
				shutdown($socket, 1);
				
				# receive a response of up to 1024 characters from server
				my $response = "";
				$socket->recv($response, 1024);
				$message = $response;
				
				$socket->close();
				print $response ;
				LOGOK "Response: $response";
				LOGINF "Socket to KNXd Control Server closed.";
			}
			else
			{
				LOGERR "Open socket to KNXd Control Server failed. Set status to down.";
				print "KNXD_STATUS_DOWN" ;
			}
		exit;
	}

