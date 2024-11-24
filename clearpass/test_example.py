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
"password": "Fac_2021",
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

#print(str(now)+"test_rest_api.py")
#just a sample get rest api
rg = requests.get(url = 'https://us01cppm01.internal.synopsys.com:443/api/guest?filter=%7B%7D&sort=-id&offset=0&limit=25&calculate_count=false', headers={ 'Authorization': value, 'Content-type': 'application/json'})
#print(rg.json())
with open('/network/scripts/clearpass/test_rest_api_output1.json', 'w+') as f:
    for chunk in rg.iter_content(chunk_size=2048*10000000000):
        if chunk:
            f.write('Printed string %s.\n' % now)
            f.write('\n')
            f.write(chunk)
            f.write('\n')
            f.flush()
rg.close()
#print(rg.headers)