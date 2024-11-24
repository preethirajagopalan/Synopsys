#!/opt/python-2.7.13/bin/python -u
from pst_to_utc import timefunc, timefunc_cet
import pyodbc
import datetime
from datetime import datetime
from datetime import date
import pytz
from pytz import timezone
import dateutil.parser
from dateutil.tz import tzutc
import MySQLdb
from helper import get_password
import json
import ast
import csv
import sys
print("-------------------------------peak_util.py-----------------------------------------------------------")
pst = timezone('US/Pacific')
dateTimeObj1 = datetime.now(pst)
dateStr1 = dateTimeObj1.strftime("%m/%d/%Y")
print(dateStr1)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


password = get_password()
dateTimeObj = datetime.utcnow()
dateStr = dateTimeObj.strftime("%m/%d/%Y")
dateTimeObj1 = datetime.utcnow()
print("yes")
print(dateStr)


conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                             'SERVER=10.225.16.15;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;'
                             'UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
#INTL-ISP
cursor_int = conn_intsql.cursor()
cursor_int.execute("""SELECT 
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[DateTime],
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
([NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41725' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40658' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'30215' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46262' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46931' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'29673' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'33599' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'42613' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'44752' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'47323' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'39730' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'33404' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41503' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41769' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40563' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'38792' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46255')""" % (dateStr))

result_int = cursor_int.fetchall()
items_int = [dict(zip([key[0].lower() for key in cursor_int.description], row)) for row in result_int]
#INTL-MPLS
cursor_int_mpls = conn_intsql.cursor()
cursor_int_mpls.execute("""SELECT 
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[DateTime],
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
([NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41720' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40655' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'28179' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'46271' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40390' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'29671' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40385' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'40598' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'44646' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'33397' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'41195' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'28791' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'49849' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'50000' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'50002' or
[NetPerfMonInt].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'42821')""" % (dateStr))

result_int_mpls = cursor_int_mpls.fetchall()
items_int_mpls = [dict(zip([key[0].lower() for key in cursor_int_mpls.description], row)) for row in result_int_mpls]
print(items_int_mpls)
cursor_int.close()
cursor_int_mpls.close()
conn_intsql.close()




conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                            'SERVER=10.200.17.64;PORT=1433;TDS_Version=8.0;ClientCharset=UTF-8;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
#US-ISP
cursor = conn_ussql.cursor()
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
([NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'66803'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'91757'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'135853' or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'86710'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'87045')""" % (dateStr1))
result = cursor.fetchall()
items = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result]
#US-MPLS
cursor_us_mpls = conn_ussql.cursor()
cursor_us_mpls.execute("""SELECT [NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[DateTime],
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
([NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'66807'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'86724'	or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'88434' or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'137213' or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'139169' or
[NetPerfMonUS].[dbo].[InterfaceTraffic_Detail].[InterfaceID]=	'140176')""" % (dateStr1))
result_us_mpls = cursor_us_mpls.fetchall()
items_us_mpls = [dict(zip([key[0].lower() for key in cursor_us_mpls.description], row)) for row in result_us_mpls]

cursor.close()
cursor_us_mpls.close()
conn_ussql.close()


us_list = []
int_list = []
for x in items_int:
    if x['in_averagebps'] is None:
        x['in_averagebps'] = 0
    if x['out_averagebps'] is None:
        x['out_averagebps'] = 0
    alternate = {'in_bps': x['in_averagebps'], 'out_bps': x['out_averagebps'],
                 'fullname': (x['fullname']), 'datetime': x['datetime'],
                 'service': 'ISP'
                 }
    int_list.append(alternate)
for x in items_int_mpls:
    if x['in_averagebps'] is None:
        x['in_averagebps'] = 0
    if x['out_averagebps'] is None:
        x['out_averagebps'] = 0
    alternate = {'in_bps': x['in_averagebps'], 'out_bps': x['out_averagebps'],
                 'fullname': (x['fullname']), 'datetime': x['datetime'],
                 'service': 'MPLS'
                 }
    int_list.append(alternate)
for x in items:
    if x['in_averagebps'] is None:
        x['in_averagebps'] = 0
    if x['out_averagebps'] is None:
        x['out_averagebps'] = 0
    alternate = {'in_bps': x['in_averagebps'], 'out_bps': x['out_averagebps'],
                 'fullname': (x['fullname']), 'datetime': x['datetime'],
                 'service': 'ISP'
                 }
    us_list.append(alternate)
for x in items_us_mpls:
    if x['in_averagebps'] is None:
        x['in_averagebps'] = 0
    if x['out_averagebps'] is None:
        x['out_averagebps'] = 0
    alternate = {'in_bps': x['in_averagebps'], 'out_bps': x['out_averagebps'],
                 'fullname': (x['fullname']), 'datetime': x['datetime'],
                 'service': 'MPLS'
                 }
    us_list.append(alternate)
final_int = ast.literal_eval(json.dumps(int_list, default=json_serial))
final_us = ast.literal_eval(json.dumps(us_list, default=json_serial))



final_list = []
result_final = []
for x in final_int:
    max_bps = ((max(x['in_bps'], x['out_bps']))/1000000)
    time = timefunc_cet(dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f"))
    alternate = {
            'in_bps': float(x['in_bps']),
            'out_bps': float(x['out_bps']),
            '@timestamp': time,
            'type': 'CircuitUtil',
            'Device': ((x['fullname'].split('-')[0]).lower().strip()),
            'Peak': max_bps,
            'service': x['service']}
    final_list.append(alternate)
for x in final_us:
    max_bps = ((max(x['in_bps'], x['out_bps']))/1000000)
    time = timefunc(dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f"))
    alternate = {
            'in_bps': float(x['in_bps']),
            'out_bps': float(x['out_bps']),
            '@timestamp': time,
            'type': 'CircuitUtil',
            'Device': ((x['fullname'].split('-')[0]).lower().strip()),
            'Peak': max_bps,
            'service': x['service']}
    final_list.append(alternate)

for x in final_list:
    if (x['service'] == 'MPLS'):
        if (x['Device'] == 'se80'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 20,
                    'PerCent': ((x['Peak'] / 20) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'indc')):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 800,
                    'PerCent': ((x['Peak'] / 800) * 100)
                    }
            # print(dict)
            result_final.append(dict)
        elif ((x['Device'] == 'cl01' or x['Device'] == 'gb01' or x['Device'] == 'cn30' or x['Device'] == 'il01')):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 50,
                    'PerCent': ((x['Peak'] / 50) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'ca06' or x['Device'] == 'pl01' or x['Device'] == 'pt02' or x['Device'] == 'pt01')):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 100,
                    'PerCent': ((x['Peak'] / 100) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'fr65' or x['Device'] == 'tw01' or x['Device'] == 'us03' or x['Device'] == 'us04'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 200,
                    'PerCent': ((x['Peak'] / 200) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'am04' or x['Device'] == 'cn58')):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 300,
                    'PerCent': ((x['Peak'] / 300) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'tw52')):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 400,
                    'PerCent': ((x['Peak'] / 400) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'cn42' or x['Device'] == 'jp01')):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 500,
                    'PerCent': ((x['Peak'] / 500) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'sv1' or x['Device'] == 'sv2'or x['Device'] == 'mdc')):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 1000,
                    'PerCent': ((x['Peak'] / 1000) * 100)
                    }

    elif(x['service'] == 'ISP'):
        if (x['Device'] == 'sv2'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 10000,
                    'PerCent': ((x['Peak'] / 10000) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'indc'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 3000, 'PerCent': ((x['Peak'] / 3000) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'am04' or x['Device'] == 'ca06' or x['Device'] == 'in19' or x['Device'] == 'jp01' or
               x['Device'] == 'mdc' or x['Device'] == 'pt01' or x['Device'] == 'pt02' or x['Device'] == 'us03' or
               x['Device'] == 'us04')):
                dict = {'in_bps': float(x['in_bps']),
                        'out_bps': float(x['out_bps']),
                        'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                        'service': x['service'], 'Circuit Size': 1000, 'PerCent': ((x['Peak'] / 1000) * 100)
                        }
                result_final.append(dict)
        elif (x['Device'] == 'cn58' or x['Device'] == 'fr65' or x['Device'] == 'il01'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 500, 'PerCent': ((x['Peak'] / 500) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'cn42' or x['Device'] == 'gb01' or x['Device'] == 'tw52'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 300, 'PerCent': ((x['Peak'] / 300) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'pl01' or x['Device'] == 'tw01'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 200,
                    'PerCent': ((x['Peak'] / 200) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'cl01' or x['Device'] == 'se80' or x['Device'] == 'cn30'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 100, 'PerCent': ((x['Peak'] / 100) * 100)
                    }
            result_final.append(dict)

keys = result_final[0].keys()
with open('/network/scripts/WFH/Output/peak_list.csv', 'w+') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(result_final)

