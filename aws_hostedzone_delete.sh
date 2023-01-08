#!/usr/bin/env bash

set -euo pipefail

domains="$*"

delete_zone () {
  for zone in $hostedzones; do
    recordset=$(aws route53 list-resource-record-sets --hosted-zone-id $zone| \
      jq -r '.ResourceRecordSets[]|select(.Type| test("SOA|NS")|not)|
      {"Changes":[{"Action":"DELETE","ResourceRecordSet":.}]}')
    if [[  -n $recordset ]]; then
      changeid=$(aws route53 change-resource-record-sets \
        --hosted-zone-id $zone \
        --change-batch "$recordset"|jq -r '.ChangeInfo.Id')
      while true; do
        sleep 5
        change_status=$(aws route53 get-change --id $changeid|jq -r '.ChangeInfo.Status')
        if [[ $change_status == 'INSYNC' ]]; then
          break
        fi
      done
    fi
    aws route53 delete-hosted-zone --id $zone
  done
}


if [[ -n $domains ]]; then
  for domain in $domains; do
    hostedzones=$(aws route53 list-hosted-zones | \
    jq -r --arg domain "${domain}." '.HostedZones[]|select(.Name == $domain )|
      .Id|sub("/hostedzone/";"")')
    delete_zone
  done
else
  hostedzones=$(aws route53 list-hosted-zones| jq -r '.HostedZones[].Id|sub("/hostedzone/";"")')
  delete_zone
fi
