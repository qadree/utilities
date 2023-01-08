#!/usr/bin/python

import requests
from sys import argv

#  Search term should be a processor type for now
search_term = argv[3]
api_base_url = argv[1]
#api_base_url = "staging-cat-nifi-master-new.uptake.com"
api_port = argv[2]
headers = {'Accept': 'application/json'}
db = 'nifi'
influx_url = "http://scrutiny-influx.uptake.com:8086/write?db=" + db
# http://production-cat-nifi-remoteapis-1.uptake.com:8080/nifi-api
api_request_url = "http://" + api_base_url + ":" + api_port + "/nifi-api"
api_search = api_request_url + '/controller/search-results?q=' + search_term
api_search_response = requests.get(api_search).json()
api_search_processor_results = api_search_response['searchResultsDTO']['processorResults']

def main():
    post_data = ''
    for keys in api_search_processor_results:
        for key in keys['matches']:
            if key == 'Type: ' + search_term:
                processgroup_id = keys['groupId']
                processgroup_name = requests.get(api_request_url + '/cluster/process-groups/' + processgroup_id + '/status', headers=headers).json()['clusterProcessGroupStatus']['processGroupName']
                processor_id = keys['id']
                processor_name = keys['name']
                processor_url = api_request_url + '/cluster/processors/' + processor_id
                processor_stat_history = requests.get(processor_url + '/status/history', headers=headers).json()
                processor_stat_most_recent = len(processor_stat_history['clusterStatusHistory']['clusterStatusHistory']['statusSnapshots']) - 1
                processor_stat_dict = processor_stat_history['clusterStatusHistory']['clusterStatusHistory']['statusSnapshots'][processor_stat_most_recent]['statusMetrics']
                processor_type = processor_stat_history['clusterStatusHistory']['clusterStatusHistory']['details']['Type']
                for processor_stat_key in processor_stat_dict:
                    post_data = (
                                post_data +
                                processor_stat_key +
                                ',host='+ api_base_url +
                                ',processor_id=' + processor_id +
                                ',processor_type=' + processor_type +
                                ',processgroup_name=' + processgroup_name.replace(' ', '\ ') +
                                ',processgroup_id=' + processgroup_id +
                                ',processor_name=' + processor_name.replace(' ', '\ ') +
                                ',metric=' + processor_stat_key +
                                ' value=' + str(processor_stat_dict[processor_stat_key]) + '\n'
                                )
    r = requests.post(influx_url, post_data)
    print post_data
main()
