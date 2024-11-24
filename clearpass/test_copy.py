#!/opt/python-2.7.13/bin/python -u
import requests
import json
from datetime import date
from datetime import datetime
import datetime
now = datetime.datetime.now()
# defining the api-endpoint and get a access token using OAUTH2
API_ENDPOINT = "https://10.15.153.78:443/api/oauth"
data = {
"grant_type": "client_credentials",
"client_id": "Preethi_Test_Token",
"client_secret": "VLDJUgbVKybHvcpgdxKeOgo25Facj1+ac18ow/ROBZ3a"}
r = requests.post(url = API_ENDPOINT, data = data, verify=False)
pastebin_url = r.text
print(pastebin_url)

# print("The pastebin URL is:%s"%pastebin_url)
# print(pastebin_url['access_token'])
tokens = json.loads(r.text)

access_token_used = (tokens['access_token'])
value = "Bearer"+ " " + access_token_used
print(value)

data1 ={
    "id": 3017,
    "name": "New Hardware Deployment-Tech Refresh",
    "description": "Use online form to request -White list for new hardware - 1 day expiration",
    "host_format": "list",
    "host_type": "MACAddress",
    "host_entries": [{"host_address": "00:00:AA:22:13:00", "host_address_desc" : "Test 14"},
{"host_address": "00:AA:BB:C1:DD:00", "host_address_desc" : "Test 1F"}
]
}
rg = requests.patch(url = 'https://us01cppm03.internal.synopsys.com:443/api/static-host-list/3017', data = data1, verify=False,headers={ 'Authorization': value, 'Content-type': 'application/json'})


print(rg.status_code)








# print(rg.headers)
# #print(str(now)+"test_rest_api.py")
# #just a sample get rest api
# rg = requests.get(url = 'https://us01cppm03:443/api/static-host-list?&sort=%2Bid&offset=0&limit=25&calculate_count=false', headers={ 'Authorization': value, 'Content-type': 'application/json'})
# #print(rg.json())
# with open('/network/scripts/clearpass/test_rest_api_output.json', 'a') as f:
#     for chunk in rg.iter_content(chunk_size=2048*10000000000):
#         if chunk:
#             f.write('Printed string %s.\n' % now)
#             f.write('\n')
#             f.write(chunk)
#             f.write('\n')
#             f.flush()
# rg.close()
# #print(rg.headers)