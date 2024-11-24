#!/usr/bin/python3.4 -u
from __future__ import absolute_import, division, print_function
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

## Adding the list of devices the configuration needed to be applied ###

list = open('/network/scripts/Ben_Interface_media_type/Input/input.txt', 'r')
list.seek(0)
list = list.readlines()


domain = '.internal.synopsys.com'

responding_list = []
ssh_failed_vpn_devices = []


for x in list:
    x = x.rstrip('\n')
    responding_list.append(x)

devices = []
list1 = []
list2 = []



for devices in responding_list:
    #print ('Connecting to device: ' + devices)
    ip_address_of_devices = devices
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
    command = 'sh ip int br | ex unass|10.|down'
    output = str(net_connect.send_command (command))
    print(devices, output)
    net_connect.disconnect()