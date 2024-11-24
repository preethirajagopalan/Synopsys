#!/opt/python-2.7.13/bin/python -u
from elasticsearch import Elasticsearch
import pyodbc
import datetime
import smtplib
import MySQLdb
from helper import get_password
import itertools
import collections
from collections import Counter
from collections import defaultdict
import json
import ast
from collections import defaultdict
from datetime import date
from datetime import datetime
import datetime
from dateutil.tz import tzutc
from airwave_api import ap_count
import csv
now = datetime.datetime.utcnow()
site_list = []
ap_count_list = []
interactive_site_list = []



def device_all():
    global items, items_int
    # Mail settings to send error reports
    me = 'preeraja@synopsys.com'
    you = ['preeraja@synopsys.com']
    # print("mail settings success")

    try:
        # retrieve password for Solar Winds
        password = get_password()

        # connection to US-SQL
        conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                    'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)

        # cursor for the database
        cursor = conn_ussql.cursor()
        cursor.execute(
            """SELECT Network_Device_Type, COUNT(*) as "total items" FROM [dbo].[Nodes] where Network_Device_Type IS NOT NULL GROUP BY Network_Device_Type;""")

        result = cursor.fetchall()
        # print(result)
    # catch the exception and send the error as-is
    except Exception as e:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Test'
        msg['From'] = me
        msg['To'] = ", ".join(you)
        text = "Connection to US-Sql Database Failed (Interface)" + "\n" + "Error: " + repr(e)
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        try:
            s = smtplib.SMTP('mailhost')
            print("Connected to SMTP")
            s.set_debuglevel(True)
            s.sendmail(me, you, msg.as_string())
            print("Sent E-Mail")
            s.quit()
        except smtplib.SMTPException as ex:
            print(ex)
        print(e)
    # convert tuple to data dictionary

    items = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result]
    #print(type(items))

    # close cursor and database connection after data extraction
    cursor.close()
    conn_ussql.close()
    print(
        "-----------------------------------------------SOLARWINDS-US----------------------------------------------------------")
    # print(items)

    ###############solarwinds-intl###############################
    # Mail settings to send error reports
    me = 'preeraja@synopsys.com'
    you = ['preeraja@synopsys.com']

    # print("mail settings success")

    try:

        # retrieve password for Solar Winds

        password = get_password()

        # connection to intl-SQL
        #print("here..")
        conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                     'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)

        # cursor for the database
        cursor_int = conn_intsql.cursor()
        print("connected successfully")
        cursor_int.execute(
            """SELECT Network_Device_Type, COUNT (*) AS "total items" FROM [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type IS NOT NULL GROUP BY Network_Device_Type;""")

        # gather all data from Solarwinds-INTL-SQL
        result_int = cursor_int.fetchall()

        # print(result)
    # catch the exception and send the error as-is
    except Exception as e:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'INTL'
        msg['From'] = me
        msg['To'] = ", ".join(you)
        text = "Connection to INTL-Sql Database Failed (Interface)" + "\n" + "Error: " + repr(e)
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        try:
            s = smtplib.SMTP('mailhost')
            print("Connected to SMTP")
            s.set_debuglevel(True)
            s.sendmail(me, you, msg.as_string())
            print("Sent E-Mail")
            s.quit()
        except smtplib.SMTPException as ex:
            print(ex)
        print(e)
    # convert tuple to data dictionary

    items_int = [dict(zip([key[0].lower() for key in cursor_int.description], row)) for row in result_int]
    #print(items_int)

    # close cursor and database connection after data extraction
    cursor_int.close()
    conn_intsql.close()
    #print("done")
    print(
        "-----------------------------------------------SOLARWINDS-INTL--------------------------------------------------------")
    # print(items_int)

    # Combine the list of dictionaries as one list of dictionary (Solarwinds-us + sOLARWINDS-INT)

    C_counts = Counter()
    for l in (items, items_int):
        #print("counters")
        #print(l)
        C_counts.update({x['network_device_type']: x['total items'] for x in l})

    C = [{'network_device_type': k, 'total items': c} for (k, c) in C_counts.items()]
    #print("printing c")
    #print(C)


    ###########type casting int#########################
    for i in C:
        for key, value in i.iteritems():
            #print(i)
            if key == "total items":
                try:
                    i[key] = int(value)
                    #("yess")
                    #print(key, value)
                except ValueError as v:
                     print("value error")

            if key == "'network_device_type":
                #print("noo")
                i[key] = str(value)
                #print(key,value)

    #print("good c")
    #print(type(C))
    a = (json.dumps(C))
    #print(a)

    final = ast.literal_eval(json.dumps(C))
    #final = (json.dumps(C))
    #print(final)


    time_field = {'@timestamp': now}
    type_field = {'type': "all"}

    for n in final:
        n.update(time_field)
        n.update(type_field)
    print("--------------------------------------------all result----------------------------------------")
    # REMOVE NON_NETWORK_STUFF
    for i in range(len(final)):
        if final[i]['network_device_type'] == 'NON_NETWORK_STUFF':
            del final[i]
            break
    keys = final[0].keys()
    with open('/network/scripts/inventory/Result/main.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final)
    return final

def device_us():

    for i in items:
        for key, value in i.iteritems():
            # print(key)
            if key == "total items":
                i[key] = int(value)
            if key == "'network_device_type":
                i[key] = str(value)
                # print(key,type(value))

    us_json = ast.literal_eval(json.dumps(items))

    time_field = {'@timestamp': now}
    type_field = {'type': "us"}

    for b in us_json:
        b.update(time_field)
        b.update(type_field)
    print("--------------------------------------------us result----------------------------------------")
    #print(us_json)
    #REMOVE NON_NETWORK_STUFF
    for i in range(len(us_json)):
        if us_json[i]['network_device_type'] == 'NON_NETWORK_STUFF':
            del us_json[i]
            break

    #print(us_json)

    keys = us_json[0].keys()
    with open('/network/scripts/inventory/Result/us.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(us_json)
    return us_json

def device_int():

    for i in items_int:
        for key, value in i.iteritems():
            if key == "total items":
                i[key] = int(value)
            if key == "'network_device_type":
                i[key] = str(value)
                # print(key,type(value))

    int_json = ast.literal_eval(json.dumps(items_int))
    #print(int_json, type(int_json))
    time_field = {'@timestamp': now}
    type_field = {'type': "int"}

    for v in int_json:
        v.update(time_field)
        v.update(type_field)
    print("-------------------------------------------int result----------------------------------------")
    # REMOVE NON_NETWORK_STUFF
    for i in range(len(int_json)):
        if int_json[i]['network_device_type'] == 'NON_NETWORK_STUFF':
            del int_json[i]
            break

    keys = int_json[0].keys()

    with open('/network/scripts/inventory/Result/int.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(int_json)
    return int_json

    #print(int_json)

def site():
    password = get_password()
    # connection to US-SQL
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    # cursor for the database
    cursor = conn_ussql.cursor()
    cursor.execute(
        """select count (distinct SITE) as Site_Count from [dbo].[Nodes] where SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    # gather all data from Solarwinds-US-SQL
    result_us = cursor.fetchall()
    cursor.execute("""select COUNT(DISTINCT SITE) from [dbo].[Nodes] where Network_Device_Type = 'SWITCH_DC' or Network_Device_Type = 'PAN_DC_FW' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    dc_site_us = cursor.fetchall()

    cursor.execute("""select count(distinct SITE) as DMZ_Site_Count_US from [dbo].[Nodes] where Network_Device_Type = 'SWITCH_DMZ' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    dmz_site_us = cursor.fetchall()

    cursor.execute("""select count (distinct Site) from [dbo].[Nodes] where Caption like '%sc9%' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    scs_us = cursor.fetchall()

    cursor.execute("""select count(caption) from [dbo].[nodes] where caption like '%cppm%' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    us_cppm = cursor.fetchall()

    # connection to intl-SQL
    conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    # cursor for the database
    cursor_int = conn_intsql.cursor()
    cursor_int.execute("""select count (distinct SITE) as Site_Count from [NetPerfMonInt].[dbo].[Nodes] where SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    result_int = cursor_int.fetchall()
    cursor_int.execute("""select COUNT(DISTINCT SITE) from [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_DC' or Network_Device_Type = 'PAN_DC_FW' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US'; """)
    dc_site_int = cursor_int.fetchall()
    cursor_int.execute("""select count (distinct SITE) as DMZ_Site_Count_Int from [NetPerfMonInt].[dbo].[Nodes] where Network_Device_Type = 'SWITCH_DMZ' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    dmz_site_int = cursor_int.fetchall()
    cursor_int.execute("""select count (distinct Site) from [NetPerfMonInt].[dbo].[Nodes] where Caption like '%scs%' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    scs_int = cursor_int.fetchall()
    cursor_int.execute("""select count(caption) from [NetPerfMonInt].[dbo].[nodes] where caption like '%cppm%' AND SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    int_cppm = cursor_int.fetchall()

    #print(result_us, result_int)
    r_us = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result_us]
    r_int = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result_int]
    dc_site_us_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in dc_site_us]
    dc_site_int_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in dc_site_int]
    dmz_site_us_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in dmz_site_us]
    dmz_site_int_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in dmz_site_int]
    scs_us_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in scs_us]
    scs_int_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in scs_int]

    us_cppm_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in us_cppm]
    int_cppm_count = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in int_cppm]


    json_us = ast.literal_eval(json.dumps(r_us))
    json_int = ast.literal_eval(json.dumps(r_int))

    dc_site_us_json = ast.literal_eval(json.dumps(dc_site_us_count))
    dc_site_int_json = ast.literal_eval(json.dumps(dc_site_int_count))

    dmz_site_us_json = ast.literal_eval(json.dumps(dmz_site_us_count))
    dmz_site_int_json = ast.literal_eval(json.dumps(dmz_site_int_count))

    scs_us_json = ast.literal_eval(json.dumps(scs_us_count))
    scs_int_json = ast.literal_eval(json.dumps(scs_int_count))

    us_cppm_json = ast.literal_eval(json.dumps(us_cppm_count))
    int_cppm_json = ast.literal_eval(json.dumps(int_cppm_count))


    global q, w, o, p, h, j, v, d, f, g, v_cppm_us, v_cppm_int, v_cppm_all, ip

    for x in json_us:
        q = x.values()[0]

    for y in json_int:
        w = y.values()[0]

    e = int(q) + int(w)

    for x in dc_site_us_json:
        o = x.values()[0]

    for x in dc_site_int_json:
        p = x.values()[0]

    ip = int(o) + int(p)

    for x in dmz_site_us_json:
        h = x.values()[0]

    for y in dmz_site_int_json:
        j = y.values()[0]
    v = int(h) + int(j)

    for x in scs_us_json:
        d = x.values()[0]
    for y in scs_int_json:
        f = y.values()[0]
    g = d + f


    for x in us_cppm_json:
        v_cppm_us = x.values()[0]
    for y in int_cppm_json:
        v_cppm_int = y.values()[0]
    v_cppm_all = v_cppm_us + v_cppm_int


    all = {'type':'site','total items': e, 'network_device_type': 'site_count_all'}
    us = {'type':'site','total items': q, 'network_device_type': 'site_count_us'}
    intl = {'type':'site','total items': w, 'network_device_type': 'site_count_int'}
    dc_us = {'type':'dc_site', 'total items':o, 'network_device_type': 'dc_site_count_us'}
    dc_int = {'type': 'dc_site', 'total items': p, 'network_device_type': 'dc_site_count_int'}
    dc_all = {'type':'dc_site', 'total items':ip, 'network_device_type': 'dc_site_count_all'}
    dmz_us = {'type':'dmz_site', 'total items':h, 'network_device_type': 'dmz_site_count_us'}
    dmz_int = {'type': 'dmz_site', 'total items': j, 'network_device_type': 'dmz_site_count_int'}
    dmz_all = {'type': 'dmz_site', 'total items': v, 'network_device_type': 'dmz_site_count_all'}
    scs_us = {'type': 'scs_site', 'total items': d, 'network_device_type': 'scs_site_count_us'}
    scs_int = {'type': 'scs_site', 'total items': f, 'network_device_type': 'scs_site_count_int'}
    scs_all = {'type': 'scs_site', 'total items': g, 'network_device_type': 'scs_site_count_all'}
    cppm_int = {'type': 'cppm', 'total items': v_cppm_int, 'network_device_type': 'cppm_int'}
    cppm_us = {'type': 'cppm', 'total items': v_cppm_us, 'network_device_type': 'cppm_us'}
    cppm_all = {'type': 'cppm', 'total items': v_cppm_all, 'network_device_type': 'cppm_all'}

    time_field = {'@timestamp': now}
    site_list.append(all)
    site_list.append(us)
    site_list.append(intl)
    site_list.append(dc_us)
    site_list.append(dc_int)
    site_list.append(dc_all)
    site_list.append(dmz_us)
    site_list.append(dmz_int)
    site_list.append(dmz_all)
    site_list.append(scs_us)
    site_list.append(scs_int)
    site_list.append(scs_all)
    site_list.append(cppm_int)
    site_list.append(cppm_us)
    site_list.append(cppm_all)


    for b in site_list:
        b.update(time_field)


    keys = site_list[0].keys()
    with open('/network/scripts/inventory/Result/site_list.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(site_list)
    return site_list

def airwave_ap():
    ap = {'type': 'ap', 'total items': ap_count, 'network_device_type': 'ap_count'}
    time_field = {'@timestamp': now}
    ap_count_list.append(ap)
    for b in ap_count_list:
        b.update(time_field)
    keys = ap_count_list[0].keys()
    with open('/network/scripts/inventory/Result/ap_count_list.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(ap_count_list)
    return ap_count_list

def vpn_device_list():
    password = get_password()
    # connection to us-SQL
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor = conn_ussql.cursor()
    cursor.execute(
        """SELECT Caption as vpn FROM [dbo].[Nodes] where Caption like '%-vpn-router%' and Caption not like '%module%';""")
    device_us = cursor.fetchall()

    # connection to intl-SQL
    conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor_int = conn_intsql.cursor()
    cursor_int.execute(
        """select Caption as vpn from [NetPerfMonInt].[dbo].[Nodes] where Caption like '%-vpn-router%' and Caption not like '%module%';""")
    device_int = cursor_int.fetchall()

    vpn_us = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in device_us]
    vpn_int = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in device_int]
    # print(type(vpn_us))
    # print(type(vpn_int))
    result = []
    vpn_us.extend(vpn_int)
    for myDict in vpn_us:
        if myDict not in result:
            result.append(myDict)

    result_vpn = ast.literal_eval(json.dumps(result))

    with open('/network/scripts/inventory/Input_Output/vpn.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for c in result_vpn:
            for k, v in c.items():
                writer.writerow([v])

def site_list_details():
    password = get_password()
    # connection to us-SQL
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor = conn_ussql.cursor()
    cursor.execute(
        """select distinct SITE as items from [dbo].[Nodes] where SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    device_us = cursor.fetchall()

    # connection to intl-SQL
    conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    cursor_int = conn_intsql.cursor()
    cursor_int.execute(
        """select distinct SITE as items from [NetPerfMonInt].[dbo].[Nodes] where SITE is not null and SITE != 'International' and SITE != 'Solarwinds-INTL' and SITE !=
'Netlab' and SITE != 'Solarwinds-US' and SITE != 'US';""")
    device_int = cursor_int.fetchall()

    site_us = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in device_us]
    site_int = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in device_int]
    result = []
    site_us.extend(site_int)
    for myDict in site_us:
        if myDict not in result:
            result.append(myDict)

    result_site = ast.literal_eval(json.dumps(result))
    time_field = {'@timestamp': now}
    type_field = {'type': "interactive_site_list"}
    network_device_type_field = {'network_device_type': "interactive_site"}
    for n in result_site:
        n.update(time_field)
        n.update(type_field)
        n.update(network_device_type_field)
    print("--------------------------------------------site_result----------------------------------------")
    keys = result_site[0].keys()

    with open('/network/scripts/inventory/Result/interactive_site_list.csv', 'wb') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(result_site)
    return result_site





if __name__ == "__main__":
    inventory_all = device_all()
    inventory_us = device_us()
    inventory_int = device_int()
    site_counts = site()
    ap_counts = airwave_ap()
    site_list_details = site_list_details()









