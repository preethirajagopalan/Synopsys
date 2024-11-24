#!/opt/python-2.7.13/bin/python
#comment
import requests
import os, sys
import json
import ast
import subprocess
import threading
from datetime import date
from datetime import datetime
import datetime
import ast
from dateutil.tz import tzutc
import csv
import itertools
now = datetime.datetime.utcnow()
print(str(now)+" av-crk.py")
list1 = []
APAC = [
'KR01',
'KP01',
'CN30',
'CN32',
'CN34',
'CN42',
'CN59',
'CN58',
'HK02',
'JP01',
'JP02',
'MO90',
'MY01',
'MY99',
'SG01',
'SG99',
'TW01',
'TW04',
'TW12',
'TW50',
'TW52',
'TW55',
'VN01',
'KR02',
'CN08',
'NL03',
'KR05',
'CN29',
'TW14'
]
EMEA = [
'AM04',
'BE06',
'CH10',
'CH99',
'CN63',
'DE02',
'DE04',
'DE06',
'DE11',
'DE99',
'DK01',
'FI01',
'FI02',
'FI03',
'FI99',
'FR01',
'FR02',
'FR03',
'FR05',
'FR10',
'FR42',
'FR62',
'FR65',
'FR98',
'GB01',
'GB04',
'GB11',
'GB12',
'GB14',
'GB50',
'GB99',
'HU01',
'IE02',
'IE99',
'IL01',
'IL99',
'IT01',
'NL20',
'NL98',
'PL01',
'PT01',
'PT02',
'RU02',
'RU20',
'SE01',
'SE80',
'GB15',
'GB72'
]
INDIA = [
'IN01',
'IN02',
'IN08',
'IN09',
'IN10',
'IN17',
'IN18',
'IN19',
'IN23',
'IN24',
'IN25',
'IN31',
'IN32',
'IN45',
'IN74',
'IN7B',
'IN7C',
'IN98',
'LK01',
'IN33',
'IN46',
'IN47',
'IN7D',
'IN37',
'LK02']
NA = ['CA06',
'CA09',
'CA11',
'CA14',
'CA42',
'CL01',
'US03',
'US04',
'US05',
'US08',
'US11',
'US16',
'US18',
'US20',
'US26',
'US27',
'US28',
'US36',
'US38',
'US47',
'US54',
'US59',
'US6A',
'US6D',
'US6J',
'US6L',
'US6M',
'US6O',
'US6P',
'US6R',
'US6S',
'US77',
'US7M',
'US8E',
'US8K',
'US8M',
'US8W',
'US95',
'USMV',
'CA16',
'CA17',
'CA18',
'US1A',
'US7N',
'US1D',
'US2D',
'US2A',
'US1A']
HQ = [
'US02',
'USSV',
'SV1',
'SV2',
'SV8',
'USMVA',
'USMVB',
'BLDGA',
'SV3'
]
data = []

def begin():
    with open("/network/scripts/av_monitoring/Input/crk_output2.txt", "r") as inFile:
        #read() the entire file as a string
        data1 = inFile.read()
        #converts the string of lists to list
        data3 = ast.literal_eval(data1)
    # for x in data:
    #     x['errorCodes'] = str(x['errorCodes'])[1:-1]
    #     if x['errorCodes'] == 'ultrasoundconfigsettings':
    #         print('original', x['displayName'], x['connectionStatus'])
    #         x['connectionStatus'] = 'connected'
    #         print('altered', x['displayName'], x['connectionStatus'])
    for x in data3:
        x['errorCodes'] = (str(x['errorCodes'])[1:-1])
        if x['errorCodes'] == "'ultrasoundconfigsettings'":
            x['connectionStatus'] = 'connected'
            data.append(x)
        else:
            data.append(x)
        # print(x['errorCodes'],x['connectionStatus'])


    for x in data:
        res = str(x['errorCodes'])[1:-1]
        if x['displayName'].split('-')[0].split()[0] in APAC:
            if x['connectionStatus'] == 'connected_with_issues':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].split()[0],
                             'ip': x['ip'],
                             '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit', 'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'APAC'}
                list1.append(alternate)
            if x['connectionStatus'] == 'disconnected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'APAC'}
                list1.append(alternate)
            if x['connectionStatus'] == 'connected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 1, 'Region':'APAC'}
                list1.append(alternate)
        elif x['displayName'].split('-')[0].split()[0] in EMEA:
            if x['connectionStatus'] == 'connected_with_issues':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].split()[0],
                             'ip': x['ip'],
                             '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit', 'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'EMEA'}
                list1.append(alternate)
            if x['connectionStatus'] == 'disconnected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'EMEA'}
                list1.append(alternate)
            if x['connectionStatus'] == 'connected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 1, 'Region':'EMEA'}
                list1.append(alternate)
        elif x['displayName'].split('-')[0].split()[0] in INDIA:
            if x['connectionStatus'] == 'connected_with_issues':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].split()[0],
                             'ip': x['ip'],
                             '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit', 'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'INDIA'}
                list1.append(alternate)
            if x['connectionStatus'] == 'disconnected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'INDIA'}
                list1.append(alternate)
            if x['connectionStatus'] == 'connected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 1, 'Region':'INDIA'}
                list1.append(alternate)
        elif x['displayName'].split('-')[0].split()[0] in NA:
            if x['connectionStatus'] == 'connected_with_issues':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].split()[0],
                             'ip': x['ip'],
                             '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit', 'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region': 'NA'}
                list1.append(alternate)
            if x['connectionStatus'] == 'disconnected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'NA'}
                list1.append(alternate)
            if x['connectionStatus'] == 'connected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 1, 'Region':'NA'}
                list1.append(alternate)
        elif x['displayName'].split('-')[0].split()[0] in HQ:
            if x['connectionStatus'] == 'connected_with_issues':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].split()[0],
                             'ip': x['ip'],
                             '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit', 'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region': 'HQ'}
                list1.append(alternate)
            if x['connectionStatus'] == 'disconnected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region':'HQ'}
                list1.append(alternate)
            if x['connectionStatus'] == 'connected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                             'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                             'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 1, 'Region':'HQ'}
                list1.append(alternate)
        else:
            if x['connectionStatus'] == 'connected_with_issues':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].split()[0],
                             'ip': x['ip'],
                             '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit', 'serial': x['serial'],
                             'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                             'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region': 'UNKN'}
                list1.append(alternate)
            if x['connectionStatus'] == 'disconnected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                         'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                         'serial': x['serial'],
                         'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                         'connectionStatus': x['connectionStatus'], 'tag': 0, 'Region': 'UNKN'}
                list1.append(alternate)
            if x['connectionStatus'] == 'connected':
                alternate = {'Name': x['displayName'], 'SiteCode': x['displayName'].split('-')[0].strip().split()[0],
                         'ip': x['ip'], '@timestamp': now, 'mac': x['mac'], 'type': 'roomkit',
                         'serial': x['serial'],
                         'software': x['software'], 'upgradeChannel': x['upgradeChannel'], 'errorCodes': res,
                         'connectionStatus': x['connectionStatus'], 'tag': 1, 'Region': 'UNKN'}
                list1.append(alternate)
    # print(list1)
    return list1


def csvfile1():
    keys1 = list1[0].keys()
    with open('/network/scripts/av_monitoring/Output/roomkit.csv', 'wb') as output_file1:
        dict_writer = csv.DictWriter(output_file1, keys1)
        dict_writer.writeheader()
        dict_writer.writerows(list1)





if __name__ == "__main__":
    begin()
    csvfile1()








