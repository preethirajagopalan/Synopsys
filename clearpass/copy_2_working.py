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
"grant_type": "client_credentials",
"client_id": "Token_2021",
"client_secret": "MjCeAWEjxJ2ZpNCAFGu3sEjxfzvImaJtgd9ABxL6bglj"}
r = requests.post(url = API_ENDPOINT, data = data)
pastebin_url = r.text
print(pastebin_url)

# print("The pastebin URL is:%s"%pastebin_url)
# print(pastebin_url['access_token'])
tokens = json.loads(r.text)

access_token_used = (tokens['access_token'])
value = "Bearer"+ " " + access_token_used
#print(value)

#print(str(now)+"test_rest_api.py")
#just a sample get rest api
rg = requests.get(url = 'https://us01cppm01.internal.synopsys.com:443/api/static-host-list?&sort=%2Bid&offset=0&limit=25&calculate_count=false', headers={ 'Authorization': value, 'Content-type': 'application/json'})
print(rg.json())
print(rg.headers)
print(rg.status_code)
with open('/network/scripts/clearpass/test_rest_api_output_copy2.json', 'w+') as f:
    for chunk in rg.iter_content(chunk_size=2048*10000000000):
        if chunk:
            f.write('Printed string %s.\n' % now)
            f.write('\n')
            f.write(chunk)
            f.write('\n')
            f.flush()
rg.close()
