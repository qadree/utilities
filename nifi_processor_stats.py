#!/usr/bin/python

import requests
from sys import argv

#  Search term should be a processor type for now
api_host = argv[1]
api_port = argv[2]
influx_host = argv[4]
search_term = argv[3]
db = 'nifi'
influx_url = "http://" + influx_host + ":8086/write?db=" + db
api_request_url = "http://" + api_host + ":" + api_port + "/nifi-api"
api_search = api_request_url + '/controller/search-results?q=' + search_term
api_search_response = requests.get(api_search).json()
api_search_processor_results = api_search_response['searchResultsDTO']['processorResults']

def main():
    post_data = ''
    for keys in api_search_processor_results:
        for key in keys['matches']:
            if key == 'Type: ' + search_term:
                processgroup_id = keys['groupId']
                processor_id = keys['id']
                processor_name = keys['name']
                processgroup_url = api_request_url + '/controller/process-groups/' + processgroup_id
                processgroup_name = requests.get(processgroup_url).json()['processGroup']['name']
                processor_url = api_request_url + '/controller/process-groups/' + processgroup_id + '/processors/' + processor_id
                processor_stat_history = requests.get(processor_url + '/status/history').json()
                processor_stat_most_recent = len(processor_stat_history['statusHistory']['statusSnapshots']) - 1
                processor_stat_dict = processor_stat_history['statusHistory']['statusSnapshots'][processor_stat_most_recent]['statusMetrics']
                processor_type = processor_stat_history['statusHistory']['details']['Type']
                for processor_stat_key in processor_stat_dict:
                    post_data = (
                                post_data +
                                processor_stat_key +
                                ',host='+ api_host +
                                ',processor_id=' + processor_id +
                                ',processor_type=' + processor_type +
                                ',processgroup_name=' + processgroup_name.replace(' ', '\ ') +
                                ',processgroup_id=' + processgroup_id +
                                ',processor_name=' + processor_name.replace(' ', '\ ') +
                                ',metric=' + processor_stat_key +
                                ' value=' + str(processor_stat_dict[processor_stat_key]) + '\n'
                                )
    r = requests.post(influx_url, post_data)
main()
