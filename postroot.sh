#!/bin/bash

logfile="REPLACELBPLOGDIR/knxd.log"
date        >> $logfile
chown loxberry $logfile
chgrp loxberry $logfile
chmod 666      $logfile
echo "<INFO> Start KNXd installation, for further infos see Plugin logfile" 2>&1
bash REPLACELBHOMEDIR/system/daemons/plugins/KNXd                    2>&1 
echo "<INFO> Installation completed" 2>&1
exit 0
