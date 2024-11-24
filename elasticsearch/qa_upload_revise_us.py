#!/opt/python-2.7.13/bin/python -u

from elasticsearch import Elasticsearch
import sys
import pyodbc
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from upload_functions import set_map, datetime_to_utc, get_password, get_password_ens
import MySQLdb

# create the object for elastic search
es = Elasticsearch(hosts=[{'host': 'snpstemp054', 'port': 9200}], timeout=400)

# find the current date
now = datetime.datetime.now()
now_str = now.strftime("%Y.%m.%d")

# set the index and type name (include datetime with index name)
index_name = 'network-interface-data' + '-' + now_str
type_name = 'interface-metrics'

# Mail settings to send error reports
me = 'preeraja@synopsys.com'
you = ['preeraja@synopsys.com', 'preeraja@synopsys']
print("mail settings success")

# connect to ens-db
pass_ens = get_password_ens()
conn_ens = MySQLdb.Connection(db='NHS_db', host='ens-db', user='winston', passwd=pass_ens)
cursor_ens = conn_ens.cursor()

# Start of Data from SolarWinds-US-SQL
# try-exception block to capture exceptions during db connection
try:
    # retrieve password for Solar Winds
    password = get_password()

    # connection to US-SQL
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)

    # cursor for the database
    cursor = conn_ussql.cursor()

    # query to extract all the interfaces, nodes which are active (Status=1), are of SNMP type.
    # script runs every 10 mins, so capture data for the last 11 mins keeping a min buffer
    cursor.execute("""SELECT DISTINCT a.NodeID, a.InterfaceID, a.In_Averagebps, a.Out_Averagebps, a.In_Maxbps,
    a.Out_Maxbps, a.In_Minbps, a.Out_Minbps, a.Timestamp, b.InterfaceName,
    b.InPercentUtil, b.OutPercentUtil, b.InDiscardsThisHour, b.InErrorsThisHour, b.OutDiscardsThisHour,
    b.OutErrorsThisHour, b.InterfaceSpeed, b.InBandwidth, b.OutBandwidth, b.InterfaceAlias, b.Interface_Tier_level,
    c.IP_Address, c.Caption, c.DNS, c.Site, c.Location, c.Node_Tier_Level, c.Asset_type, c.Site_ELK,
    c.PercentLoss, c.AvgResponseTime, c.CPULoad, c.PercentMemoryUsed
    FROM [NetPerfMonUS].[dbo].[InterfaceTraffic_CS_Detail] as a WITH (NOLOCK) 
    INNER JOIN [NetPerfMonUS].[dbo].[Interfaces] as b WITH (NOLOCK)
    ON a.NodeID = b.NodeID
    AND a.InterfaceID = b.InterfaceID
    INNER JOIN [NetPerfMonUS].[dbo].[Nodes] as c WITH (NOLOCK) 
    ON a.NodeID = c.NodeID
    WHERE b.Status = 1 AND a.Timestamp >= DATEADD(mi, -10, GETDATE()) AND c.Status = 1
    AND b.ObjectSubType = 'SNMP' and c.ObjectSubType = 'SNMP'""")

    # gather all data from Solarwinds-US-SQL
    result = cursor.fetchall()
    #print(result)
# catch the exception and send the error as-is
except Exception as e:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Error Report from Elastic Search'
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

# close cursor and database connection after data extraction
cursor.close()
conn_ussql.close()

# convert all the tuple info into dictionary
if result:
    # check if the number of interfaces received is <1000
    limit = 1000
    count = len(items)
    if count <= limit:

        # create the message to send report
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Error Report from Elastic Search'
        msg['From'] = me
        msg['To'] = ", ".join(you)
        text = "No. Of Entries from US-SQL (Interface) <=1000"
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)

        # check if connection to SMTP was succesful
        try:
            s = smtplib.SMTP('mailhost')
            print("Connected to SMTP")
            s.set_debuglevel(True)
            s.sendmail(me, you, msg.as_string())
            print("Sent E-Mail")
            s.quit()
        except smtplib.SMTPException as ex:
            print(ex)

    bulk_data = [] # create the list to upload data on ELK

    # go through all the items from the dictionary and process it for ELK upload
    for item in items:
        data_dict = item

        # set all the node data with 'node.' in front of the field names
        # also rename the fields as appropriate

        data_dict['node.nodeid'] = data_dict['nodeid']
        del data_dict['nodeid']

        data_dict['node.ip_address'] = data_dict['ip_address']
        del data_dict['ip_address']

        data_dict['node.network-node'] = data_dict['caption']
        del data_dict['caption']

        data_dict['node.dns'] = data_dict['dns']
        del data_dict['dns']

        data_dict['node.dc_site'] = data_dict['site']
        del data_dict['site']

        data_dict['node.snmp_location'] = data_dict['location']
        del data_dict['location']

        data_dict['node.node_tier_level'] = data_dict['node_tier_level']
        del data_dict['node_tier_level']

        data_dict['node.asset_type'] = data_dict['asset_type']
        del data_dict['asset_type']

        data_dict['node.packetloss'] = data_dict['percentloss']
        del data_dict['percentloss']

        data_dict['node.avgresponsetime'] = data_dict['avgresponsetime']
        del data_dict['avgresponsetime']

        data_dict['node.avgcpuload'] = data_dict['cpuload']
        del data_dict['cpuload']

        data_dict['node.memoryused'] = data_dict['percentmemoryused']
        del data_dict['percentmemoryused']

        data_dict['site'] = data_dict['site_elk']
        del data_dict['site_elk']

        # set all the interface data with 'interface.' in front of the field names
        # also rename the fields as appropriate

        data_dict['interface.interfaceid'] = data_dict['interfaceid']
        del data_dict['interfaceid']

        data_dict['interface.interfacename'] = data_dict['interfacename']
        del data_dict['interfacename']

        data_dict['interface.in_averagebps'] = data_dict['in_averagebps']
        del data_dict['in_averagebps']

        data_dict['interface.out_averagebps'] = data_dict['out_averagebps']
        del data_dict['out_averagebps']

        data_dict['interface.in_maxbps'] = data_dict['in_maxbps']
        del data_dict['in_maxbps']

        data_dict['interface.out_maxbps'] = data_dict['out_maxbps']
        del data_dict['out_maxbps']

        data_dict['interface.in_minbps'] = data_dict['in_minbps']
        del data_dict['in_minbps']

        data_dict['interface.out_minbps'] = data_dict['out_minbps']
        del data_dict['out_minbps']

        data_dict['interface.inpercentutil'] = data_dict['inpercentutil']
        del data_dict['inpercentutil']

        data_dict['interface.outpercentutil'] = data_dict['outpercentutil']
        del data_dict['outpercentutil']

        data_dict['interface.indiscardsthishour'] = data_dict['indiscardsthishour']
        del data_dict['indiscardsthishour']

        data_dict['interface.inerrorsthishour'] = data_dict['inerrorsthishour']
        del data_dict['inerrorsthishour']

        data_dict['interface.outdiscardsthishour'] = data_dict['outdiscardsthishour']
        del data_dict['outdiscardsthishour']

        data_dict['interface.outerrorsthishour'] = data_dict['outerrorsthishour']
        del data_dict['outerrorsthishour']

        data_dict['interface.interfacespeed'] = data_dict['interfacespeed']
        del data_dict['interfacespeed']

        data_dict['interface.inbandwidth'] = data_dict['inbandwidth']
        del data_dict['inbandwidth']

        data_dict['interface.outbandwidth'] = data_dict['outbandwidth']
        del data_dict['outbandwidth']

        data_dict['interface.rack_location'] = data_dict['interfacealias']
        del data_dict['interfacealias']

        data_dict['interface.interface_tier_level'] = data_dict['interface_tier_level']
        del data_dict['interface_tier_level']

        # below code is for world map, change as required. currently checking based on the first two
        # chars of data_dict['site'] and use country_code2 on grafana
        if data_dict['site']:
            ctry = data_dict['site'][:2].lower()
            if ctry == 'sd':
                crty = 'us'
            data_dict['geoip.country_code2'] = ctry

        # replacing dc_site with SAVVIS to BADC
        if data_dict['node.dc_site'] == 'SAVVIS':
            data_dict['node.dc_site'] = 'BADC'

        # convert datetime to UTC (datetime_to_utc() found in upload_functions.py file)

        if data_dict['timestamp']:
            #print(str(data_dict['timestamp']),type(data_dict['timestamp']))
            datetemp = str(data_dict['timestamp']).split(".")[0]
            datetemp1 = datetime.datetime.strptime(datetemp,'%Y-%m-%d %H:%M:%S')
            date_time = datetime_to_utc(datetemp1, code='us')
            data_dict['timestamp'] = str(date_time)
            if not "." in data_dict['timestamp']:
                data_dict['timestamp'] = data_dict['timestamp'] + ".000000"
            dt = data_dict['timestamp']

        data_dict['type'] = type_name  # include type exclusively since _type will be deprecated soon

        # remove .internal.synopsys.com from dns
        if data_dict['node.dns']:
            a = data_dict['node.dns'].split(".")
            data_dict['node.dns'] = a[0]

        # remove .internal.synopsys.com from network-node
        if data_dict['node.network-node']:
            d1 = data_dict['node.network-node'].split(".")
            data_dict['node.network-node'] = d1[0]
            d = d1[0]

        # checking the case where a/b has to be removed from the hostname to read lansweeper data
        i = str(data_dict['interface.interfacename'])
        if "/" in i:
            i1 = i.split("/")
            if len(i1) >2 and len(i1[0]) > 5:
                if d[-1] == 'a' or d[-1] == 'b':
                    d = d[:-1]
                # considering 'sig' in hostname
                elif d[-3:] == 'sig':
                    d = d[:-5]

        # lansweeper data from ens-db
        # try-exception block for ens-db (MySQL) connection (with dnsname)
        # first : check if the hostname matches with the dnsname (ideal scenario)
        try:
            cursor_ens.execute("""SELECT * FROM lansweeper_data WHERE dnsname like '{0}%'"""
                               .format(d))
            result_ls = cursor_ens.fetchall()
            ls_data1 = [dict(zip([key[0].lower() for key in cursor_ens.description], row)) for row in result_ls]
        except Exception as ep:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Error Report from Elastic Search'
            msg['From'] = me
            msg['To'] = ", ".join(you)
            text = "Connection to ens-db failed when checking with dnsname (Interface-US)" + "\n" + "Error: " + repr(ep)
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
            print(ep)

        if len(ls_data1) != 0:
            ls_data = ls_data1
        else:
            # check if the hostname matches with the assetname. Reason: When the dnsname is not managed in LS)
            # the information sometimes matches by treating the assetname as hostname
            try:
                # try-exception for ens-db with assetname
                cursor_ens.execute("""SELECT * FROM `lansweeper_data` WHERE `assetname` like '{0}%'"""
                                       .format(a[0]))
                result_ls = cursor_ens.fetchall()
                ls_data2 = [dict(zip([key[0].lower() for key in cursor_ens.description], row)) for row in result_ls]
                ls_data = ls_data2
            except Exception as ep:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'Error Report from Elastic Search'
                msg['From'] = me
                msg['To'] = ", ".join(you)
                text = "Connection to ens-db failed when checking with assetname (Interface-US) " + "\n" + "Error: " + repr(ep)
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
                print(ep)   

        # check if lansweeper has no data for the particular connected device
        if len(ls_data) == 0:
            # set value for lansweeper as 'NULL', since no combinations match
            data_dict['lansweeper.switch.dnsname'] = 'null'
            data_dict['lansweeper.if.description'] = 'null'
            data_dict['lansweeper.if.macaddress'] = 'null'
            data_dict['lansweeper.asset.macaddress'] = 'null'
            data_dict['lansweeper.hostname'] = 'null'
            data_dict['lansweeper.asset.ipaddress'] = 'null'
            data_dict['lansweeper.asset.iplocation'] = 'null'
            data_dict['lansweeper.asset.manufacturer'] = 'null'
            data_dict['lansweeper.asset.model'] = 'null'
            data_dict['lansweeper.asset.type'] = 'null'

        else:
            check = 0
            for ls in ls_data:
                # gather ens-db data for ELK upload
                # remove .internal.synopsys.com from dnsname
                if '.synopsys.com' in ls['dnsname']:
                    ls1 = ls['dnsname'].split(".")
                    data_dict['lansweeper.switch.dnsname'] = ls1[0]
                else:
                    data_dict['lansweeper.switch.dnsname'] = ls['dnsname']

                if i == ls['ifdescription']:
                    data_dict['lansweeper.if.description'] = ls['ifdescription']
                    data_dict['lansweeper.if.macaddress'] = ls['ifmacaddress']
                    data_dict['lansweeper.asset.macaddress'] = ls['assetmacaddress']
                    data_dict['lansweeper.hostname'] = unicode(ls['assetname'], 'utf8')
                    data_dict['lansweeper.asset.ipaddress'] = ls['ipaddress']
                    data_dict['lansweeper.asset.iplocation'] = ls['iplocation']
                    data_dict['lansweeper.asset.manufacturer'] = ls['assetmanufacturer']
                    data_dict['lansweeper.asset.model'] = ls['assetmodel']
                    data_dict['lansweeper.asset.type'] = ls['assettypename']
                    check = 1       # set check to 1 to know that details were retrieved from ens-db

            # if dnsname was found in ens-db but the connecting interface details are missing,
            # there's a chance that connecting device information exists in LS but is not associated
            # to the hostname correctly
            if check == 0:
                data_dict['lansweeper.if.description'] = 'null'
                data_dict['lansweeper.if.macaddress'] = 'null'
                data_dict['lansweeper.asset.macaddress'] = 'null'
                data_dict['lansweeper.hostname'] = 'null'
                data_dict['lansweeper.asset.ipaddress'] = 'null'
                data_dict['lansweeper.asset.iplocation'] = 'null'
                data_dict['lansweeper.asset.manufacturer'] = 'null'
                data_dict['lansweeper.asset.model'] = 'null'
                data_dict['lansweeper.asset.type'] = 'null'

        # create the structure to set index and type name
        op_dict = {
                    "index": {
                            "_index": index_name,
                            "_type": type_name,
                            }
                    }
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)
        
    # set the messages for log (can be found in qa_upload_us_log.log file)
    print('Bulk Data for US created (Interface)')
    print(now)
        


    # settings and mappings for solarwinds-us-sql data (found in upload_functions.py file)
    settings = set_map(code='us')

    # check if the index name exists, if yes then proceed with bulk upload, else create index before bulk upload
    if not es.indices.exists(index_name):
        # try-catch block to check if index was successfully created
        try:
            es.indices.create(index=index_name, body=settings)
            print('Created Index')
        except Exception as et:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Error Report from Elastic Search'
            msg['From'] = me
            msg['To'] = ", ".join(you)
            text = "Creating Index on Elasticsearch Failed (Interface - US)" + "\n" + "Error: " + repr(et)
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
            print(et)   

    # try-catch block to check if bulk upload onto Elasticsearch was successfull or not    
    try:    
        outcome = es.bulk(index=index_name, body=bulk_data)
        print('Uploaded to ES')
    except Exception as et:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Error Report from Elastic Search'
            msg['From'] = me
            msg['To'] = ", ".join(you)
            text = "Inserting on Elasticsearch Failed (Interface - US)" + "\n" + "Error: " + repr(et)
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
            print(et)

else:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Error Report from Elastic Search'
    msg['From'] = me
    msg['To'] = ", ".join(you)
    text = "No Result from SolarWinds-US-SQL" + "\n" + "Error: "
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
# End of Data from SolarWinds-US-SQL

