#!/remote/devinfra/tools/python/anaconda3/bin/python
from datetime import datetime,date,timedelta
import time
import pandas as pd
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
import csv
import xlsxwriter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os.path
import smtplib,string
import getpass
import sys
from collections import defaultdict

input_list1 = []
input_list2 = []

rightnow = time.time()
utc = datetime.fromtimestamp(rightnow)
tenminutes = timedelta(minutes=10)
timediff = utc - tenminutes
start_epoch = int(timediff.timestamp() * 1000)  # in miliseconds
end_epoch = int(utc.timestamp() * 1000)
# print(start_epoch, timediff)
print(utc)
print("---------------------elk_auth_failed_updated.py----------------------")

def dataload(start_epoch,end_epoch):

	ca_cert = "/remote/devinfra/automation/network/conf/snpsICA2.pem"
	es = Elasticsearch(
	      ['elasticinfosec09'],
	      http_auth=('elastalert_user', 'e!asta!ert_pa$$'),
	      use_ssl=True,
	      ca_certs=ca_cert
	)

	datalist=[]
	query =  {
			 "size":10000,
			  "query": {
			    "bool": {
			      "must": [
			        {
			          "query_string": {
			            # "query": "@timestamp:>="+str(start_epoch)+" AND @timestamp:<="+str(end_epoch)
						  "query": "(message:\"*Login failed for*\" OR message:\"*Login failed using*\"  AND @timestamp:>=" + str(start_epoch) + " AND @timestamp:<=" + str(end_epoch) + ")"
			          }
			        }
			      ]
			    }
			  }
			}

	#print(query)
	res = es.search(index="network-rsyslog*",scroll="10m", body=query, request_timeout=350)
	sid = res['_scroll_id']
	scroll_size = len(res['hits']['hits'])
	#print(res['hits']['hits'])
	# append header
	datalist.append(['@timestamp','message'])
	while (scroll_size > 0):
		for item in res["hits"]["hits"]:
		    data=[]
		    hit=item['_source']
		    hit['message']=hit['message'].strip()
		    try:
		        data.append(hit['@timestamp'])
		        data.append(hit['message'])
		        datalist.append(data)
		    except Exception as e:
		        print(e)
		res = es.scroll(scroll_id = sid, scroll= "2m")
		sid = res['_scroll_id']
		scroll_size = len(res["hits"]["hits"])
	# print(datalist)
	with open('/network/scripts/WFH/elk/elk_auth_failed_log.csv', 'w+') as f:
		writer = csv.writer(f)
		writer.writerows(datalist)

	data = pd.read_csv("/network/scripts/WFH/elk/elk_auth_failed_log.csv")
	for_count = 0
	using_count = 0
	for i in range(len(data)):
		msg_string = data.loc[i, "message"]
		if "Login failed using" in msg_string:
			split_arr = data.loc[i, "message"].split("[")
			a1 = split_arr[0].split()
			a2 = a1[-2]
			input_list1.append(a2)
		elif "Login failed for" in msg_string:
			split_arr = data.loc[i, "message"].split("[")
			a1 = split_arr[0].split()
			a2 = a1[-2]
			input_list2.append(a2)
		else:
			print("not found")
	using_my_dict = {item: input_list1.count(item) for item in input_list1}
	for_my_dict = {item: input_list2.count(item) for item in input_list2}
	result = {key: using_my_dict.get(key, 0) + for_my_dict.get(key, 0)
			  for key in set(using_my_dict) | set(for_my_dict)}
	print(using_my_dict)
	print(for_my_dict)
	print(result)
	print(sum(result.values()))
	total_count = sum(result.values())

	if total_count > 200:
		sender = 'preeraja@synopsys.com'
		receivers = ['network-core@synopsys.com']
		SUBJECT = "Too many authentication failures for Pulse Gateways"
		BODY = MIMEMultipart('alternative')
		BODY['Subject'] = SUBJECT
		BODY['From'] = sender
		BODY['To'] = ','.join(receivers)
		TEXT = """\
				<html>
				<body>
				<p>This is an automated email to alert on "Too many Login Authentication Failures", please do not REPLY to it.
				    <br>
				    <br>
				    You are receiving this alert because we see too many login auth failures in logs(ELK). This email will be generated when ELK receives more than 200 cumulative logs independent of any particular gateway within last 10 minutes.
				    <br>
				    <br>
					There are two types of Login Auth failures:-
					 <br>
					 <br>
					1) "Login failed for" counts =  """ + str(for_my_dict) + """ <br>
					2) "Login failed using" counts = """ + str(using_my_dict) + """ <br>
					3)  Sum Total =  """ + str(total_count) + """ <br>
				    <br><br><br>
				    Thanks,
				    <br>
				    Preethi

				        </p>
				      </body>
				    </html>
				    """
		html = MIMEText(TEXT, 'html')
		BODY.attach(html)

		try:
			smtpObj = smtplib.SMTP('mailhost')
			smtpObj.sendmail(sender, receivers, BODY.as_string())
			print("Successfully sent email")
			smtpObj.quit()

		except Exception as e:
			print("Error: unable to send email")
dataload(start_epoch,end_epoch)