#!/bin/sh

# Bashscript which is executed by bash *AFTER* complete installation is done
# (but *BEFORE* postupdate). Use with caution and remember, that all systems
# may be different! Better to do this in your own Pluginscript if possible.
#
# Exit code must be 0 if executed successfull.
#
# Will be executed as user "loxberry".
#
# We add 5 arguments when executing the script:
# command <TEMPFOLDER> <NAME> <FOLDER> <VERSION> <BASEFOLDER>
#
# For logging, print to STDOUT. You can use the following tags for showing
# different colorized information during plugin installation:
#
# <OK> This was ok!"
# <INFO> This is just for your information."
# <WARNING> This is a warning!"
# <ERROR> This is an error!"
# <FAIL> This is a fail!"

# To use important variables from command line use the following code:
ARGV0=$0 # Zero argument is shell command
#echo "<INFO> Command is: $ARGV0"

ARGV1=$1 # First argument is temp folder during install
#echo "<INFO> Temporary folder is: $ARGV1"

ARGV2=$2 # Second argument is Plugin-Name for scipts etc.
#echo "<INFO> (Short) Name is: $ARGV2"

ARGV3=$3 # Third argument is Plugin installation folder
#echo "<INFO> Installation folder is: $ARGV3"

ARGV4=$4 # Forth argument is Plugin version
#echo "<INFO> Installation folder is: $ARGV4"

ARGV5=$5 # Fifth argument is Base folder of LoxBerry
#echo "<INFO> Base folder is: $ARGV5"

# Replace real subfolder and scriptname in config file and create subfolder.dat in CGI folder
echo "<INFO> Replace informations in daemon and config file"
/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/system/daemons/plugins/$ARGV2
/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/config/plugins/$ARGV3/knxd.cfg
/bin/sed -i "s#REPLACEBYSUBFOLDER#$ARGV3#" $ARGV5/system/daemons/plugins/$ARGV2
/bin/sed -i "s#REPLACEBYSUBFOLDER#$ARGV3#" $ARGV5/config/plugins/$ARGV3/knxd.cfg
/bin/sed -i "s#REPLACEBYPLUGINNAME#$ARGV2#" $ARGV5/system/daemons/plugins/$ARGV2

/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/webfrontend/cgi/plugins/$ARGV3/bin/server_control.pl
/bin/sed -i "s#REPLACEBYPLUGINNAME#$ARGV2#" $ARGV5/webfrontend/cgi/plugins/$ARGV3/bin/server_control.pl


echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO>  "
echo "<INFO> *******************************************************************************"
echo "<INFO> * Please reboot your LoxBerry to start the KNXd Installation.                  "
echo "<INFO> * Warning! This will take a long time! Be patient, please!                     "
echo "<INFO> * I suggest to do it in the night during sleep.                                "
echo "<INFO> * You can use the plugin Logfile for details and progress information.         "
echo "<INFO> *******************************************************************************"
echo "<INFO> * Bitte den LoxBerry neu starten um die KNXd Installation zu starten.          "
echo "<INFO> * Warnung! Das dauert wirklich lange! Geduld, bitte!                           "
echo "<INFO> * Ich empfehle, es in der Nacht beim Schlafen zu machen!                       "
echo "<INFO> * Die Plugin Logdatei kann benutzt werden um Details und Fortschritt zu sehen. "
echo "<INFO> *******************************************************************************"

# Exit with Status 0
exit 0
