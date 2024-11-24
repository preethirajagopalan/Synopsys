# #!/opt/python-2.7.13/bin/python -u
from datetime import date
from elasticsearch import Elasticsearch
from elasticsearch import helpers, Elasticsearch
from elasticsearch.helpers import bulk
import csv
import datetime
import os

# find the current date
#now = datetime.datetime.now() - datetime.timedelta(1)
now = datetime.datetime.now()
now_str = now.strftime("%Y.%m.%d")
print(str(now)+ " dc-es-working.py")

# create the object for elastic search
es = Elasticsearch(hosts=[{'host': 'snpstemp054', 'port': 9200}], timeout=400)
index_name = 'network-dc-monitoring' + '-' + now_str
type_name = 'network-dc-monitoring'

request_body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },

            "mappings": {
                "network-dc-monitoring": {
                    "properties": {
                        "Name": {"type": "keyword"},
                        "SiteCode": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "tag": {"type": "long"},
                        "@timestamp": {"type": "date",
                                     "format": "yyyy-MM-dd HH:mm:ss.SSSSSS"},
                        "type": {"type": "keyword"}
                    }}}}
#
#
if not es.indices.exists(index_name):
        print("creating usage profile_index index...")
        es.indices.create(index = index_name, body = request_body)
path='/network/scripts/DC_Monitoring/Output/'
path_files = os.listdir(path)
for file in path_files:
    with open(path + file) as f:
        reader = csv.DictReader(f)
        helpers.bulk(es, reader, index=index_name, doc_type=type_name)
