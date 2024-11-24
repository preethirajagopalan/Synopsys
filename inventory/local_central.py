#!/usr/bin/python3.4 -u
from __future__ import absolute_import, division, print_function
import re
import netmiko
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
from pprint import pprint
import itertools
import collections
from collections import Counter
from collections import defaultdict
import json
import ast
from collections import defaultdict
from datetime import date
from datetime import datetime
import datetime
import csv
now = datetime.datetime.utcnow()
ssh_failed_vpn_devices = []
def local_central():
    username = 'network-team'
    password = 'Iltw@S2017'

    ## Adding the list of devices the configuration needed to be applied ###

    list = open('/network/scripts/inventory/Input_Output/vpn.csv', 'r')
    list.seek(0)
    list = list.readlines()

    domain = '.internal.synopsys.com'

    responding_list = []
    devices_list = []
    ssh_failed_vpn_devices = []
    devices = []
    central_sites = []
    local_sites = []

    for devices_list in list:
        devices_list = devices_list.rstrip('\n')
        # devices_list = devices_list + domain
        responding_list.append(devices_list)

    for devices in responding_list:
        print('Connecting to device: ' + devices)
        ip_address_of_devices = devices
        ios_l2 = {
            'device_type': 'cisco_ios',
            'ip': ip_address_of_devices,
            'username': username,
            'password': password,
            'timeout': 5, 'use_keys': False, 'allow_agent': False
        }

        try:
            net_connect = ConnectHandler(**ios_l2)
            time.sleep(1)
        except:
            ssh_failed_vpn_devices.append(devices)
            continue

        command = 'sh ip route 0.0.0.0 | i Known'
        output = net_connect.send_command_timing(command)
        a = output
        print(devices, a)
        if "bgp" in a:
            central_sites.append(devices)
        else:
            local_sites.append(devices)
        net_connect.disconnect()

    local_site_count = len(local_sites)
    central_site_count = len(central_sites)
    print(local_site_count, central_site_count)
    print(ssh_failed_vpn_devices)

    local_dict = [{"network_device_type": "local", "total items": local_site_count}]
    central_dict = [{"network_device_type": "central", "total items": central_site_count}]

    # Combine the list of dictionaries as one list of dictionary (Solarwinds-us + sOLARWINDS-INT)
    C_counts = Counter()
    for l in (local_dict, central_dict):
        # print("counters")
        # print(l)
        C_counts.update({x['network_device_type']: x['total items'] for x in l})
    C = [{'network_device_type': k, 'total items': c} for (k, c) in C_counts.items()]
    # ##########type casting int#########################
    for i in C:
        for key, value in i.items():
            if key == "total items":
                i[key] = int(value)
            if key == "'network_device_type":
                i[key] = str(value)
    final = ast.literal_eval(json.dumps(C))
    time_field = {'@timestamp': now}
    type_field = {'type': "local_central"}
    for n in final:
        n.update(time_field)
        n.update(type_field)
    keys = final[0].keys()
    with open('/network/scripts/inventory/Result/local_central.csv', 'w') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final)
    dictOfWords = {"item": local_sites[i] for i in range(0, len(local_sites))}
    print(dictOfWords)
    with open("/network/scripts/inventory/Input_Output/ssh_failed_vpn_devices.csv", 'w', newline='') as File:
        wrr = csv.writer(File)
        wrr.writerow(ssh_failed_vpn_devices)

if __name__ == "__main__":
    local_central()










