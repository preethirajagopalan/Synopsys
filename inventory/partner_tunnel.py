#!/usr/bin/python3.4 -u
from __future__ import absolute_import, division, print_function
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
import re
now = datetime.datetime.utcnow()

ssh_failed_tunnels_devices = []

def cisco():
    total = 0
    total2 = 0
    responding_list = []
    devices_list = []
    devices = []
    central_sites = []
    local_sites = []


    list = open('/network/scripts/inventory/Input_Output/partner_static.csv', 'r')
    list.seek(0)
    list = list.readlines()
    domain = '.internal.synopsys.com'

    for devices_list in list:
        devices_list = devices_list.rstrip('\n')
        responding_list.append(devices_list)
    for devices in responding_list:
        print('Connecting to device: ' + devices)
        ip_address_of_devices = devices
        ios_l2 = {
            'device_type': 'cisco_ios',
            'ip': ip_address_of_devices,
            'username': 'network-team',
            'password': 'Iltw@S2017',
            'timeout': 5, 'use_keys': False, 'allow_agent': False
        }
        try:
            net_connect = ConnectHandler(**ios_l2)
            #print('cisco')
            time.sleep(1)
        except:
            print('failed_cisco')
            ssh_failed_tunnels_devices.append(devices)
            continue

        command = 'sh crypto isakmp sa | i QM_IDLE'
        output1 = net_connect.send_command_timing(command)
        b = output1
        #print(devices, b)
        count = sum(1 for match in re.finditer(r"\bQM_IDLE\b", b))
        total = total + count
        print(total, ssh_failed_tunnels_devices)
        command = 'show crypto ikev2 sa | i READY'
        output2 = net_connect.send_command_timing(command)
        c = output2
        #print(devices, c)
        count2 = sum(1 for match in re.finditer(r"\bREADY\b", c))
        total2 = total2 + count2
        net_connect.disconnect()
        print("preethi")
        print(total)
        print(total2)

        global cisco_total
        cisco_total = total + total2
        print("cisco_total", cisco_total)


def juniper():
    responding_list = []
    devices_list = []
    devices = []
    #ssh_failed_vpn_devices = []
    #print('reading')
    list = open('/network/scripts/inventory/Input_Output/partner_juniper_static.csv', 'r')
    list.seek(0)
    list = list.readlines()

    for devices_list in list:
        devices_list = devices_list.rstrip('\n')
        responding_list.append(devices_list)

    for devices in responding_list:
        print('Connecting to device: ' + devices)
        ip_address_of_devices = devices
        ios_l2 = {
            'device_type': 'juniper_junos',
            'ip': ip_address_of_devices,
            'username': 'admin',
            'password': '.S$utra',
            'timeout': 5, 'use_keys': False, 'allow_agent': False
        }

        try:
            net_connect = ConnectHandler(**ios_l2)
            #print('here')
            time.sleep(1)
        except:
            ssh_failed_tunnels_devices.append(devices)
            continue

        command = 'show security ipsec sa | match "Total active tunnels: " '
        output = net_connect.send_command(command)
        a = output
        res = [int(i) for i in output.split() if i.isdigit()]
        global juniper_total
        juniper_total = res[0]


def cigital():
    responding_list = []
    devices_list = []
    devices = []
    #ssh_failed_vpn_devices = []
    #print('reading')
    list = open('/network/scripts/inventory/Input_Output/partner_cigital_static.csv', 'r')
    list.seek(0)
    list = list.readlines()

    for devices_list in list:
        devices_list = devices_list.rstrip('\n')
        responding_list.append(devices_list)

    for devices in responding_list:
        print('Connecting to device: ' + devices)
        ip_address_of_devices = devices
        ios_l2 = {
            'device_type': 'cisco_asa','ip': ip_address_of_devices,'username': 'network-team','password': 'Iltw@S2017','timeout': 5, 'use_keys': False, 'allow_agent': False
        }

        try:
            net_connect = ConnectHandler(**ios_l2)
            time.sleep(1)
        except:
            ssh_failed_tunnels_devices.append(devices)
            continue

        command = 'show crypto ikev1 sa | i Active SA'
        output = net_connect.send_command(command)
        res = [int(i) for i in output.split() if i.isdigit()]
        global cigital_total
        cigital_total = res[0]


def total():
    global grand_total
    grand_total = cisco_total + juniper_total + cigital_total
    print("grand_total",grand_total)
    partner_dict = [{"network_device_type": "partner_tunnels", "total items": grand_total}]
    partner_final = ast.literal_eval(json.dumps(partner_dict))
    time_field = {'@timestamp': now}
    type_field = {'type': "partner_tunnel"}
    for n in partner_final:
        n.update(time_field)
        n.update(type_field)
    keys = partner_final[0].keys()
    with open('/network/scripts/inventory/Result/partner_tunnels.csv', 'w', newline='') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(partner_final)
    with open("/network/scripts/inventory/Input_Output/ssh_failed_tunnels_devices.csv", 'w', newline='') as resultFile:
        wr = csv.writer(resultFile)
        wr.writerow(ssh_failed_tunnels_devices)




if __name__ == "__main__":
    cisco()
    juniper()
    cigital()
    total()

