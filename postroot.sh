#!/bin/bash

logfile="REPLACELBPLOGDIR/knxd.log"
date        >> $logfile
chown loxberry $logfile
chgrp loxberry $logfile
chmod 666      $logfile
echo "Start KNXd installation, for further infos see Plugin logfile" >>$logfile 2>&1
bash REPLACELBHOMEDIR/system/daemons/plugins/KNXd                    >>$logfile 2>&1 &
exit 0
