#!/usr/bin/perl
#
# eibtime.pl - Send time and date to KNX/EIB
# Version: 2.0
#
# Copyright (C) 2008 Thomas Hoerndlein
# Adapted for LoxBerry by Christian Wörstenfeld
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
use warnings;
use strict;

# Used variables
our $homefolder;
our $pluginconfigdir;
our $pluginconfigfile;
our $plugin_cfg;
our $psubfolder;
our $grptime;
our $grpdate;
our $datetimeuse;
our $sec;
our $min;
our $hour;
our $mon;
our $year;
our $mday;
our $wday;
our $yday;
our $isdst;
our $byte1;
our $byte2;
our $byte3;
our $eibURL;
our $groupwrite;
our $error;

# Set variables
$eibURL           = "ip:localhost";
$groupwrite       = "/usr/lib/knxd/groupwrite";
$homefolder       = abs_path($0);
$homefolder       =~ s/(.*)\/(.*)\/(.*)\/(.*)\/(.*)\/(.*)\/(.*)$/$1/g;
$psubfolder       = abs_path($0);
$psubfolder       =~ s/(.*)\/(.*)\/(.*)\/(.*)$/$2/g;
$pluginconfigdir  = $homefolder."/config/plugins/".$psubfolder;
$pluginconfigfile = "$pluginconfigdir/knxd.cfg";
$plugin_cfg       = new Config::Simple("$pluginconfigfile");
$grptime          = $plugin_cfg->param('KNXD_GAD_TIM');
$grpdate          = $plugin_cfg->param('KNXD_GAD_DAT');
$datetimeuse      = $plugin_cfg->param('KNXD_GAD_DAT_TIM_USE');
$error            = "";

# Check if used flag is set, if not, exit
if ( "$datetimeuse" ne "on")
{
  print "Feature disabled. Exiting.\n";
	exit 0
}

# Check KNX group address format
if ($grptime  !~ /^([0-9]|1[0-5])[\/]{1}[0-7]{1}[\/]{1}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$/ )
{
  print "Invalid Time-GAD $grptime\n";
  exit 1;
}
if ($grpdate !~ /^([0-9]|1[0-5])[\/]{1}[0-7]{1}[\/]{1}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$/ )
{
  print "Invalid Date-GAD $grpdate\n";
  exit 1;
}

# Get local time
($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);

# localtime sunday is 0, KNX sunday is 7
$wday = 7 if !$wday;     

# Calculate KNX time and send on bus
$byte1 = sprintf "%lx", $wday * 32 + $hour;
$byte2 = sprintf "%lx", $min;
$byte3 = sprintf "%lx", $sec;
print "System-Time: Day $wday $hour:$min:$sec  = KNX-Time: $byte1 $byte2 $byte3 \n";
system ("$groupwrite $eibURL $grptime $byte1 $byte2 $byte3");
if ($? ne 0)
{
  $error = "Error sending time to Time-GAD $grptime.\n";
}
else
{
  print "Time successfully sent to Time-GAD $grptime.\n";
}

# Calculate KNX date and send on bus
$byte1 = sprintf "%lx", $mday;
$byte2 = sprintf "%lx", $mon + 1;
$byte3 = sprintf "%lx", $year - 100;

print "System-Date: $mday ", $mon + 1, " ", $year - 100, " = KNX-Date: $byte1 $byte2 $byte3\n";
system ("$groupwrite  $eibURL $grpdate $byte1 $byte2 $byte3");
if ($? ne 0)
{
  $error = "Error sending date to Date-GAD $grpdate.\n";
}
else
{
  print "Date successfully sent to Date-GAD $grpdate.\n";
}

# On errors exit with code 1
if ( "$error" ne "")
{
  print $error;
  exit 1;
}
exit 0;
