#!/usr/bin/python

import requests, re
from sys import argv


api_base_url = argv[1]
api_port = argv[2]
scrutiny_host = argv[3]
headers = {'Accept': 'application/json'}
db = 'nifi_test'
influx_url = "http://" + scrutiny_host + ":8086/write?db=" + db
cluster_status_url = "http://" + api_base_url + ":" + api_port + "/nifi-api/cluster"
cluster_status_response = requests.get(cluster_status_url, headers=headers).json()
composite_components = re.compile('(\d+)(\W+)(\d+(\.\d+)?)( bytes| KB| MB| GB| TB)')


def unit_converter(value, unit):
    value = float(value)
    # print type(value)
    if unit == " KB":
        value = value * 1024
    elif unit == " MB":
        value = value * 1024**2
    elif unit == " GB":
        value = value * 1024**3
    elif unit == " TB":
        value = value * 1024**4
    else:
        value = value
    return int(value);


def main():
    post_data = ''
    for node in cluster_status_response['cluster']['nodes']:
        #split combined queue stat into size and count, convert size to bytes
        queued =  composite_components.match(node['queued'].replace(',', ''))
        queued_count = queued.group(1)
        queued_size = queued.group(3)
        queued_size_units = queued.group(5)
        queued_size_bytes = unit_converter(queued_size, queued_size_units)
        node_id = node['nodeId']
        address = node['address']
        status = node['status']
        primary = node['primary']
        active_threads = node['activeThreadCount']
        heartbeat = node['heartbeat']
        post_data = (
                    'cluster_status' +

                    ',activeThreadCount='+ str(active_threads) +
                    ',queued_count='+ str(queued_count) +
                    ',queued_size='+ str(queued_size_bytes) +
                    ',heartbeat='+ str(heartbeat).replace(' ', '\ ') +
                    ',node_connection_status=' + str(status) +
                    ', cluster_hostname=' + str(api_base_url) +
                    ',nodeId=' + str(node_id) +
                    ',address=' + str(address) +
                    ',primary=' + str(primary) + '\n'
                    )
    r = requests.post(influx_url, post_data)
main()
