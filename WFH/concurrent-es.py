# #!/opt/python-2.7.13/bin/python -u
from datetime import date
from elasticsearch import Elasticsearch
from elasticsearch import helpers, Elasticsearch
from elasticsearch.helpers import bulk
import csv
import datetime
import os

now = datetime.datetime.now()
now_str = now.strftime("%Y.%m.%d")
print(now)

# create the object for elastic search
ca_cert = "/remote/devinfra/ca-trust/snpsICA2.pem"
es = Elasticsearch(
              ['ems'],
        http_auth=('network-admin','NetworkTeam'),
        use_ssl=True,
        ca_certs=ca_cert
    )
index_name = 'network-wfh'
type_name = 'network-wfh'

path='/network/scripts/WFH/Output/'
path_files = os.listdir(path)
for file in path_files:
    with open(path + file) as f:
        reader = csv.DictReader(f)
        # for row in reader:
        #     print(row)
        #print(f)
        helpers.bulk(es, reader, index=index_name, doc_type=type_name)
