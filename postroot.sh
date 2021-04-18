#!/bin/bash

logfile="REPLACELBPLOGDIR/knxd.log"
date        >> $logfile
chown loxberry $logfile
chgrp loxberry $logfile
chmod 666      $logfile
echo "<INFO> Start KNXd installation" 2>&1
tail -f $logfile &
TAILPID=$!
bash REPLACELBHOMEDIR/system/daemons/plugins/KNXd                  >/dev/null 2>&1 
kill -9 $TAILPID
echo "<INFO> Installation completed. Please wait a while for the background processes to be completed. See Pluing log for details." 2>&1
service rpimonitor status |grep " active " >/dev/null && echo `echo "rpimonitor service IS running, restarting"; service rpimonitor restart` || echo "rpimonitor service NOT running, no restart"
exit 0
