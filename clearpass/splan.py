#!/opt/python-2.7.13/bin/python -u
import requests
import json
from datetime import date
from datetime import datetime
import datetime
now = datetime.datetime.now()
# defining the api-endpoint and get a access token using OAUTH2
API_ENDPOINT = "https://us01cppm01.internal.synopsys.com:443/api/oauth"
data = {
"grant_type": "password",
"username": "apiguestsplan",
"password": "mfC2uMq05HU5",
"client_id":"Guest_SPLAN_FAC"}
r = requests.post(url = API_ENDPOINT, data = data)
pastebin_url = r.text
#print(pastebin_url)

# print("The pastebin URL is:%s"%pastebin_url)
# print(pastebin_url['access_token'])
tokens = json.loads(r.text)

access_token_used = (tokens['access_token'])
value = "Bearer"+ " " + access_token_used
print(value)

data1 = {"enabled": True,"username": "abc_pre1", "role_id":2,"password":"1234", "expire_time": "1619415001", "sponsor_profile_name": "CPPM-Guest-Provisioning"}
payload = json.dumps(data1)
rg = requests.post(url = 'https://us01cppm01.internal.synopsys.com:443/api/guest?change_of_authorization=true', data = payload, headers={'Authorization': value,'Content-Type': 'application/json'})
print(rg.text)
# print(rg.headers)
# print(rg.status_code)
#to delete
#https://us01cppm01.internal.synopsys.com:443/api/guest/63873?change_of_authorization=undefined
#rg = requests.post(url = 'https://us01cppm01.internal.synopsys.com:443/api/guest?change_of_authorization=undefined', data = payload, headers={'Authorization': value,'Content-Type': 'application/json'})
