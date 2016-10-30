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


##########################################################################
# Modules
##########################################################################

use CGI::Carp qw(fatalsToBrowser);
use CGI qw/:standard/;
use Config::Simple;
use File::HomeDir;
use Data::Dumper;
use Cwd 'abs_path';
use HTML::Entities;
use URI::Escape;
use warnings;
use strict;
no  strict "refs"; # we need it for template system

##########################################################################
# Variables
##########################################################################
our $cfg;
our $plugin_cfg;
our $phrase;
our $namef;
our $value;
our %query;
our $lang;
our $template_title;
our @help;
our $helptext="";
our $installfolder;
our $languagefile;
our $version;
our $saveformdata=0;
our $message;
our $nexturl;
our $do="form";
my  $home = File::HomeDir->my_home;
our $psubfolder;
our $languagefileplugin;
our $phraseplugin;
our %Config;
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
our $pluginconfigfile;
our @language_strings;
our @plugin_config_strings;
our $wgetbin;
our $configured_urls="";
our $error=""; 
our $KNXD_GAD_QUERY;
our $HTTP_HOST=$ENV{'HTTP_HOST'};
our $SERVER_PORT=$ENV{'SERVER_PORT'};

##########################################################################
# Read Settings
##########################################################################

# Version of this script
	$version = "1.0";

# Figure out in which subfolder we are installed
	$psubfolder = abs_path($0);
	$psubfolder =~ s/(.*)\/(.*)\/(.*)$/$2/g;

#Set directories + read LoxBerry config
	$cfg              = new Config::Simple("$home/config/system/general.cfg");
	$installfolder    = $cfg->param("BASE.INSTALLFOLDER");
	$lang             = $cfg->param("BASE.LANG");

#Set directories + read Plugin config
	$pluginconfigdir  = "$home/config/plugins/$psubfolder";
	$pluginconfigfile = "$pluginconfigdir/knxd.cfg";
	$plugin_cfg       = new Config::Simple("$pluginconfigfile");

# Go through all the plugin config options

	foreach my $key (keys %{ $plugin_cfg->vars() } ) 
	{
		(my $plugin_cfg_section,my $plugin_cfg_varname) = split(/\./,$key,2);
		push @plugin_config_strings, $plugin_cfg_varname;
	}
	
	foreach our $plugin_config_string (@plugin_config_strings)
	{
		${$plugin_config_string} = $plugin_cfg->param($plugin_config_string);
	}	
# Everything from URL
	foreach (split(/&/,$ENV{'QUERY_STRING'}))
	{
	  ($namef,$value) = split(/=/,$_,2);
	  $namef =~ tr/+/ /;
	  $namef =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	  $value =~ tr/+/ /;
	  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	  $query{$namef} = $value;
	}

# Set parameters coming in - get over post
	if ( !$query{'saveformdata'} ) { if ( param('saveformdata') ) { $saveformdata = quotemeta(param('saveformdata')); } else { $saveformdata = 0;      } } else { $saveformdata = quotemeta($query{'saveformdata'}); }
	if ( !$query{'lang'} )         { if ( param('lang')         ) { $lang         = quotemeta(param('lang'));         } else { $lang         = $lang;  } } else { $lang         = quotemeta($query{'lang'});         }
	if ( !$query{'do'} )           { if ( param('do')           ) { $do           = quotemeta(param('do'));           } else { $do           = "form"; } } else { $do           = quotemeta($query{'do'});           }

# Init Language
# Clean up lang variable
	$lang         =~ tr/a-z//cd; 
	$lang         = substr($lang,0,2);
	# If there's no language phrases file for choosed language, use german as default
	if (!-e "$installfolder/templates/system/$lang/language.dat") 
	{
		$lang = "de";
	}

# Read translations / phrases
	$languagefile 			= "$installfolder/templates/system/$lang/language.dat";
	$phrase 						= new Config::Simple($languagefile);
	$languagefileplugin = "$installfolder/templates/plugins/$psubfolder/$lang/language.dat";
	$phraseplugin 			= new Config::Simple($languagefileplugin);
	foreach my $key (keys %{ $phraseplugin->vars() } ) 
	{
		(my $cfg_section,my $cfg_varname) = split(/\./,$key,2);
		push @language_strings, $cfg_varname;
	}
	foreach our $template_string (@language_strings)
	{
		${$template_string} = $phraseplugin->param($template_string);
	}		
 $KNXD_GAD_QUERY =~ s/\~/\n/g;
 # Clean up saveformdata variable
 $saveformdata =~ tr/0-1//cd; 
 $saveformdata = substr($saveformdata,0,1);

##########################################################################
# Main program
##########################################################################

	if ($saveformdata) 
	{
	  print "Content-Type: text/html\n\n"; 
		&save;
	}
	elsif ( $do eq "test")
	{
	  print "Content-Type: text/html\n\n"; 
		&test;
	}
	else 
	{
	  print "Content-Type: text/html\n\n"; 
		&form;
	}
	exit;

#####################################################
# 
# Subroutines
#
#####################################################

#####################################################
# Form-Sub
#####################################################

	sub form 
	{
		# The page title read from language file + plugin name
		$template_title = $phrase->param("TXT0000") . ": " . $phraseplugin->param("MY_NAME");

		# Print Template header
		&lbheader;
		
		# Parse the strings we want
		open(F,"$installfolder/templates/plugins/$psubfolder/$lang/settings.html") || die "Missing template plugins/$psubfolder/$lang/settings.html";
		while (<F>) 
		{
			$_ =~ s/<!--\$(.*?)-->/${$1}/g;
		  print $_;
		}
		close(F);

		# Parse page footer		
		&footer;
		exit;
	}

#####################################################
# Test-Sub to check if KNXd Control Server is up
#####################################################

	sub test
	{
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
			}
			else
			{
				print "KNXD_STATUS_DOWN" ;
			}
		exit;
	}

#####################################################
# Save-Sub
#####################################################

	sub save 
	{
		# Write configuration file
		@config_params 		= param; 
		our $save_config 	= 0;
		$url_count_id 		= 1;
		
		# Write all lines into config
		for our $config_id (0 .. $#config_params)
		{
			if ($config_params[$config_id] eq "saveformdata" && param($config_params[$config_id]) eq 1)
			{
				$save_config = 1;
			}
			else
			{
	 			$CGI::LIST_CONTEXT_WARN = 0;
				$plugin_cfg->param($config_params[$config_id], param($config_params[$config_id]));
		 	  $CGI::LIST_CONTEXT_WARN = 1;
			}
			$config_id ++;
		}
		if ($save_config eq 1)
		{
			use Config::Simple '-strict';
			$plugin_cfg->delete("default.KNXD_GAD_DAT_TIM_USE_checkbox");
			$plugin_cfg->delete("default.KNXD_GAD_QUERY_USE_checkbox");
			$plugin_cfg->save();
      $message = $phraseplugin->param("TXT_ERROR1_CONFIG_SAVED");
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
				$message = $phraseplugin->param($response);
				
				$socket->close();
			}
			else
			{
	      $error = $phraseplugin->param("TXT_ERROR1_CONFIG_SAVED");
	      &error;
			}
		}
		else
		{
			exit(1);
		}
		$template_title = $phrase->param("TXT0000") . ": " . $phraseplugin->param("MY_NAME");
		$nexturl 				= "./index.cgi?do=form";
		
		# Print Template
		&lbheader;
		open(F,"$installfolder/templates/system/$lang/success.html") || die "Missing template system/$lang/succses.html";
		  while (<F>) 
		  {
		    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
		    print $_;
		  }
		close(F);
		&footer;
		exit;
	}

#####################################################
# Error-Sub
#####################################################

	sub error 
	{
		$template_title = $phrase->param("TXT0000") . " - " . $phrase->param("TXT0028");
		
		&lbheader;
		open(F,"$installfolder/templates/system/$lang/error.html") || die "Missing template system/$lang/error.html";
    while (<F>) 
    {
      $_ =~ s/<!--\$(.*?)-->/${$1}/g;
      print $_;
    }
		close(F);
		&footer;
		exit;
	}

#####################################################
# Page-Header-Sub
#####################################################

	sub lbheader 
	{
		 # Create Help page
	  open(F,"$installfolder/templates/plugins/$psubfolder/$lang/help.html") || die "Missing template plugins/$psubfolder/$lang/help.html";
 		  while (<F>) 
		  {
		     $_ =~ s/<!--\$(.*?)-->/${$1}/g;
		     $helptext = $helptext . $_;
		  }

	  close(F);
	  open(F,"$installfolder/templates/system/$lang/header.html") || die "Missing template system/$lang/header.html";
	    while (<F>) 
	    {
	      $_ =~ s/<!--\$(.*?)-->/${$1}/g;
	      print $_;
	    }
	  close(F);
	}

#####################################################
# Footer
#####################################################

	sub footer 
	{
	  open(F,"$installfolder/templates/system/$lang/footer.html") || die "Missing template system/$lang/footer.html";
	    while (<F>) 
	    {
	      $_ =~ s/<!--\$(.*?)-->/${$1}/g;
	      print $_;
	    }
	  close(F);
	}
