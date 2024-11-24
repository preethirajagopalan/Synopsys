#!/opt/python-2.7.13/bin/python -u
# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


data = \
    'credential_0=network-team&credential_1=Iltw@S2017&destination=/&login=Log In'
headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'Cache-Control': 'no-cache'}

ampsession = requests.Session()
loginamp = ampsession.post('https://10.15.95.250/LOGIN',
                           headers=headers, data=data, verify=False)

result = ampsession.get('https://10.15.95.250/amp_stats.xml',
                        headers=headers, verify=False)

aplist = result.text
print(aplist)
with open('/network/scripts/inventory/Result/data.xml', 'w') as f:
    f.write(result.text)
tree = ET.parse('/network/scripts/inventory/Result/data.xml')
root = tree.getroot()

global ap_count

for description in root.iter('up_wireless'):
    # print(description.text)
    ap_count = description.text

print(ap_count)

