#!/remote/devinfra/tools/python/anaconda3/bin/python
import datetime, time
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
import operator
now = datetime.datetime.now()
now_utc = datetime.datetime.utcnow()
print(str(now) + "elk_bg.py")
def convert(seconds):
	seconds = seconds % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60

	return "%d:%02d:%02d" % (hour, minutes, seconds)

end_epoch = time.mktime(datetime.datetime.now().timetuple()) * 1000
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
start_epoch = time.mktime(yesterday.timetuple()) * 1000
# print(start_epoch, yesterday)
# print(end_epoch, datetime.datetime.now())

def dataload(start_epoch,end_epoch,v):

	ca_cert = "/remote/devinfra/automation/network/conf/snpsICA2.pem"
	es = Elasticsearch(
	      ['elasticinfosec09'],
	      http_auth=('elastalert_user', 'e!asta!ert_pa$$'),
	      use_ssl=True,
	      ca_certs=ca_cert
	)

	datalist=[]
	query =  {
			 "size":500,
			  "query": {
			    "bool": {
			      "must": [
			        {
			          "query_string": {
			            "query": "message:\"*Closed connection\" AND @timestamp:>="+str(start_epoch)+" AND @timestamp:<="+str(end_epoch)+" AND relayhost:(\""+v+"\")"
			          }
			        }
			      ]
			    }
			  }
			}

	#print(query)
	res = es.search(index="network-rsyslog*",scroll="5m", body=query, request_timeout=350)
	sid = res['_scroll_id']
	scroll_size = len(res['hits']['hits'])
	# print(scroll_size)
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
	#print(datalist)
	es.clear_scroll(body={'scroll_id': [sid]}, ignore=(404, ))
	with open('/network/scripts/WFH/elk/nw_log.csv', 'w+') as f:
	    writer = csv.writer(f)
	    writer.writerows(datalist)

def data_bg(usermap,BU,bulist):
	vpns = pd.read_csv("/network/scripts/WFH/elk/vpn.csv")
	vpn_list = vpns['vpn'].values.tolist()
	vpn_users = {}
	list1 = []
	with open(usermap, "r") as inFile:
		data1 = inFile.read()
	for v in vpn_list:
		dataload(start_epoch, end_epoch, v)
		data = pd.read_csv("/network/scripts/WFH/elk/nw_log.csv")
		print(data)
		# aggregate users
		users = {}
		for i in range(len(data)):
			# user manipulation
			split_arr = data.loc[i, "message"].split("(")
			# a1 = split_arr[0].split("]")
			user = split_arr[0].split("]")[-1].strip().lower()
			if '@' in user:
				user = user.split('@')[0].lower()
			if 'default network::' in user:
				user = user.split('default network::')[-1].lower()
			# closed_time manipulation
			split_arr1 = data.loc[i, "message"].split("after")
			closed_time = split_arr1[-1].split("seconds")[0].strip()
			if ((user != 'message') & (user in data1)):
				alternate = {user: closed_time}
				list1.append(alternate)
	dd = defaultdict(list)
	for inner_dict in list1:
		for k, v in inner_dict.items():
			dd[k].append(int(v))
	out_dict = {k: sum(v) for k, v in dd.items()}
	dict_list = []
	for i, j in out_dict.items():
		dict_list.append(({'User': i, 'WorkingHours': convert(j), '@timestamp': now_utc, 'BU': BU, 'type': 'elk'}))
	# print(dict_list)
	keys1 = dict_list[0].keys()
	with open(bulist, 'w+') as output_file1:
		dict_writer = csv.DictWriter(output_file1, keys1)
		dict_writer.writeheader()
		dict_writer.writerows(dict_list)
data_bg('/network/scripts/WFH/elk/user_sg_mapping.csv','SG','/network/scripts/WFH/elk/Output/sg_list.csv')
data_bg('/network/scripts/WFH/elk/user_it_mapping.csv','IT','/network/scripts/WFH/elk/Output/it_list.csv')
data_bg('/network/scripts/WFH/elk/user_bot_mapping.csv','BOT','/network/scripts/WFH/elk/Output/bot_list.csv')
data_bg('/network/scripts/WFH/elk/user_cto_mapping.csv','CTO','/network/scripts/WFH/elk/Output/cto_list.csv')
data_bg('/network/scripts/WFH/elk/user_dg_mapping.csv','DG','/network/scripts/WFH/elk/Output/dg_list.csv')
data_bg('/network/scripts/WFH/elk/user_dtg_mapping.csv','DTG','/network/scripts/WFH/elk/Output/dtg_list.csv')
data_bg('/network/scripts/WFH/elk/user_dvt_mapping.csv','DVT','/network/scripts/WFH/elk/Output/dvt_list.csv')
data_bg('/network/scripts/WFH/elk/user_fin_mapping.csv','FIN','/network/scripts/WFH/elk/Output/fin_list.csv')
data_bg('/network/scripts/WFH/elk/user_foi_mapping.csv','FOI','/network/scripts/WFH/elk/Output/foi_list.csv')
data_bg('/network/scripts/WFH/elk/user_gts_mapping.csv','GTS','/network/scripts/WFH/elk/Output/gts_list.csv')
data_bg('/network/scripts/WFH/elk/user_hrfa_mapping.csv','HRFA','/network/scripts/WFH/elk/Output/hrfa_list.csv')
data_bg('/network/scripts/WFH/elk/user_lmg_mapping.csv','LMG','/network/scripts/WFH/elk/Output/lmg_list.csv')
data_bg('/network/scripts/WFH/elk/user_nv_mapping.csv','NV','/network/scripts/WFH/elk/Output/nv_list.csv')
data_bg('/network/scripts/WFH/elk/user_oop_mapping.csv','OOP','/network/scripts/WFH/elk/Output/oop_list.csv')
data_bg('/network/scripts/WFH/elk/user_scmg_mapping.csv','SCMG','/network/scripts/WFH/elk/Output/scmg_list.csv')
data_bg('/network/scripts/WFH/elk/user_seg_mapping.csv','SEG','/network/scripts/WFH/elk/Output/seg_list.csv')
data_bg('/network/scripts/WFH/elk/user_sig_mapping.csv','SIG','/network/scripts/WFH/elk/Output/sig_list.csv')
data_bg('/network/scripts/WFH/elk/user_sg_mapping.csv','SG','/network/scripts/WFH/elk/Output/sg_list.csv')
data_bg('/network/scripts/WFH/elk/user_snps_mapping.csv','SNPS','/network/scripts/WFH/elk/Output/snps_list.csv')
data_bg('/network/scripts/WFH/elk/user_vg_mapping.csv','VG','/network/scripts/WFH/elk/Output/vg_list.csv')
data_bg('/network/scripts/WFH/elk/user_wwas_mapping.csv','WWAS','/network/scripts/WFH/elk/Output/wwas_list.csv')
