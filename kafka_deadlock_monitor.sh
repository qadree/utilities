#!/bin/bash

victorops_url=$1
kafka_pid=$(systemctl -p MainPID show kafka|grep -Eo '[0-9]+')
dump_file="/home/centos/jstack_$(hostname)"

if [ $kafka_pid == 0 ]; then
 break
else
 jstack -l $kafka_pid|tee ${dump_file}|grep 'deadlock'
 if [ $? == 0 ]; then
  mv ${dump_file}{,_$(date "+%m%d%H%M%Y")}
  curl -X POST -d '
    {
    "entity_id":"Deadlocked threads on EMD staging - '$(hostname)'"'',
    "message_type":"critical",
    "state_message":"Thread deadlock detected."
    }' $victorops_url
 fi
fi
