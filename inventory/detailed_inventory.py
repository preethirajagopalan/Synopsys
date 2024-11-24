#!/opt/python-2.7.13/bin/python -u
from elasticsearch import Elasticsearch
import pyodbc
import datetime
import smtplib
import MySQLdb
from helper import get_password
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
from dateutil.tz import tzutc
import csv
import itertools
now = datetime.datetime.utcnow()
a = []
r = []
result = []
op_r = []
op_result = []
lt = []
lt1 = []
lt3 =  []


def detailed():
    password = get_password()
    global ACI_STUFF, CLEARPASS_SERVER, CONTROLLER_GUEST, CONTROLLER_LOCAL, CONTROLLER_MASTER, CONTROLLER_RAP, JUNOS_PULSE, NON_NETWORK_STUFF, PAN_DC_FW, PAN_INTERNET_FW, RIVERBED, ROUTER, ROUTER_MPLS, ROUTER_SW_MODULE, ROUTER_VPN, SCS_STUFF, SWITCH_ACCESS, SWITCH_CORE, SWITCH_DC, SWITCH_DMZ, SWITCH_IP_MGMT, SWITCH_LAB
    global INT_ACI_STUFF, INT_CLEARPASS_SERVER, INT_CONTROLLER_GUEST, INT_CONTROLLER_LOCAL, INT_CONTROLLER_MASTER, INT_CONTROLLER_RAP, INT_JUNOS_PULSE, INT_NON_NETWORK_STUFF, INT_PAN_DC_FW, INT_PAN_INTERNET_FW, INT_RIVERBED, INT_ROUTER, INT_ROUTER_MPLS, INT_ROUTER_SW_MODULE, INT_ROUTER_VPN, INT_SCS_STUFF, INT_SWITCH_ACCESS, INT_SWITCH_CORE, INT_SWITCH_DC, INT_SWITCH_DMZ, INT_SWITCH_IP_MGMT, INT_SWITCH_LAB
    # connection to US-SQL
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    # cursor for the database
    cursor = conn_ussql.cursor()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SWITCH_DC' and caption is not null;""")
    # gather all data from Solarwinds-US-SQL
    SWITCH_DC = cursor.fetchall()
    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'ACI_STUFF' and caption is not null;""")
    ACI_STUFF = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'CLEARPASS_SERVER' and caption is not null;""")
    CLEARPASS_SERVER = cursor.fetchall()

    cursor.execute("""SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_GUEST' and caption is not null;""")
    CONTROLLER_GUEST = cursor.fetchall()

    cursor.execute("""SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_LOCAL' and caption is not null;""")
    CONTROLLER_LOCAL = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_MASTER' and caption is not null;""")
    # gather all data from Solarwinds-US-SQL
    CONTROLLER_MASTER = cursor.fetchall()
    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_RAP' and caption is not null;""")
    CONTROLLER_RAP = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'JUNOS_PULSE' and caption is not null;""")
    JUNOS_PULSE = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'NON_NETWORK_STUFF' and caption is not null;""")
    NON_NETWORK_STUFF = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'PAN_DC_FW' and caption is not null;""")
    PAN_DC_FW = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'PAN_INTERNET_FW' and caption is not null;""")
    PAN_INTERNET_FW = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'RIVERBED' and caption is not null;""")
    RIVERBED = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'ROUTER' and caption is not null;""")
    ROUTER = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'ROUTER_MPLS' and caption is not null;""")
    ROUTER_MPLS = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'ROUTER_SW_MODULE' and caption is not null;""")
    ROUTER_SW_MODULE = cursor.fetchall()
    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'ROUTER_VPN' and caption is not null;""")
    ROUTER_VPN = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SCS_STUFF' and caption is not null;""")
    SCS_STUFF = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SWITCH_ACCESS' and caption is not null;""")
    SWITCH_ACCESS = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SWITCH_CORE' and caption is not null;""")
    SWITCH_CORE = cursor.fetchall()
    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SWITCH_DC' and caption is not null;""")
    SWITCH_DC = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SWITCH_DMZ' and caption is not null;""")
    SWITCH_DMZ = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SWITCH_IP_MGMT' and caption is not null;""")
    SWITCH_IP_MGMT = cursor.fetchall()

    cursor.execute(
        """SELECT Caption FROM [dbo].[Nodes] where Network_Device_Type = 'SWITCH_LAB' and caption is not null;""")
    SWITCH_LAB = cursor.fetchall()

    # connection to intl-SQL
    conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    # cursor for the database
    cursor_int = conn_intsql.cursor()




    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_LAB' and caption is not null;""")
    INT_SWITCH_LAB = cursor_int.fetchall()

    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_IP_MGMT' and caption is not null;""")
    INT_SWITCH_IP_MGMT = cursor_int.fetchall()

    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_DMZ' and caption is not null;""")
    INT_SWITCH_DMZ = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_DC' and caption is not null;""")
    INT_SWITCH_DC = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_CORE' and caption is not null;""")
    INT_SWITCH_CORE = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_ACCESS' and caption is not null;""")
    INT_SWITCH_ACCESS = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SCS_STUFF' and caption is not null;""")
    INT_SCS_STUFF = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'ROUTER_VPN' and caption is not null;""")
    INT_ROUTER_VPN = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'ROUTER_SW_MODULE' and caption is not null;""")
    INT_ROUTER_SW_MODULE = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'ROUTER_MPLS' and caption is not null;""")
    INT_ROUTER_MPLS = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'ROUTER' and caption is not null;""")
    INT_ROUTER = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'RIVERBED' and caption is not null;""")
    INT_RIVERBED = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'PAN_INTERNET_FW' and caption is not null;""")
    INT_PAN_INTERNET_FW = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'PAN_DC_FW' and caption is not null;""")
    INT_PAN_DC_FW = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'NON_NETWORK_STUFF' and caption is not null;""")
    INT_NON_NETWORK_STUFF = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'JUNOS_PULSE' and caption is not null;""")
    INT_JUNOS_PULSE = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_RAP' and caption is not null;""")
    INT_CONTROLLER_RAP = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_MASTER' and caption is not null;""")
    INT_CONTROLLER_MASTER = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_LOCAL' and caption is not null;""")
    INT_CONTROLLER_LOCAL = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'CONTROLLER_GUEST' and caption is not null;""")
    INT_CONTROLLER_GUEST = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'CLEARPASS_SERVER' and caption is not null;""")
    INT_CLEARPASS_SERVER = cursor_int.fetchall()
    cursor_int.execute(
        """SELECT Caption FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'ACI_STUFF' and caption is not null;""")
    INT_ACI_STUFF = cursor_int.fetchall()

    print(ACI_STUFF)
    global mach_int, mach_us, us1, us2, us3, us4, us5, us6, us7, us8, us9, us10, us11, us12, us13, us14, us15, us16, us17, us18, us19, us20, us21, us22, int1, int2, int3, int4, int5, int6, int7, int8, int9, int10, int11, int12, int13, int14, int15, int16, int17, int18, int19, int20, int21, int22
    us1 = list(itertools.chain(*ACI_STUFF))
    us2 = list(itertools.chain(*CLEARPASS_SERVER))
    us3 = list(itertools.chain(*CONTROLLER_GUEST))
    us4 = list(itertools.chain(*CONTROLLER_LOCAL))
    us5 = list(itertools.chain(*CONTROLLER_MASTER))
    us6 = list(itertools.chain(*CONTROLLER_RAP))
    us7 = list(itertools.chain(*JUNOS_PULSE))
    us8 = list(itertools.chain(*NON_NETWORK_STUFF))
    us9 = list(itertools.chain(*PAN_DC_FW))
    us10 = list(itertools.chain(*PAN_INTERNET_FW))
    us11 = list(itertools.chain(*RIVERBED))
    us12 = list(itertools.chain(*ROUTER))
    us13 = list(itertools.chain(*ROUTER_MPLS))
    us14 = list(itertools.chain(*ROUTER_SW_MODULE))
    us15 = list(itertools.chain(*ROUTER_VPN))
    us16 = list(itertools.chain(*SCS_STUFF))
    us17 = list(itertools.chain(*SWITCH_ACCESS))
    us18 = list(itertools.chain(*SWITCH_CORE))
    us19 = list(itertools.chain(*SWITCH_DC))
    us20 = list(itertools.chain(*SWITCH_DMZ))
    us21 = list(itertools.chain(*SWITCH_IP_MGMT))
    us22 = list(itertools.chain(*SWITCH_LAB))
    int1 = list(itertools.chain(*INT_ACI_STUFF))
    int2 = list(itertools.chain(*INT_CLEARPASS_SERVER))
    int3 = list(itertools.chain(*INT_CONTROLLER_GUEST))
    int4 = list(itertools.chain(*INT_CONTROLLER_LOCAL))
    int5 = list(itertools.chain(*INT_CONTROLLER_MASTER))
    int6 = list(itertools.chain(*INT_CONTROLLER_RAP))
    int7 = list(itertools.chain(*INT_JUNOS_PULSE))
    int8 = list(itertools.chain(*INT_NON_NETWORK_STUFF))
    int9 = list(itertools.chain(*INT_PAN_DC_FW))
    int10 = list(itertools.chain(*INT_PAN_INTERNET_FW))
    int11 = list(itertools.chain(*INT_RIVERBED))
    int12 = list(itertools.chain(*INT_ROUTER))
    int13 = list(itertools.chain(*INT_ROUTER_MPLS))
    int14 = list(itertools.chain(*INT_ROUTER_SW_MODULE))
    int15 = list(itertools.chain(*INT_ROUTER_VPN))
    int16 = list(itertools.chain(*INT_SCS_STUFF))
    int17 = list(itertools.chain(*INT_SWITCH_ACCESS))
    int18 = list(itertools.chain(*INT_SWITCH_CORE))
    int19 = list(itertools.chain(*INT_SWITCH_DC))
    int20 = list(itertools.chain(*INT_SWITCH_DMZ))
    int21 = list(itertools.chain(*INT_SWITCH_IP_MGMT))
    int22 = list(itertools.chain(*INT_SWITCH_LAB))



def list_to_dict(GIVEN_LIST, GIVEN_TYPE):
    list1 = []

    for x in GIVEN_LIST:
        d = {}
        d['network_device_type'] = GIVEN_TYPE
        d['items'] = x
        d['@timestamp'] = now
        d['type'] = "detailed"
        list1.append(d)

    #print(list1)
    return list1
def remove_u(x):
    x = ast.literal_eval(json.dumps(x))
    return x
# def big_list():
#     biggie = list(itertools.chain.from_iterable(zip(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18,a19, a20,a21, a22)))
#     return biggie

def combined_list_of_dicts(given_r):
    r.extend(given_r)
    for myDict in r:
        if myDict not in result:
            result.append(myDict)
    return result

def optimized_riverbed():
    on_prem_services = ['RSYNC', 'SNAPMIRROR', 'HTTP 80', 'PERFORCE', 'FTP', 'CIFS', 'SRDF', 'HTTPS', 'CITRIX']
    cloud_services = ['BOX', 'O365', 'O365 WEB APPS', 'O365 USER IDENTITY', 'SALESFORCE', 'SUCCESSFACTORS']



    for x in on_prem_services:
        d1 = {}
        d1['network_device_type'] = 'riverbed_onprem_services'
        d1['items'] = x
        d1['@timestamp'] = now
        d1['type'] = "Optimized_Services"
        lt.append(d1)
    for y in cloud_services:
        d2 = {}
        d2['network_device_type'] = 'riverbed_cloud_services'
        d2['items'] = y
        d2['@timestamp'] = now
        d2['type'] = "Optimized_Services"
        lt1.append(d2)
    return lt, lt1
#(lt, lt1)


def optimized_list_combined(given_r):
    op_r.extend(given_r)
    for myDict in op_r:
        if myDict not in op_result:
            op_result.append(myDict)
    return op_result
def monitoring():
    monitoring_services = ['LIVEACTION', 'SOLARWINDS', 'CAPE SENSORS', 'ELK']
    for x in monitoring_services:
        d3 = {}
        d3['network_device_type'] = 'monitoring_services'
        d3['items'] = x
        d3['@timestamp'] = now
        d3['type'] = "Synopsys_Monitoring_Services"
        lt3.append(d3)
    return lt3

def machinetype():
    global MACHINE_TYPE_US, MACHINE_TYPE_INT, items, items_int
    password = get_password()
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor = conn_ussql.cursor()
    cursor.execute("""SELECT distinct MachineType as MachineType, Vendor as Vendor, Network_Device_Type as Network_Device_Type FROM [dbo].[Nodes] WHERE Vendor != 'Windows' and Vendor! = 'Unknown';""")
    MACHINE_TYPE_US = cursor.fetchall()
    items = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in MACHINE_TYPE_US]
    cursor.close()
    conn_ussql.close()
    password = get_password()
    conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor_int = conn_intsql.cursor()
    cursor_int.execute(
        """SELECT distinct MachineType as MachineType, Vendor as Vendor, Network_Device_Type as Network_Device_Type FROM [NetPerfMonInt].[dbo].[Nodes] WHERE Vendor != 'Windows' and Vendor! = 'Unknown';""")
    MACHINE_TYPE_INT = cursor_int.fetchall()
    items_int = [dict(zip([key[0].lower() for key in cursor_int.description], row)) for row in MACHINE_TYPE_INT]
    cursor_int.close()
    conn_intsql.close()
    global f1, f2
    print(items_int)
    f1 = ast.literal_eval(json.dumps(items))
    f2 = ast.literal_eval(json.dumps(items_int))
    time_field = {'@timestamp': now}
    type_field = {'type': "MachineType_US"}
    for n in f1:
        n.update(time_field)
        n.update(type_field)
    type_field2 = {'type': "MachineType_INT"}
    for n2 in f2:
        n2.update(time_field)
        n2.update(type_field2)
    keys = f1[0].keys()
    with open('/network/scripts/inventory/Result/mach_us.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(f1)
    keys = f2[0].keys()
    with open('/network/scripts/inventory/Result/mach_int.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(f2)
    return f1, f2

def serial():
    global serial_us, serial_int, s_us, s_int
    password = get_password()
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor = conn_ussql.cursor()
    cursor.execute(
        """SELECT [NetPerfMonUS].[dbo].[Nodes].[Caption] as items, [NetPerfMonUS].[dbo].[HWH_HardwareInfo].[ServiceTag] as serialnumber
FROM [NetPerfMonUS].[dbo].[Nodes] 
join [NetPerfMonUS].[dbo].[HWH_HardwareInfo] on
[NetPerfMonUS].[dbo].[Nodes].[NodeID] = [NetPerfMonUS].[dbo].[HWH_HardwareInfo].[ID] 
WHERE [NetPerfMonUS].[dbo].[HWH_HardwareInfo].[ServiceTag] IS NOT NULL and 
[NetPerfMonUS].[dbo].[HWH_HardwareInfo].[ServiceTag] != '' and [NetPerfMonUS].[dbo].[Nodes].[Network_Device_Type] != 'NON_NETWORK_STUFF';""")
    serial_us = cursor.fetchall()
    s_us = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in serial_us]
    cursor.close()
    conn_ussql.close()
    password = get_password()
    conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor_int = conn_intsql.cursor()
    cursor_int.execute(
        """SELECT [NetPerfMonInt].[dbo].[Nodes].[Caption] as items, [NetPerfMonInt].[dbo].[HWH_HardwareInfo].[ServiceTag] as serialnumber
FROM [NetPerfMonInt].[dbo].[Nodes] 
join [NetPerfMonInt].[dbo].[HWH_HardwareInfo] on
[NetPerfMonInt].[dbo].[Nodes].[NodeID] = [NetPerfMonInt].[dbo].[HWH_HardwareInfo].[ID] 
WHERE [NetPerfMonInt].[dbo].[HWH_HardwareInfo].[ServiceTag] IS NOT NULL and 
[NetPerfMonInt].[dbo].[HWH_HardwareInfo].[ServiceTag] != '' and [NetPerfMonInt].[dbo].[Nodes].[Network_Device_Type] != 'NON_NETWORK_STUFF';""")
    serial_int = cursor_int.fetchall()
    s_int = [dict(zip([key[0].lower() for key in cursor_int.description], row)) for row in serial_int]
    cursor_int.close()
    conn_intsql.close()
    global s1, s2
    s1 = ast.literal_eval(json.dumps(s_us))
    s2 = ast.literal_eval(json.dumps(s_int))
    time_field = {'@timestamp': now}
    type_field = {'type': "Serial_us"}
    for n in s1:
        n.update(time_field)
        n.update(type_field)
    type_field2 = {'type': "Serial_int"}
    for n2 in s2:
        n2.update(time_field)
        n2.update(type_field2)
    keys = s1[0].keys()
    with open('/network/scripts/inventory/Result/serial_us.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(s1)
    keys = s2[0].keys()
    with open('/network/scripts/inventory/Result/serial_int.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(s2)
    return s1, s2










if __name__ == "__main__":
    detailed()
    r1 = remove_u(us1)
    r2 = remove_u(us2)
    r3 = remove_u(us3)
    r4 = remove_u(us4)
    r5 = remove_u(us5)
    r6 = remove_u(us6)
    r7 = remove_u(us7)
    r8 = remove_u(us8)
    r9 = remove_u(us9)
    r10 = remove_u(us10)
    r11 = remove_u(us11)
    r12 = remove_u(us12)
    r13 = remove_u(us13)
    r14 = remove_u(us14)
    r15 = remove_u(us15)
    r16 = remove_u(us16)
    r17 = remove_u(us17)
    r18 = remove_u(us18)
    r19 = remove_u(us19)
    r20 = remove_u(us20)
    r21 = remove_u(us21)
    r22 = remove_u(us22)
    ir1 = remove_u(int1)
    ir2 = remove_u(int2)
    ir3 = remove_u(int3)
    ir4 = remove_u(int4)
    ir5 = remove_u(int5)
    ir6 = remove_u(int6)
    ir7 = remove_u(int7)
    ir8 = remove_u(int8)
    ir9 = remove_u(int9)
    ir10 = remove_u(int10)
    ir11 = remove_u(int11)
    ir12 = remove_u(int12)
    ir13 = remove_u(int13)
    ir14 = remove_u(int14)
    ir15 = remove_u(int15)
    ir16 = remove_u(int16)
    ir17 = remove_u(int17)
    ir18 = remove_u(int18)
    ir19 = remove_u(int19)
    ir20 = remove_u(int20)
    ir21 = remove_u(int21)
    ir22 = remove_u(int22)
    

    a1 = list_to_dict(r1, "US_ACI_STUFF")
    a2 = list_to_dict(r2, "US_CLEARPASS_SERVER")
    a3 = list_to_dict(r3, "US_CONTROLLER_GUEST")
    a4 = list_to_dict(r4, "US_CONTROLLER_LOCAL")
    a5 = list_to_dict(r5, "US_CONTROLLER_MASTER")
    a6 = list_to_dict(r6, "US_CONTROLLER_RAP")
    a7 = list_to_dict(r7, "US_JUNOS_PULSE")
    a8 = list_to_dict(r8, "US_NON_NETWORK_STUFF")
    a9 = list_to_dict(r9, "US_PAN_DC_FW")
    a10 = list_to_dict(r10, "US_PAN_INTERNET_FW")
    a11 = list_to_dict(r11, "US_RIVERBED")
    a12 = list_to_dict(r12, "US_ROUTER")
    a13 = list_to_dict(r13, "US_ROUTER_MPLS")
    a14 = list_to_dict(r14, "US_ROUTER_SW_MODULE")
    a15 = list_to_dict(r15, "US_ROUTER_VPN")
    a16 = list_to_dict(r16, "US_SCS_STUFF")
    a17 = list_to_dict(r17, "US_SWITCH_ACCESS")
    a18 = list_to_dict(r18, "US_SWITCH_CORE")
    a19 = list_to_dict(r19, "US_SWITCH_DC")
    a20 = list_to_dict(r20, "US_SWITCH_DMZ")
    a21 = list_to_dict(r21, "US_SWITCH_IP_MGMT")
    a22 = list_to_dict(r22, "US_SWITCH_LAB")

    ia1 = list_to_dict(ir1, "INT_ACI_STUFF")
    ia2 = list_to_dict(ir2, "INT_CLEARPASS_SERVER")
    ia3 = list_to_dict(ir3, "INT_CONTROLLER_GUEST")
    ia4 = list_to_dict(ir4, "INT_CONTROLLER_LOCAL")
    ia5 = list_to_dict(ir5, "INT_CONTROLLER_MASTER")
    ia6 = list_to_dict(ir6, "INT_CONTROLLER_RAP")
    ia7 = list_to_dict(ir7, "INT_JUNOS_PULSE")
    ia8 = list_to_dict(ir8, "INT_NON_NETWORK_STUFF")
    ia9 = list_to_dict(ir9, "INT_PAN_DC_FW")
    ia10 = list_to_dict(ir10, "INT_PAN_INTERNET_FW")
    ia11 = list_to_dict(ir11, "INT_RIVERBED")
    ia12 = list_to_dict(ir12, "INT_ROUTER")
    ia13 = list_to_dict(ir13, "INT_ROUTER_MPLS")
    ia14 = list_to_dict(ir14, "INT_ROUTER_SW_MODULE")
    ia15 = list_to_dict(ir15, "INT_ROUTER_VPN")
    ia16 = list_to_dict(ir16, "INT_SCS_STUFF")
    ia17 = list_to_dict(ir17, "INT_SWITCH_ACCESS")
    ia18 = list_to_dict(ir18, "INT_SWITCH_CORE")
    ia19 = list_to_dict(ir19, "INT_SWITCH_DC")
    ia20 = list_to_dict(ir20, "INT_SWITCH_DMZ")
    ia21 = list_to_dict(ir21, "INT_SWITCH_IP_MGMT")
    ia22 = list_to_dict(ir22, "INT_SWITCH_LAB")


    c1 = combined_list_of_dicts(a1)
    c2 = combined_list_of_dicts(a2)
    c3 = combined_list_of_dicts(a3)
    c4 = combined_list_of_dicts(a4)
    c5 = combined_list_of_dicts(a5)
    c6 = combined_list_of_dicts(a6)
    c7 = combined_list_of_dicts(a7)
    c8 = combined_list_of_dicts(a8)
    c9 = combined_list_of_dicts(a9)
    c10 = combined_list_of_dicts(a10)
    c11 = combined_list_of_dicts(a11)
    c12 = combined_list_of_dicts(a12)
    c13 = combined_list_of_dicts(a13)
    c14 = combined_list_of_dicts(a14)
    c15 = combined_list_of_dicts(a15)
    c16 = combined_list_of_dicts(a16)
    c17 = combined_list_of_dicts(a17)
    c18 = combined_list_of_dicts(a18)
    c19 = combined_list_of_dicts(a19)
    c20 = combined_list_of_dicts(a20)
    c21 = combined_list_of_dicts(a21)
    c22 = combined_list_of_dicts(a22)
    ic1 = combined_list_of_dicts(ia1)
    ic2 = combined_list_of_dicts(ia2)
    ic3 = combined_list_of_dicts(ia3)
    ic4 = combined_list_of_dicts(ia4)
    ic5 = combined_list_of_dicts(ia5)
    ic6 = combined_list_of_dicts(ia6)
    ic7 = combined_list_of_dicts(ia7)
    ic8 = combined_list_of_dicts(ia8)
    ic9 = combined_list_of_dicts(ia9)
    ic10 = combined_list_of_dicts(ia10)
    ic11 = combined_list_of_dicts(ia11)
    ic12 = combined_list_of_dicts(ia12)
    ic13 = combined_list_of_dicts(ia13)
    ic14 = combined_list_of_dicts(ia14)
    ic15 = combined_list_of_dicts(ia15)
    ic16 = combined_list_of_dicts(ia16)
    ic17 = combined_list_of_dicts(ia17)
    ic18 = combined_list_of_dicts(ia18)
    ic19 = combined_list_of_dicts(ia19)
    ic20 = combined_list_of_dicts(ia20)
    ic21 = combined_list_of_dicts(ia21)
    ic22 = combined_list_of_dicts(ia22)
    #(ic22)
    keys = ic22[0].keys()
    with open('/network/scripts/inventory/Result/detailed_inventory.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(ic22)
    q1 = optimized_riverbed()
    opc1 = optimized_list_combined(lt)
    opc2 = optimized_list_combined(lt1)
    keys = opc2[0].keys()
    with open('/network/scripts/inventory/Result/detailed_inventory_rvbd.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(opc2)
    m1 = monitoring()
    with open('/network/scripts/inventory/Result/detailed_inventory_monitoring.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(m1)
    macht = machinetype()
    ss = serial()












