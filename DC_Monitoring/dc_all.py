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
now_str = now.strftime("%Y.%m.%d")
print(str(now)+ " dc_all.py")


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
    with open("/network/scripts/DC_Monitoring/Input/cname_orig1.txt", "r") as inFile:
        # read() the entire file as a string
        data1 = inFile.read()
        # converts the string of lists to list
        data = ast.literal_eval(data1)
        for x in data['result']:
            if '-leaf' in x['name']:
                list1.append((x['name']))
            elif '-spine' in x['name']:
                list1.append((x['name']))
    #print(list1)

    ping = Pinger()
    ping.thread_count = 4
    ping.hosts = list1
    ping.start()
    OutPut = ast.literal_eval(json.dumps(Pinger.status))

    alive_result = OutPut["online"]
    dead_result  = OutPut["offline"]
    for el in alive_result:
        sub = el.split(', ')
        alive_res1.append(sub)
    for el in dead_result:
        sub = el.split(', ')
        dead_res1.append(sub)
    merged = list(itertools.chain.from_iterable(alive_res1))
    for x in merged:
        if '-leaf' in x:
            alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "leaf", 'category': 'apic', 'status':'online'}
            lt1.append(alternate)
        elif '-spine' in x:
            alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 1,
                             'type': "spine", 'category': 'apic','status':'online'}
            lt1.append(alternate)
    merged1 = list(itertools.chain.from_iterable(dead_res1))
    for x in merged1:
        if '-leaf' in x:
            alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "leaf", 'category': 'apic', 'status':'offline'}
            lt1.append(alternate)
        elif '-spine' in x:
            alternate = {'Name': x, 'SiteCode': x.split('-')[0].strip().upper(), '@timestamp': now, 'tag': 0,
                             'type': "spine", 'category': 'apic','status':'offline'}
            lt1.append(alternate)

    final_lst.extend(lt1)
    final_lst.extend(lt2)
    keys = final_lst[0].keys()
    with open('/network/scripts/DC_Monitoring/Output/dc_list.csv', 'w+') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final_lst)
if __name__ == "__main__":
    main_func()





