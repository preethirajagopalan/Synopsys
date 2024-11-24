#!/opt/python-2.7.13/bin/python -u 
import requests
import json
import smtplib
from datetime import date
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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
    if item['total-count'] > 10900:
        #print(item['total-count'])
        sender = 'preeraja@synopsys.com'
        receivers = ['preeraja@synopsys.com']
        SUBJECT = "Total Licenses Leased out of new license server is greater than 10900"
        BODY = MIMEMultipart('alternative')
        BODY['Subject'] = SUBJECT
        BODY['From'] = sender
        BODY['To'] = ','.join(receivers)
        TEXT = """\
             <html>
             <body>
             <p>This is an automated email to alert on " Total Licenses Leased out of new License server is greater than 10900", please do not REPLY to it.
                 <br>
                 <br>
                 You are receiving this alert because Total Licenses Leased out of new License server is greater than 10900.
                 <br>
                 <br>
                 <br>
                 <br>
                1) " Total Licenses Leased out =  """ + str(item['total-count']) + """ <br>
                2) " Total Licenses Limit " = 11000 <br>
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


