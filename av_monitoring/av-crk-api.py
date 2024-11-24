#!/opt/python-2.7.13/bin/python -u
#comments
import requests
import json
from datetime import date
from datetime import datetime
import datetime
now = datetime.datetime.utcnow()
print(str(now)+" av-crk-api.py")
# print("im here")
r = requests.get(url = 'https://api.ciscospark.com/v1/devices/?start=0&max=1000', headers={ 'Authorization': 'Bearer YzU5ZGQ0NDctMGUwNy00NDNiLThiMDEtMDY2Y2E3ZDE5MTk3Yzg4MDAzYWItMGI4_PF84_8ae73c79-2089-459f-863f-1b6547df8b0c', 'Content-type': 'application/json'})
print(r.json())
with open('/network/scripts/av_monitoring/Input/crk_output.json', 'w+') as f:
    for chunk in r.iter_content(chunk_size=2048*10000000000):
        if chunk:
            f.write(chunk)
            f.flush()
r.close()
print(r.headers)
