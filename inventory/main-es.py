# #!/opt/python-2.7.13/bin/python -u
from collections import defaultdict
from datetime import date
from elasticsearch import Elasticsearch
from elasticsearch import helpers, Elasticsearch
from elasticsearch.helpers import bulk
import csv
import datetime
import os
now = datetime.datetime.now()
now_str = now.strftime("%Y.%m.%d")
print(now_str)

# create the object for elastic search
#es = Elasticsearch(hosts=[{'host': 'snpstemp054', 'port': 9200}], timeout=400)
ca_cert = "/remote/devinfra/ca-trust/snpsICA2.pem"
es = Elasticsearch(
              ['ems'],
        http_auth=('network-admin','NetworkTeam'),
        use_ssl=True,
        ca_certs=ca_cert
    )
#index_name = 'network-dashboard' + '-' + now_str
index_name = 'network-dashboard'
type_name = 'network-dashboard'

request_body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },

            "mappings": {
                "network-dashboard": {
                    "properties": {
                        "network_device_type": {"type": "keyword"},
                        "items": {"type": "keyword"},
                        "total items": {"type": "long"},
                        "type": {"type": "keyword"},
                        "machinetype": {"type": "keyword"},
                        "vendor": {"type": "keyword"},
                        "Device": {"type": "keyword"},
                        "serialnumber": {"type": "keyword"},
                        "@timestamp": {"type": "date",
                                       "format": "yyyy-MM-dd HH:mm:ss.SSSSSS"}
                    }}}}


if not es.indices.exists(index_name):
        print("creating usageprofile_index index...")
        es.indices.create(index = index_name, body = request_body)

path = '/network/scripts/inventory/Result/'
path_files = os.listdir(path)
print(path_files)
for file in path_files:
    print(file)
    with open(path + file) as f:
        reader = csv.DictReader(f)
        helpers.bulk(es, reader, index=index_name, doc_type=type_name)







