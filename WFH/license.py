#!/opt/python-2.7.13/bin/python -u 
import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date
from datetime import datetime
import datetime
from dateutil.tz import tzutc
import ast
import csv
now = datetime.datetime.utcnow()
lst = []
lst1 = []
r = requests.get('https://10.205.3.31/api/v1/license/license-server-lease-information', auth=('uKGsmQDFrEsKbvCk6fQOA6QE38j7ZSbwOKciarmZ1IU=',''), verify=False)
print("-------------------------------license.py-----------------------------------------------------------")
initial_response = r.json()
final1 = ast.literal_eval(json.dumps(initial_response['leased-license-counts']['features']['feature']))
#print(initial_response['leased-license-counts']['features']['feature'])
for item in final1:
    if (item['name']) == 'Concurrent Users':
        # print(item['total-count'])
        # print(item['name'])
        # print(item['clients']['client-info'])
        for x in (item['clients']['client-info']):
            alternate = {'Name': (x['name']),'type': ((item['name'])),'@timestamp': now, 'total':(item['total-count']),
                     'license_leased': x['leased-count']}
            lst.append(alternate)
        alternate1 = {'@timestamp': now, 'total': (item['total-count']), 'type':'total-count'}
        lst1.append(alternate1)
    if item['total-count'] > 11500:
        #print(item['total-count'])
        sender = 'netops@synopsys.com'
        receivers = ['network-core@synopsys.com']
        SUBJECT = "Total Pulse Licenses Leased out of new license server is greater than 11500"
        BODY = MIMEMultipart('alternative')
        BODY['Subject'] = SUBJECT
        BODY['From'] = sender
        BODY['To'] = ','.join(receivers)
        TEXT = """\
             <html>
             <body>
             <p>This is an automated email to alert on " Total Pulse Licenses Leased out of new License server is greater than 11500", please do not REPLY to it.
                 <br>
                 <br>
                 You are receiving this alert because Total Pulse Licenses Leased out of new License server is greater than 11500.
                 <br>
                 <br>
                 <br>
                 <br>
                1) Total Licenses Leased out =  """ + str(item['total-count']) + """ <br>
                2) Total Licenses Limit  = 12000 <br>
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
            print(e,"Error: unable to send email")


keys = lst[0].keys()
with open('/network/scripts/WFH/Output/license.csv', 'wb') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(lst)
keys1 = lst1[0].keys()
with open('/network/scripts/WFH/Output/total-license.csv', 'wb') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys1)
    dict_writer.writeheader()
    dict_writer.writerows(lst1)
