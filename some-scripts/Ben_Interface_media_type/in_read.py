# #!/opt/python-2.7.13/bin/python -u
# with open('/network/scripts/Ben_Interface_media_type/Input/in.txt') as f:
#     lines = f.read().split(" ")
# print(lines)
# for x in lines:
#     if "mpls-router" in x:
#         print(x)
#     if "Gig" in x:
#         print(x)

import csv
from netmiko import ConnectHandler
from getpass import getpass
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from time import time
from ftplib import FTP
import json
import os
import signal
import sys
import time
import re
from pprint import pprint
username = 'network-team'
password = 'Iltw@S2017'

reader = csv.DictReader(open("/network/scripts/Ben_Interface_media_type/Input/ben.csv"))
for row in reader:
    ip_address_of_devices = row['devices']
    ios_l2 = {
        'device_type': 'cisco_ios',
        'ip': ip_address_of_devices,
        'username': username,
        'password': password,
    }
    try:
        net_connect = ConnectHandler(**ios_l2)
        time.sleep(1)
    except:
        ssh_failed_vpn_devices.append(devices)
        continue
    command = 'sh int '+row['interfaces']+' | in media'
    output = str(net_connect.send_command(command))
    print(row['devices'], output)
    net_connect.disconnect()

    #print(row['devices'])