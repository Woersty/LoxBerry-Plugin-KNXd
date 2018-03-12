#!/usr/bin/perl
#
# gad_query.pl - read request to groupaddress on KNX/EIB
# Version: v2018.3.11
#
# Copyright (C) 2018 for LoxBerry by Christian Wörstenfeld
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses/>.

use Config::Simple;
use Cwd 'abs_path';
use Time::HiRes qw(usleep);
use warnings;
use strict;

# Used variables
our $pluginconfigfile;
our $plugin_cfg;
our $query_list;
our $query_use;
our $eibURL;
our $groupread;
our $error;
our @gad_items;

# Set variables
$eibURL           = "ip:localhost";
$groupread        = "/usr/lib/knxd/groupread";
$pluginconfigfile = "REPLACELBPCONFIGDIR/knxd.cfg";
$plugin_cfg       = new Config::Simple("$pluginconfigfile");
$query_list       = $plugin_cfg->param('KNXD_GAD_QUERY');
$query_use        = $plugin_cfg->param('KNXD_GAD_QUERY_USE_CB');
$error            = "";

# Check if used flag is set, if not, exit
if ( "$query_use" ne "1")
{
  print "Feature disabled. Exiting.\n";
	exit 0
}

# Read items from config into array
@gad_items = split /~/, $query_list;

# Walk trough array
foreach my $gad_item (@gad_items) 
{
	# Check KNX group address format
	if ($gad_item !~ /^([0-9]|1[0-5])[\/]{1}[0-7]{1}[\/]{1}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$/ )
	{
	  print "Invalid GAD Format for $gad_item \n";
	  $error .= "Invalid GAD Format for $gad_item \n";
	}
	else
	{
		print "Query GAD $gad_item \n";
		system ("$groupread $eibURL $gad_item ");
		if ($? ne 0)
		{
		  print "Error reading GAD $gad_item \n";
		  $error .= "Error reading GAD $gad_item \n";
		}
		else
		{
		  print "Successfully sent read request to GAD $gad_item \n";
		# 250000 microseconds = 250 milliseconds = 0,25 s  
  		usleep(250000);
		}
	}
}

# On errors exit with code 1
if ( "$error" ne "")
{
  print "\nSummary:\n--------\n".$error;
  exit 1;
}
else
{
  print "\nSummary:\n--------\nEverything OK";
	exit 0;
}

