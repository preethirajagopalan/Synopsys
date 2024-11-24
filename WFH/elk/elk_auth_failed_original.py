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

rightnow = time.time()
utc = datetime.fromtimestamp(rightnow)
tenminutes = timedelta(minutes=10)
timediff = utc - tenminutes

# print(yesterday,now)
# current_time = datetime.datetime.utcnow()  # use datetime.datetime.utcnow() for UTC time
# ten_minutes_ago = current_time - datetime.timedelta(minutes=10)
#
start_epoch = int(timediff.timestamp() * 1000)  # in miliseconds
end_epoch = int(utc.timestamp() * 1000)
print(start_epoch, timediff)
print(end_epoch, utc)
# print(ten_minutes_ago_epoch_ts,end_epoch)
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

	print(query)
	res = es.search(index="network-rsyslog*",scroll="10m", body=query, request_timeout=350)
	sid = res['_scroll_id']
	scroll_size = len(res['hits']['hits'])
	print(res['hits']['hits'])
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
		if "Login failed for" in msg_string:
			for_count += 1
		elif "Login failed using" in msg_string:
			using_count += 1
	total_count = for_count + using_count
	print(for_count, using_count, total_count)
	alternate = {"total":total_count,"Login_failed_for_count":for_count, "Login_failed_using_count":using_count}

	if total_count > 40:
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
				<p>This is an automated email to alert on "Too many Login Authetntication Failures", please do not REPLY to it. 
				    <br>
				    <br>
				    You are receving this alert because we see too many login auth failures in logs(ELK). This email will be generated when ELK receives more than 40 cumulative logs independent of any particular gateway within last 10 minutes.
				    <br>
				    <br>
					There are two types of Login Auth failures:-
					 <br>
					 <br>
					1) "Login failed for" counts =  """ + str(alternate['Login_failed_for_count']) + """ <br>
					2) "Login failed using" counts = """ + str(alternate['Login_failed_using_count']) + """ <br>
					3)  Sum Total =  """ + str(alternate['total']) + """ <br>
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


		# SERVER = "localhost"
		#
		# FROM = "preeraja@synopsys.com"
		# TO = ['preeraja@synopsys.com', 'michaeli@synopsys.com'] # must be a list
		#
		# SUBJECT = "Cumulative failed login counts"
		#
		# TEXT = alternate
		#
		# # Prepare actual message
		#
		# message = """\
		# From: %s
		# To: %s
		# Subject: %s
		#
		# %s
		# """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
		#
		# # Send the mail
		#
		# server = smtplib.SMTP(SERVER)
		# server.sendmail(FROM, TO, message)
		# server.quit()
	else:
		# sender = 'preeraja@synopsys.com'
		# receivers = ['preeraja@synopsys.com']
		# SUBJECT = "Too many authentication failures for Pulse Gateways"
		# BODY = MIMEMultipart('alternative')
		# BODY['Subject'] = SUBJECT
		# BODY['From'] = sender
		# BODY['To'] = ','.join(receivers)
		# TEXT = """\
		# <html>
		# <body>
		# <p>This is an automated email to alert on "Too many Login Authetntication Failures", please do not REPLY to it.
		#     <br>
		#     <br>
		#     You are receving this alert because we see too many login auth failures in logs(ELK). This email will be generated when ELK receives more than 40 cumulative logs independent of any particular gateway within last 10 minutes.
		#     <br>
		#     <br>
		# 	There are two types of Login Auth failures:-
		# 	 <br>
		# 	 <br>
		# 	1) "Login failed for" counts =  """ + str(alternate['Login_failed_for_count']) + """ <br>
		# 	2) "Login failed using" counts = """ + str(alternate['Login_failed_using_count']) + """ <br>
		# 	3)  Sum Total =  """ + str(alternate['total']) + """ <br>
		#     <br><br><br>
		#     Thanks,
		#     <br>
		#     Preethi
		#
		#         </p>
		#       </body>
		#     </html>
		#     """
		# html = MIMEText(TEXT, 'html')
		# BODY.attach(html)
		#
		# try:
		# 	smtpObj = smtplib.SMTP('mailhost')
		# 	smtpObj.sendmail(sender, receivers, BODY.as_string())
		# 	print("Successfully sent email")
		# 	smtpObj.quit()
		#
		# except Exception as e:
		# 	print("Error: unable to send email")
		print("Email will not be sent as sum total count is less than 40")
dataload(start_epoch,end_epoch)