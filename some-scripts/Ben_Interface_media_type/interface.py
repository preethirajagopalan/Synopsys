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
list = []
flattened_list = []
def interfaces():
    username = 'network-team'
    password = 'Iltw@S2017'

    ## Adding the list of devices the configuration needed to be applied ###

    list = open('/network/scripts/some-scripts/Ben_Interface_media_type/Input/input.csv', 'r')
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
    #print(responding_list)

    for devices in responding_list:
        #print('Connecting to device: ' + devices)
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
        # command1 = 'sh ip int br | ex unass'
        # output1 = net_connect.send_command_timing(command1)
        # print(devices_list, output1)
        command = 'sh ip int br | ex unass|10.|down'
        output = net_connect.send_command_timing(command)
        a = output
        b = str(a)
        c = b.split("\n")
        #print(c)
        #print(str(c[1]).split(" "))
        list.append(str(c[1]).split(" "))
        #print("im here after list[1] print")
        final = list[1]
        s = final[0]
        #print(final[0])
        if re.search(r"\bG",s ):
            print(final[0])
        #print("im here in 2 spot")
        if "." in final[0]:
            #print("im here in if")
            port = final[0].rsplit(".")
            #print(port)
            interfacename = str(port[0])
        else:
            #print("im here in else")
            interfacename = str(final[0])
        #print("im here after else")
        #print(str(interfacename))
        command2 = 'sh int '+interfacename+' | i media'
        #print(command2)
        #print("im after command2")
        output2 = net_connect.send_command_timing(command2)
        #print("im before last print")
        orig_stdout = sys.stdout
        f = open('/network/scripts/some-scripts/Ben_Interface_media_type/Input/out.csv', 'w')
        sys.stdout = f
        print(devices_list,output2)
        sys.stdout = orig_stdout
        f.close()

if __name__ == "__main__":
    interfaces()










