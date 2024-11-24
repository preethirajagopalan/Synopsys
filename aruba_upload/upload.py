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
from pprint import pprint

username = input("Enter your SSH username: ")
password = getpass()

## Adding the list of devices the configuration needed to be applied ###

list = open('text.txt', 'r')
list.seek(0)
list = list.readlines()

domain = '.internal.synopsys.com'

responding_list = []
switch_data = []
data_list = []
devices_list = []

for devices_list in list:
        devices_list = devices_list.rstrip('\n')
        devices_list = devices_list + domain
        responding_list.append(devices_list)

devices = []

for devices in responding_list:
    print ('Connecting to device: ' + devices)
    ip_address_of_devices = devices
    ios_l2 = {
             'device_type': 'aruba_os',
             'ip': ip_address_of_devices,
             'username': username,
             'password': password,
              }
    net_connect = ConnectHandler(**ios_l2)
    time.sleep(1)
    copyftp = 'copy ftp: 10.12.237.213 networkadmin /aruba/ArubaOS_70xx_6.4.4.16_61809 system: partition 1'
    output = net_connect.send_command_timing(copyftp)

    if 'Password:' in output:
        output += net_connect.send_command_timing('Fsck16!!')

    #output = net_connect.send_command_timing('boot system partition 0')
    output = net_connect.send_command ('show image version')
    print (output)
    net_connect.disconnect()