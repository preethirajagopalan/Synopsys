#!/opt/python-2.7.13/bin/python
import requests
import os, sys, socket
import json, ast
import subprocess
import threading
from elasticsearch import Elasticsearch
from elasticsearch import helpers, Elasticsearch
from elasticsearch.helpers import bulk
from datetime import date
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os.path
import smtplib, string
import datetime
import ast
from dateutil.tz import tzutc
import csv
import itertools

now = datetime.datetime.utcnow()


# print(str(now)+" gsoc_ping.py")


class Pinger(object):
    status = {''
              'online': [], 'offline': []}  # Populated while we are running
    hosts = []  # List of all hosts/ips in our input queue

    # How many ping process at the time.
    thread_count = 4

    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()

    def ping(self, ip):
        # Use the system ping command with count of 1 and wait time of 1.
        ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))

        return ret == 0  # Return True if our ping command succeeds

    def pop_queue(self):
        ip = None

        self.lock.acquire()  # Grab or wait+grab the lock.

        if self.hosts:
            ip = self.hosts.pop()

        self.lock.release()  # Release the lock, so another thread could grab it.

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
        [t.join() for t in threads]

        return self.status


def main_func():
    my_file = open("/network/scripts/690/input.txt", "r")
    list = my_file.readlines()
    list1 = []
    list2 = []
    socketlist_offline = []
    socketlist_online = []
    socketlist_offline_email = []

    for element in list:
        list1.append(element.strip())
    # print(list1)

    ping = Pinger()
    ping.thread_count = 4
    ping.hosts = list1
    ping.start()
    OutPut = ast.literal_eval(json.dumps(Pinger.status))
    print("----------------------------------------------------------------------------ONLINE-------------------------------------------------------------------------------------------------------------------")
    print(OutPut['online'])
    print("----------------------------------------------------------------------------OFFLINE-------------------------------------------------------------------------------------------------------------------")
    print(OutPut['offline'])

    for x in OutPut['offline']:
        socketlist_offline_email.append({x: socket.getnameinfo((x, 0), 0)[0]})

    for x in OutPut['offline']:
        socketlist_offline.append(
            {'ip': x, 'name': socket.getnameinfo((x, 0), 0)[0], 'Status': 'offline', '@timestamp': now, 'tag': 0})
    for x in OutPut['online']:
        socketlist_online.append(
            {'ip': x, 'name': socket.getnameinfo((x, 0), 0)[0], 'Status': 'online', '@timestamp': now, 'tag': 1})
    list2.extend(socketlist_offline)
    list2.extend(socketlist_online)

    items = ["\n    <li>{}</li>".format(s) for s in socketlist_offline_email]
    items = "".join(items)

    keys1 = list2[0].keys()
    with open('/network/scripts/690/output.txt', 'wb') as output_file1:
        dict_writer = csv.DictWriter(output_file1, keys1)
        dict_writer.writeheader()
        dict_writer.writerows(list2)


    if OutPut['offline']:
        sender = 'preeraja@synopsys.com'
        receivers = ['preeraja@synopsys.com', 'bent@synopsys.com']
        SUBJECT = "Ping failed for following 690 devices"
        BODY = MIMEMultipart('alternative')
        BODY['Subject'] = SUBJECT
        BODY['From'] = sender
        BODY['To'] = ','.join(receivers)
        TEXT = """\
    			<html>
    			<body>
    			<p>This is an automated email for ICMP/Ping failed 690 devices
    			    <br>
    			    <br>
    			    You are receiving this email alert as my_ping.py script has been executed
    			    <br>
    				<br>
    				Offline Devices are:-  {0}   <br>
    			    <br><br><br>
    			    Thanks,
    			    <br>
    			    Preethi

    			        </p>
    			      </body>
    			    </html>
    			    """.format(items)
        html = MIMEText(TEXT, 'html')
        BODY.attach(html)

        try:
            smtpObj = smtplib.SMTP('mailhost')
            smtpObj.sendmail(sender, receivers, BODY.as_string())
            print(str(now) + " Successfully sent email")
            smtpObj.quit()

        except Exception as e:
            print(str(now) + " Error: unable to send email")


if __name__ == "__main__":
    main_func()







