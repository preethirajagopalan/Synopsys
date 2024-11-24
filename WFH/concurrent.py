#!/opt/python-2.7.13/bin/python -u
from __future__ import division
from pst_to_utc import timefunc, timefunc_cet
import pyodbc
import datetime
import MySQLdb
from helper import get_password
import json
import ast
from datetime import date, datetime
from dateutil.tz import tzutc
import csv
import pytz
import datetime
from pytz import timezone
from datetime import datetime
import dateutil.parser
import peak_util
import license
import sys
print("---------------------------concurrent.py-----------------------------------------------------------------------")



new_dict ={
"tw52-vpn-vm-91r43":"2500",
"cn42-vpn-vm-91r43":"2500",
"ca06-vpn-vm-91r43":"2500",
"am04-vpn-vm-9143":"2500",
"ca06-vpn-vm-mgmt":"2500",
"ru20-vpn-vm-mgmt":"2500",
"am04-vpn-vm-mgmt":"2500",
"cn42-vpn-vm-mgmt":"2500",
"tw52-vpn-vm-mgmt":"2500",
"kr02-vpn-mgmt":"100",
"ca06-vpn-mgmt":"1000",
"cl01-vpn-mgmt":"200",
"us04-vpn-mgmt":"1000",
"ca11-vpn-mgmt":"200",
"ru20-vpn-mgmt":"200",
"cn30-vpn-mgmt":"2500",
"cn42-vpn-mgmt":"200",
"cn58-vpn-mgmt":"2500",
"fr65-vpn-mgmt":"200",
"gb01-vpn-mgmt":"200",
"il01-vpn-mgmt":"200",
"in19-vpn-mgmt":"2500",
"jp01-vpn-mgmt":"2500",
"pt02-vpn-mgmt":"200",
"tw52-vpn-mgmt":"200",
"hqdc-vpn-1-mgmt":"25000",
"hqdc-vpn-2-mgmt":"25000",
"us03-vpn-1-mgmt":"1000",
"us03-vpn-2-mgmt":"1000",
"indc-vpn-1-mgmt":"2500",
"indc-vpn-2-mgmt":"2500",
"mdc-vpn-1-mgmt":"2500",
"mdc-vpn-2-mgmt":"2500",
"pl01-vpn-mgmt":"100",
"pt01-vpn-mgmt":"100",
"se80-vpn-mgmt":"100",
"tw01-vpn-mgmt":"100",
"vn04-ram":"100"
}


final_list = []

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


password = get_password()
dateTimeObj = datetime.utcnow()
dateStr = dateTimeObj.strftime("%m/%d/%Y")
pst = timezone('US/Pacific')
dateTimeObj1 = datetime.now(pst)
dateStr1 = dateTimeObj1.strftime("%m/%d/%Y")

conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                             'SERVER=10.225.16.15;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;'
                             'UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
cursor_int = conn_intsql.cursor()
cursor_int.execute("""SELECT 
[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[AssignmentName],
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[DateTime],
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[Status] as 'Max_ConCurrentUsers'
FROM [NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail] 
left join [NetPerfMonInt].[dbo].[CustomPollerAssignmentView] on 
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID] = 
[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[CustomPollerAssignmentID]
where 
([NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[DateTime] < getutcdate() and
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[DateTime] > 
DATEADD(minute, -15, FORMAT(getutcdate(), 'MM/dd/yyyy HH:mm:ss')))
and [NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[CustomPollerName] = 'iveConcurrentUsers'
group by
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID]
,[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[AssignmentName],[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[Status],
[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[CustomPollerName], [NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[DateTime]""")
result_int = cursor_int.fetchall()
items_int = [dict(zip([key[0].lower() for key in cursor_int.description], row)) for row in result_int]
conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                            'SERVER=10.200.17.64;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)

cursor = conn_ussql.cursor()
cursor.execute(
    """SELECT 
[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[AssignmentName],[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[DateTime],
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[Status] as 'Max_ConCurrentUsers'
FROM [NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail] 
left join [NetPerfMonUS].[dbo].[CustomPollerAssignmentView] on 
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID] = 
[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[CustomPollerAssignmentID] 
where 
([NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[DateTime] < getutcdate() and
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[DateTime] > 
DATEADD(minute, -15, FORMAT(getutcdate(), 'MM/dd/yyyy HH:mm:ss')))
and [NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[CustomPollerName] = 'iveConcurrentUsers'
group by
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID]
,[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[AssignmentName],[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[Status],
[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[CustomPollerName],
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[DateTime]
    """)
result = cursor.fetchall()
items = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result]
cursor.close()
conn_ussql.close()
items.extend(items_int)
final = ast.literal_eval(json.dumps(items, default=json_serial))
# sys.stdout = open("/network/scripts/WFH/printoutput0.txt", "w")
# print(final)
# sys.stdout.close()
# for x in final:
#         # print(x)
#         alternate = {'VPN Gateway': (((x['assignmentname'].replace("iveConcurrentUsers on", " ")).lower()).replace(".internal.synopsys.com", "")), 'max_concurrentusers': int(x['max_concurrentusers']),
#                      '@timestamp': nowfunc.now, 'type': 'Pulse', 'SiteCode':((x['assignmentname'].replace("iveConcurrentUsers on", " ")).split('-')[0]).lower()}
#         final_list.append(alternate)
#print(final)
for x in final:
    A = int(((x['max_concurrentusers'])))
    B = int(new_dict[((x['assignmentname'].replace("iveConcurrentUsers on", " ")).lower()).replace(".internal.synopsys.com","").strip()])
    C = float(A/B)*100
    time = dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f")
    alternate = {'VPN Gateway': (
        ((x['assignmentname'].replace("iveConcurrentUsers on", " ")).lower()).replace(".internal.synopsys.com", "").strip()),
                 'max_concurrentusers': int(x['max_concurrentusers']),
        'PerCentUsage':C,
                 '@timestamp': time, 'type': 'Pulse', 'VPN Capcity':(new_dict[((x['assignmentname'].replace("iveConcurrentUsers on", " ")).lower()).replace(".internal.synopsys.com", "").strip()])
    }
    final_list.append(alternate)
# sys.stdout = open("/network/scripts/WFH/printoutput1.txt", "w")
# print(final_list)
# sys.stdout.close()

keys = final_list[0].keys()
with open('/network/scripts/WFH/Output/concurrent_list.csv', 'wb') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(final_list)


