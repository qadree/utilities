#!/usr/bin/python

import requests, re
from sys import argv


api_base_url = argv[1]
api_port = argv[2]
host = argv[1]

headers = {'Accept': 'application/json'}
db = 'nifi_test'
influx_url = "http://scrutiny-influx.uptake.com:8086/write?db=" + db
cluster_status_url = "http://" + api_base_url + ":" + api_port + "/nifi-api/cluster"
cluster_status_response = requests.get(cluster_status_url, headers=headers).json()
composite_components = re.compile('(-)?((\d+)(\.\d+)?)( bytes| KB| MB| GB| TB)')
queued_components = re.compile('(\d+)(\W+)(\d+(\.\d+)?)( bytes| KB| MB| GB| TB)')

def node_ids():
    cluster_status_nodes = cluster_status_response['cluster']['nodes']
    for node in cluster_status_nodes:
        node_queued_components = queued_components.match(node['queued'].replace(',', ''))
        size = node_queued_components.group(3)
        units = node_queued_components.group(5)
        node['queued_count'] = node_queued_components.group(1)
        node['queued_size'] = unit_converter(size, units)
        yield node;

def unit_converter(value, unit):
    value = float(value)
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
    return int(round(value));

def node_diagnostics(node_id):
    node_diagnostics_url = "http://" + api_base_url + ":" + api_port + "/nifi-api/cluster/nodes/" + node_id + "/system-diagnostics"
    diagnostics = requests.get(node_diagnostics_url).json()['systemDiagnostics']
    return diagnostics;


def flatten_json(json_input):
    measurements = {}

    def flatten(value, key=''):
        if type(value) is dict:
            for stat in value:
                flatten(value[stat], key + stat + '_')
        elif type(value) is list:
            i = 0
            for stat in value:
                flatten(stat, key + str(i) + '_')
                i += 1
        else:
            measurements[key[:-1]] = value

    flatten(json_input)
    return measurements;


def main():
    for node in node_ids():
        node_jvm_stats = {}
        node_jvm_stats['nodeId'] = node['nodeId']
        node_jvm_stats['status'] = node['status']
        node_jvm_stats['primary'] = node['primary']
        node_jvm_stats['activeThreadCount'] = node['activeThreadCount']
        node_jvm_stats['address'] = node['address']
        node_jvm_stats['queued'] = node['queued'].replace(',', '')
        node_jvm_stats['queued_count'] = node['queued_count']
        node_jvm_stats['queued_size'] = node['queued_size']
        diagnostics = flatten_json(node_diagnostics(node_jvm_stats['nodeId']))
        for stats in diagnostics:
            key = stats
            value = str(diagnostics[stats])
            units = composite_components.match(value)
            if units != None:
                value = unit_converter(units.group(2), units.group(5))
                node_jvm_stats[key] = value
            else:
                node_jvm_stats[key] = value.replace('%', '')
        print(node_jvm_stats)

'''
        post_data = (
                    'nifi_jvm_metrics' +
                    ',address='+ str(node_jvm_stats['address']) +
                    ',cluster_hostname='+ api_base_url +
                    ',nodeId='+ str(node_jvm_stats['nodeId']) +
                    ',node_connection_status=' + str(node_jvm_stats['status']) +
                    ',primary='+ str(node_jvm_stats['primary']) +
                    ',node_connection_status=' + str(node_jvm_stats[]) +
                    ', cluster_hostname=' + str(node_jvm_stats[]) +
                    ',nodeId=' + str(node_jvm_stats[]) +
                    ',address=' + str(node_jvm_stats[]) +
                    ',primary=' + str(node_jvm_stats[]) + '\n'
                    )
    #r = requests.post(influx_url, post_data)

'''
main()
