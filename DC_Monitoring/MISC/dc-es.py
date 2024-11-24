# #!/opt/python-2.7.13/bin/python -u
from datetime import date
from elasticsearch import Elasticsearch
from elasticsearch import helpers, Elasticsearch
from elasticsearch.helpers import bulk
import csv
import datetime
import os

# find the current date
now = datetime.datetime.now()
now_str = now.strftime("%Y.%m.%d")
print(str(now)+ " dc-es.py")

# create the object for elastic search
ca_cert = "/remote/devinfra/ca-trust/snpsICA2.pem"
es = Elasticsearch(
              ['ems'],
        http_auth=('network-admin','NetworkTeam'),
        use_ssl=True,
        ca_certs=ca_cert
    )

index_name = 'network-dc-monitor'
type_name = 'network-dc-monitoring'


path='/network/scripts/DC_Monitoring/Output/'
path_files = os.listdir(path)
for file in path_files:
    with open(path + file) as f:
        reader = csv.DictReader(f)
        # print(f)
        helpers.bulk(es, reader, index=index_name, doc_type=type_name)
