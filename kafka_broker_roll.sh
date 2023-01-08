
zk_host=127.0.0.1
command='sudo systemctl restart kafka'
sleep_time=30
broker_ids=($(zkCli -server ${zk_host}:2181 ls /kafka/brokers/ids|tail -n1|grep -Eo '[[:digit:]]+'))
controller_id=$(zkCli -server ${zk_host}:2181 get /kafka/controller 2>/dev/null|grep -Eo '{[[:print:]]+}'|jq -r .brokerid)

for i in ${!broker_ids[@]}; do
  if [ $controller_id == ${broker_ids[$i]} ]; then
    unset broker_ids[$i]
    brokers="${!broker_ids[@]} ${controller_id}"
    break
  fi
done

broker_ids=$brokers

for broker_id in $broker_ids; do
    while true; do
      host=$(zkCli -server ${zk_host}:2181 get /kafka/brokers/ids/$broker_id 2>/dev/null|grep -Eo '{[[:print:]]+}'|jq -r .host)
      ip=$(dig A +short $host)
      echo "Checking $ip for under replicated topics"
      if [[ -n $(kafkacat -b $ip -L -J|jq '.topics|map(select( any(.partitions[]; (.isrs|length) < (.replicas|length) )))|.[].topic') ]]; then
        echo "Topics are under replicated, will check again in $sleep_time seconds"
        sleep $sleep_time
      else
        echo "No under replicated topics found."
        echo "Executing $command on $ip"
        ssh -qo "StrictHostKeyChecking=no" ${ip} $command
        break
      fi
      #printf "%02s%40s%18s\n" "$broker_id" "$host" "$ip"
    done
done
