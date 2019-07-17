#!/bin/bash

echo "<INFO> Creating temporary folders for upgrading"
mkdir -p /tmp/REPLACELBPPLUGINDIR

echo "<INFO> Checking existing config file"
egrep "^KNXD_OPTS=" REPLACELBPCONFIGDIR/knxd.cfg >/dev/null 2>&1
if [ $? -eq 0 ]
 then
   echo "<INFO>KNXD_OPTS options found, ok"
   echo "<INFO> Current KNXD_OPTS config is:"
   grep KNXD_OPTS REPLACELBPCONFIGDIR/knxd.cfg
 else
   echo "<INFO>No KNXD_OPTS options found, add them"
   echo 'KNXD_OPTS=""' >> REPLACELBPCONFIGDIR/knxd.cfg
fi

export KNXD_OPTS="`grep KNXD_OPTS REPLACELBPCONFIGDIR/knxd.cfg`"
export KNXD_OPTS=`echo "${KNXD_OPTS/%\"/}"`
if [[ $KNXD_OPTS == *"-b "* ]] || [[ $KNXD_OPTS == *"--layer2 "* ]]; then
  echo "-b option found, proceed..."
else
  echo "-b option not found, will add it..."
  KNXD_OPTS=$KNXD_OPTS" -b ipt:miniserver "
fi

if [[ $KNXD_OPTS == *"-e="* ]] || [[ $KNXD_OPTS == *"--eibaddr="* ]]; then
  echo "-e / --eibaddr option found, proceed..."
else
  echo "-e / --eibaddr option not found, will add it..."
  KNXD_OPTS=$KNXD_OPTS" --eibaddr=0.0.1 "
fi

if [[ $KNXD_OPTS == *"-E="* ]] || [[ $KNXD_OPTS == *"--client-addrs="* ]]; then
  echo "-e / --client-addrs option found, proceed..."
else
  echo "-e / --client-addrs option not found, will add it..."
  KNXD_OPTS=$KNXD_OPTS" --client-addrs=0.0.2:8 "
fi

KNXD_OPTS=$KNXD_OPTS'"'
sed -i  "s%KNXD_OPTS=.*%$KNXD_OPTS%g" REPLACELBPCONFIGDIR/knxd.cfg

echo "<INFO> New KNXD_OPTS config is:"
grep KNXD_OPTS REPLACELBPCONFIGDIR/knxd.cfg

echo "<INFO> Backing up existing config files"
cp -v -r REPLACELBPCONFIGDIR/* /tmp/REPLACELBPPLUGINDIR
