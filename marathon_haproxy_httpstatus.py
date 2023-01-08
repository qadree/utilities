import csv
import requests

host = 'example.com' 

ha_proxy_url_1 = 'http://' + host + ':9090/haproxy?stats;csv'

ha_stats_response_1 = requests.get(ha_proxy_url_1).content.decode(encoding='utf-8')
ha_stats_1 = ha_stats_response_1.lstrip('# ').splitlines()
csv_dict_1 = csv.DictReader(ha_stats_1)

fields_1 = csv_dict_1.fieldnames

print('\n mlb-1')
for i in csv_dict_1:
    if i['pxname'] == 'marathon_http_in':
        print('5xx responses: ' + i['hrsp_5xx'] + '\n' +
              '4xx responses: ' + i['hrsp_4xx'] + '\n' +
              '2xx responses: ' + i['hrsp_2xx'])



