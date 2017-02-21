#!/bin/sh

ARGV0=$0 # Zero argument is shell command
ARGV1=$1 # First argument is temp folder during install
ARGV2=$2 # Second argument is Plugin-Name for scipts etc.
ARGV3=$3 # Third argument is Plugin installation folder
ARGV4=$4 # Forth argument is Plugin version
ARGV5=$5 # Fifth argument is Base folder of LoxBerry

echo "<INFO> Copy back existing config files"
cp -v -r /tmp/uploads/$ARGV1\_upgrade/config/$ARGV3/* $ARGV5/config/plugins/$ARGV3/ 

echo "<INFO> Upgrade-Mode and no new installation for KNXd needed = Remove modify.me file"
rm -f $ARGV5/config/plugins/$ARGV3/modify.me 

echo "<INFO> Copy back existing log files"
cp -v -r /tmp/uploads/$ARGV1\_upgrade/log/$ARGV3/* $ARGV5/log/plugins/$ARGV3/ 

echo "<INFO> Remove temporary folders"
rm -r /tmp/uploads/$ARGV1\_upgrade

/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/system/daemons/plugins/$ARGV2
/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/config/plugins/$ARGV3/knxd.cfg
/bin/sed -i "s#REPLACEBYSUBFOLDER#$ARGV3#" $ARGV5/system/daemons/plugins/$ARGV2
/bin/sed -i "s#REPLACEBYSUBFOLDER#$ARGV3#" $ARGV5/config/plugins/$ARGV3/knxd.cfg
/bin/sed -i "s#REPLACEBYPLUGINNAME#$ARGV2#" $ARGV5/system/daemons/plugins/$ARGV2

/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/webfrontend/cgi/plugins/$ARGV3/bin/server_control.pl
/bin/sed -i "s#REPLACEBYPLUGINNAME#$ARGV2#" $ARGV5/webfrontend/cgi/plugins/$ARGV3/bin/server_control.pl

# Exit with Status 0
exit 0
