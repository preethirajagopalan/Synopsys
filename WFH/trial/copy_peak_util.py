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
import sys

pst = timezone('US/Pacific')
dateTimeObj1 = datetime.now(pst)
dateStr1 = dateTimeObj1.strftime("%m/%d/%Y")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


password = get_password()
mst = timezone('CET')
dateTimeObj = datetime.utcnow()
dateStr = dateTimeObj.strftime("%m/%d/%Y")
dateTimeObj1 = datetime.utcnow()
print(dateStr, dateStr1)

conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                             'SERVER=10.225.16.15;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;'
                             'UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
cursor_int = conn_intsql.cursor()
print("connected successfully intl")
cursor_int.execute("""SELECT [NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[DateTime],
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[In_Averagebps],
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[Out_Averagebps],
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[NodeID],
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID],
[NetPerfMonInt].[dbo].[Interfaces].[FullName]
FROM [NetPerfMonInt].[dbo].[InterfaceTraffic_Detail] join [NetPerfMonInt].[dbo].[Interfaces]
on [NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID] =
[NetPerfMonInt].[dbo].[Interfaces].[InterfaceID] where
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[DateTime] > '%s' and
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[In_Averagebps] is not NULL and
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[Out_Averagebps] is not NULL and
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41725'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41720'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40658'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40655'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'30215'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'28179'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46262'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46271'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46931'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40390'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'29673'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'29671'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'33599'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40385'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'42613'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40598'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'44752'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'27467'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'47323'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'39730'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'44646'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'33404'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'33397'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41503'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41195'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41769'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'28791'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40563'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40559'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'38792'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41350'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46255'	or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'42821'	
""" % (dateStr))
result_int = cursor_int.fetchall()
items_int = [dict(zip([key[0].lower() for key in cursor_int.description], row)) for row in result_int]
conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                            'SERVER=10.200.17.64;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)

cursor = conn_ussql.cursor()
print("connected US")
cursor.execute("""SELECT [NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[DateTime],
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[In_Averagebps],
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[Out_Averagebps],
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[NodeID],
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID],
[NetPerfMonUS].[dbo].[Interfaces].[FullName]
FROM [NetPerfMonUS].[dbo].[InterfaceTraffic_Detail] join [NetPerfMonUS].[dbo].[Interfaces]
on [NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID] =
[NetPerfMonUS].[dbo].[Interfaces].[InterfaceID] where
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[DateTime] > '%s' and
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[In_Averagebps] is not NULL and
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[Out_Averagebps] is not NULL and
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'66803'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'66807'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'91757'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'88434'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'135853' or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'139169' or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'137213' or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'86710'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'86724'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'87045'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'140176'
""" % (dateStr1))
result = cursor.fetchall()
items = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result]
cursor.close()
conn_ussql.close()
items.extend(items_int)
int_list = []
for x in items:
    if x['in_averagebps'] is None:
        x['in_averagebps'] = 0
    if x['out_averagebps'] is None:
        x['out_averagebps'] = 0
    alternate = {'in_averagebps': x['in_averagebps'], 'out_averagebps': x['out_averagebps'],
                 'fullname': (x['fullname']), 'datetime': x['datetime']
                 }
    int_list.append(alternate)
final = ast.literal_eval(json.dumps(int_list, default=json_serial))
# sys.stdout = open("/network/scripts/WFH/trial/output/file.txt", "w+")
# print(final)
final_list = []
for x in final:
    max_bps = max(x['in_averagebps'], x['out_averagebps'])
    if 'mpls' in x['fullname']:
        alternate = {
            '@timestamp': dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f"),
            'type': 'CircuitUtil',
            'Device': ((x['fullname'].split('-')[0]).lower().strip()),
            'Peak': max_bps,
            'service': 'MPLS'}
        final_list.append(alternate)
    if 'vpn' in x['fullname']:
        alternate1 = {
            '@timestamp': dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f"),
            'type': 'CircuitUtil',
            'Device': (x['fullname'].split('-')[0]).lower().strip(),
            'Peak': max_bps,
            'service': 'ISP'}
        final_list.append(alternate1)
print(final_list)
result_final = []

for x in final_list:
    if ((x['Device'] == 'ca06' or x['Device'] == 'pl01' or x['Device'] == 'pt02' or x['Device'] == 'tw01' or x[
        'Device'] == 'pt01') and x['service'] == 'MPLS'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 100000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'se80') and x['service'] == 'MPLS'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 20000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'cl01' or x['Device'] == 'gb01' or x['Device'] == 'cn30') and x['service'] == 'MPLS'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 50000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'fr65' or x['Device'] == 'tw52' or x['Device'] == 'us03' or x['Device'] == 'us04') and x[
        'service'] == 'MPLS'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 200000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'am04' or x['Device'] == 'cn58') and x['service'] == 'MPLS'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 300000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'cn42' or x['Device'] == 'indc' or x['Device'] == 'jp01' or x['Device'] == 'mdc') and x[
        'service'] == 'MPLS'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 500000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'indc') and x['service'] == 'ISP'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 3000000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'am04' or x['Device'] == 'ca06' or x['Device'] == 'in19' or x['Device'] == 'jp01' or x[
        'Device'] == 'mdc' or x['Device'] == 'pt01' or x['Device'] == 'pt02' or x['Device'] == 'us03' or x[
             'Device'] == 'us04') and x['service'] == 'ISP'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 1000000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'cn58' or x['Device'] == 'fr65' or x['Device'] == 'il01') and x['service'] == 'ISP'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 500000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'cn42' or x['Device'] == 'gb01' or x['Device'] == 'tw52') and x['service'] == 'ISP'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 300000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'pl01' or x['Device'] == 'tw01') and x['service'] == 'ISP'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 200000000
        }
        result_final.append(dict)
    if ((x['Device'] == 'cl01' or x['Device'] == 'se80' or x['Device'] == 'cn30') and x['service'] == 'ISP'):
        dict = {
            'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
            'service': x['service'], 'Circuit Size': 100000000
        }
        result_final.append(dict)

keys = result_final[0].keys()
with open('/network/scripts/WFH/Output/peak_list.csv', 'wb') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(result_final)



