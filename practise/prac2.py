#!/opt/python-2.7.13/bin/python -u

import pyodbc
from helper import get_password
import MySQLdb
password = get_password()
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
# print(type(result_int))
# print(result_int)


for row in result_int:
    print(row)
    break

# for key in cursor_int.description:
#     print(key[0].lower())


