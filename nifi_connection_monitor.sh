#!/bin/bash
#Created by Qadree Woodland, to send VictorOps alert for any disconnected node
#Edited by Ilan Arlin, July 7, 2017 - Added check for already running, and expanded state_message, and a few other little things
#Should run in cron, probably every ten minutes to ensure a restart if script ends for any reason.
#Example:
#*/10 * * * * /usr/local/bin/nifi_connection_monitor.sh >> /var/log/nifi_connection_monitor.log 2>&1

#This section checks for already running, so that this script will be restarted if it has ended, but will NOT run multiple concurrent copies.
count=`ps aux | grep nifi-app.log | grep -v grep | wc -l`
if [ "$count" -gt "0" ]; then
    exit
fi

echo "`date`: nifi_connection_monitor.sh (re)started"

alert="disconnected"
victorops_url='https://alert.victorops.com/integrations/generic/20131114/alert/1a44e077-c65f-4ed3-b659-14a03706f68e/soc'
hostname=`hostname`
thisscript=$0

tail -n 0 -F /opt/nifi/logs/nifi-app.log 2>/dev/null | \
while read log_line; do
  echo "$log_line" | grep -iq $alert
  if [ $? = 0 ]; then
     host_ip=`echo $log_line | grep -oE '(socketAddress=)([0-9]+(\.[0-9]+)+)' |cut -f2 -d'='`
    curl -X POST -d '{"entity_id":"Nifi Node '$host_ip' '$alert'","message_type":"critical","state_message":"Node '$host_ip' '$alert' alert from script '$thisscript' on server '$hostname'."}' $victorops_url
  fi
done

