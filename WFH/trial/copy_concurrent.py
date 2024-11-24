#!/opt/python-2.7.13/bin/python -u
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


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
    
password = get_password()
dateTimeObj = datetime.utcnow()
dateStr = dateTimeObj.strftime("%m/%d/%Y")
pst = timezone('US/Pacific')
dateTimeObj1 = datetime.now(pst)
dateStr1 = dateTimeObj1.strftime("%m/%d/%Y")
print(dateStr,dateStr1)

conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                     'SERVER=10.225.16.15;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;'
                             'UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
cursor_int = conn_intsql.cursor()
print("connected successfully")
cursor_int.execute("""SELECT 
[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[AssignmentName],
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[DateTime],
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[Status] as 'Max_ConCurrentUsers'
FROM [NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail] 
left join [NetPerfMonInt].[dbo].[CustomPollerAssignmentView] on 
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID] = 
[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[CustomPollerAssignmentID] 
where [NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[DateTime] > '%s' 
and [NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[CustomPollerName] = 'iveConcurrentUsers'
group by
[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID]
,[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[AssignmentName],[NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[Status],
[NetPerfMonInt].[dbo].[CustomPollerAssignmentView].[CustomPollerName], [NetPerfMonInt].[dbo].[CustomPollerStatistics_Detail].[DateTime] """ % (dateStr))
result_int = cursor_int.fetchall()
items_int = [dict(zip([key[0].lower() for key in cursor_int.description], row)) for row in result_int]
conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                    'SERVER=10.200.17.64;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)


cursor = conn_ussql.cursor()
cursor.execute(
            """
            SELECT 
[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[AssignmentName],[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[DateTime],
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[Status] as 'Max_ConCurrentUsers'
FROM [NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail] 
left join [NetPerfMonUS].[dbo].[CustomPollerAssignmentView] on 
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID] = 
[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[CustomPollerAssignmentID] 
where [NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[DateTime] > '%s' 
and [NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[CustomPollerName] = 'iveConcurrentUsers'
group by
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[CustomPollerAssignmentID]
,[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[AssignmentName],[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[Status],
[NetPerfMonUS].[dbo].[CustomPollerAssignmentView].[CustomPollerName],
[NetPerfMonUS].[dbo].[CustomPollerStatistics_Detail].[DateTime]
            """% (dateStr1))
result = cursor.fetchall()
items = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result]
#print(items)
cursor.close()
conn_ussql.close()
items.extend(items_int)
final = ast.literal_eval(json.dumps(items, default=json_serial))
final_list = []
# for x in final:
#         # print(x)
#         alternate = {'VPN Gateway': (((x['assignmentname'].replace("iveConcurrentUsers on", " ")).lower()).replace(".internal.synopsys.com", "")), 'max_concurrentusers': int(x['max_concurrentusers']),
#                      '@timestamp': nowfunc.now, 'type': 'Pulse', 'SiteCode':((x['assignmentname'].replace("iveConcurrentUsers on", " ")).split('-')[0]).lower()}
#         final_list.append(alternate)
# print(final_list)
for x in final:
        #print(type(x['datetime']))
        alternate = {'VPN Gateway': (((x['assignmentname'].replace("iveConcurrentUsers on", " ")).lower()).replace(".internal.synopsys.com", "")), 'max_concurrentusers': int(x['max_concurrentusers']),
                     '@timestamp': dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f"), 'type': 'Pulse'}
        final_list.append(alternate)
#print(final_list)
keys = final_list[0].keys()
with open('/network/scripts/WFH/Output/concurrent_list.csv', 'wb') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(final_list)


