#!/opt/python-2.7.13/bin/python
import requests
import os, sys
import json, ast
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
print(str(now)+" av_all.py")

HQ = [
'us02',
'ussv',
'sv1',
'sv2',
'sv8',
'usmva',
'usmvb',
'bldga',
'sv3'
]
APAC = [
'cn60',
'kr01',
'kp01',
'cn30',
'cn32',
'cn34',
'cn42',
'cn59',
'cn58',
'hk02',
'jp01',
'jp02',
'mo90',
'my01',
'my99',
'sg01',
'sg99',
'tw01',
'tw04',
'tw12',
'tw50',
'tw52',
'tw55',
'vn01',
'kr02',
'cn08',
'nl03',
'kr05',
'cn29',
'tw14'
]
EMEA = [
'gb07',
'am04',
'be06',
'ch10',
'ch99',
'cn63',
'de02',
'de04',
'de06',
'de11',
'de99',
'dk01',
'fi01',
'fi02',
'fi03',
'fi99',
'fr01',
'fr02',
'fr03',
'fr05',
'fr10',
'fr42',
'fr62',
'fr65',
'fr98',
'gb01',
'gb04',
'gb11',
'gb12',
'gb14',
'gb50',
'gb99',
'hu01',
'ie02',
'ie99',
'il01',
'il99',
'it01',
'nl20',
'nl98',
'pl01',
'pt01',
'pt02',
'ru02',
'ru20',
'se01',
'se80',
'gb15',
'gb72'
]
INDIA = [
'in01',
'in02',
'in08',
'in09',
'in10',
'in17',
'in18',
'in19',
'in23',
'in24',
'in25',
'in31',
'in32',
'in45',
'in74',
'in7b',
'in7c',
'in98',
'lk01',
'in33',
'in46',
'in47',
'in7d',
'in37',
'lk02']
NA = [
'us6u',
'ca06',
'ca09',
'ca11',
'ca14',
'ca42',
'cl01',
'us03',
'us04',
'us05',
'us08',
'us11',
'us16',
'us18',
'us20',
'us26',
'us27',
'us28',
'us36',
'us38',
'us47',
'us54',
'us59',
'us6a',
'us6d',
'us6j',
'us6l',
'us6m',
'us6o',
'us6p',
'us6r',
'us6s',
'us77',
'us7m',
'us8e',
'us8k',
'us8m',
'us8w',
'us95',
'usmv',
'ca16',
'ca17',
'ca18',
'us1a',
'us7n',
'us1d',
'us2d',
'us2a',
'us1a']
class Pinger(object):
    status = {''
              'online': [], 'offline': []} # Populated while we are running
    hosts = [] # List of all hosts/ips in our input queue

    # How many ping process at the time.
    thread_count = 4

    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()

    def ping(self, ip):
        # Use the system ping command with count of 1 and wait time of 1.
        ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))

        return ret == 0 # Return True if our ping command succeeds

    def pop_queue(self):
        ip = None

        self.lock.acquire() # Grab or wait+grab the lock.

        if self.hosts:
            ip = self.hosts.pop()

        self.lock.release() # Release the lock, so another thread could grab it.

        return ip

    def dequeue(self):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            result = 'online' if self.ping(ip) else 'offline'
            self.status[result].append(ip)

    def start(self):
        threads = []

        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        [ t.join() for t in threads ]


        return self.status
def main_func():
    final_lst = []
    list1 = []
    alive_result = []
    dead_result = []
    alive_res1 = []
    dead_res1 = []
    lt1 = []
    lt2 = []
    with open("/network/scripts/av_monitoring/Input/cname_orig.txt", "r") as inFile:
        # read() the entire file as a string
        data1 = inFile.read()
        # converts the string of lists to list
        data = ast.literal_eval(data1)
        for x in data['result']:
            if '-hdvc.internal.synopsys.com' in x['name']:
                list1.append((x['name']))
            elif '-sch.internal.synopsys.com' in x['name']:
                list1.append((x['name']))
            elif '-am.internal.synopsys.com' in x['name']:
                list1.append((x['name']))
            elif '-ds.internal.synopsys.com' in x['name']:
                list1.append((x['name']))
            elif '-wb.internal.synopsys.com' in x['name']:
                list1.append((x['name']))
            elif '-tp.internal.synopsys.com' in x['name']:
                list1.append((x['name']))
            elif '-ts.internal.synopsys.com' in x['name']:
                list1.append((x['name']))
    #(list1)
    ping = Pinger()
    ping.thread_count = 4
    ping.hosts = list1
    ping.start()
    OutPut = ast.literal_eval(json.dumps(Pinger.status))
    alive = dict(OutPut.items()[len(OutPut) / 2:])
    dead = dict(OutPut.items()[:len(OutPut) / 2])
    alive_values = alive.values()
    dead_values = dead.values()

    for x in alive_values:
        for y in x:
            alive_result.append(y)
    for x in dead_values:
        for y in x:
            dead_result.append(y)
    # (alive_result)
    for el in alive_result:
        sub = el.split(', ')
        alive_res1.append(sub)
    for el in dead_result:
        sub = el.split(', ')
        dead_res1.append(sub)
    merged = list(itertools.chain.from_iterable(alive_res1))
    for x in merged:
        x.split('-')
        if x.split('-')[0].strip() in APAC:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "polycom_online", 'Region': 'APAC', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "am_online", 'Region': 'APAC', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "sch_online", 'Region': 'APAC', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ds_online", 'Region': 'APAC', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "wb_online", 'Region': 'APAC', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "tp_online", 'Region': 'APAC', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ts_online", 'Region': 'APAC', 'category': 'av_all'}
                lt1.append(alternate)

        elif x.split('-')[0].strip() in EMEA:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "polycom_online", 'Region': 'EMEA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "am_online", 'Region': 'EMEA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "sch_online", 'Region': 'EMEA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ds_online", 'Region': 'EMEA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "wb_online", 'Region': 'EMEA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "tp_online", 'Region': 'EMEA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ts_online", 'Region': 'EMEA', 'category': 'av_all'}
                lt1.append(alternate)

        elif x.split('-')[0].strip() in INDIA:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "polycom_online", 'Region': 'INDIA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "am_online", 'Region': 'INDIA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "sch_online", 'Region': 'INDIA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ds_online", 'Region': 'INDIA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "wb_online", 'Region': 'INDIA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "tp_online", 'Region': 'INDIA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ts_online", 'Region': 'INDIA', 'category': 'av_all'}
                lt1.append(alternate)

        elif x.split('-')[0].strip() in NA:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "polycom_online", 'Region': 'NA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "am_online", 'Region': 'NA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "sch_online", 'Region': 'NA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ds_online", 'Region': 'NA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "wb_online", 'Region': 'NA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "tp_online", 'Region': 'NA', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ts_online", 'Region': 'NA', 'category': 'av_all'}
                lt1.append(alternate)
        elif x.split('-')[0].strip() in HQ:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "polycom_online", 'Region': 'HQ', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "am_online", 'Region': 'HQ', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "sch_online", 'Region': 'HQ', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ds_online", 'Region': 'HQ', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "wb_online", 'Region': 'HQ', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "tp_online", 'Region': 'HQ', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ts_online", 'Region': 'HQ', 'category': 'av_all'}
                lt1.append(alternate)
        else:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "polycom_online", 'Region': 'UNKN', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "am_online", 'Region': 'UNKN', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "sch_online", 'Region': 'UNKN', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ds_online", 'Region': 'UNKN', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "wb_online", 'Region': 'UNKN', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "tp_online", 'Region': 'UNKN', 'category': 'av_all'}
                lt1.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "ts_online", 'Region': 'UNKN', 'category': 'av_all'}
                lt1.append(alternate)
    merged1 = list(itertools.chain.from_iterable(dead_res1))
    for x in merged1:
        x.split('-')
        if x.split('-')[0].strip() in APAC:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "polycom_offline", 'Region': 'APAC', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "am_offline", 'Region': 'APAC', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "sch_offline", 'Region': 'APAC', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ds_offline", 'Region': 'APAC', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "wb_offline", 'Region': 'APAC', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "tp_offline", 'Region': 'APAC', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ts_offline", 'Region': 'APAC', 'category': 'av_all'}
                lt2.append(alternate)

        elif x.split('-')[0].strip() in EMEA:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "polycom_offline", 'Region': 'EMEA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "am_offline", 'Region': 'EMEA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "sch_offline", 'Region': 'EMEA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ds_offline", 'Region': 'EMEA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "wb_offline", 'Region': 'EMEA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "tp_offline", 'Region': 'EMEA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ts_offline", 'Region': 'EMEA', 'category': 'av_all'}
                lt2.append(alternate)

        elif x.split('-')[0].strip() in INDIA:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "polycom_offline", 'Region': 'INDIA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "am_offline", 'Region': 'INDIA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "sch_offline", 'Region': 'INDIA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ds_offline", 'Region': 'INDIA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "wb_offline", 'Region': 'INDIA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "tp_offline", 'Region': 'INDIA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ts_offline", 'Region': 'INDIA', 'category': 'av_all'}
                lt2.append(alternate)

        elif x.split('-')[0].strip() in NA:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "polycom_offline", 'Region': 'NA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "am_offline", 'Region': 'NA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "sch_offline", 'Region': 'NA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ds_offline", 'Region': 'NA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "wb_offline", 'Region': 'NA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "tp_offline", 'Region': 'NA', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ts_offline", 'Region': 'NA', 'category': 'av_all'}
                lt2.append(alternate)
        elif x.split('-')[0].strip() in HQ:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "polycom_offline", 'Region': 'HQ', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "am_offline", 'Region': 'HQ', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "sch_offline", 'Region': 'HQ', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ds_offline", 'Region': 'HQ', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "wb_offline", 'Region': 'HQ', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "tp_offline", 'Region': 'HQ', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ts_offline", 'Region': 'HQ', 'category': 'av_all'}
                lt2.append(alternate)
        else:
            if '-hdvc.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "polycom_offline", 'Region': 'UNKN', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-am.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "am_offline", 'Region': 'UNKN', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-sch.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "sch_offline", 'Region': 'UNKN', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ds.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ds_offline", 'Region': 'UNKN', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-wb.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "wb_offline", 'Region': 'UNKN', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-tp.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "tp_offline", 'Region': 'UNKN', 'category': 'av_all'}
                lt2.append(alternate)
            elif '-ts.internal.synopsys.com' in x:
                alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "ts_offline", 'Region': 'UNKN', 'category': 'av_all'}
                lt2.append(alternate)
    final_lst.extend(lt1)
    final_lst.extend(lt2)
    keys = final_lst[0].keys()
    with open('/network/scripts/av_monitoring/Output/av-list.csv', 'w+') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final_lst)
if __name__ == "__main__":
    main_func()





