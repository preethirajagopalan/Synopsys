#!/opt/python-2.7.13/bin/python -u

from elasticsearch import Elasticsearch
import pyodbc
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from node_functions import set_map, get_password
import requests

# create the object for elastic search
es = Elasticsearch(hosts=[{'host': 'snpstemp054', 'port': 9200}], timeout=400)

# find the current date
now = datetime.datetime.now()
now_str = now.strftime("%Y.%m.%d")

# set the index and type name (include datetime with index name)
index_name = 'network-nodes' + '-' + now_str
type_name = 'switch-metrics'

# Mail settings to send error reports
me = 'preeraja@synopsys.com'
you = ['preeraja@synopsys.com', 'preeraja@synopsys']
print("mail settings success")

# defining the parameters for gathering loc. info from lookup
token = '865668c5-56c9-434b-be50-875cabfce3b5'
cert = '/etc/ssl/certs/ca-bundle.crt'

# Start of Data from SolarWinds-US-SQL
# try-exception block to capture exceptions during db connection
try:
    # retrieve password for Solar Winds
    password = get_password()

    # connection to US-SQL
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)

    # cursors for the database
    cursor = conn_ussql.cursor()
    cur_1 = conn_ussql.cursor()

    # query to extract flex details along with metrics like temp. 
    cursor.execute("""SELECT a.Caption, a.Vendor, a.IOSVersion, a.MachineType,
                        a.Asset_type, a.Site_ELK,
                        b.Manufacturer, b.Model, b.ServiceTag,
                        c.SensorDisplayName, c.SensorValue
                        FROM [NetPerfMonUS].[dbo].[Nodes] as a WITH (NOLOCK)
                        INNER JOIN [NetPerfMonUS].[dbo].[HWH_HardwareInfo] as b WITH (NOLOCK) 
                        ON a.NodeID = b.ID
                        INNER JOIN [NetPerfMonUS].[dbo].[APM_HardwareSensorAlertData] as c WITH (NOLOCK) 
                        ON a.NodeID = c.NodeID
                        WHERE c.CategoryName = 'Temperature' and c.SensorDisplayName like '%s'
                        """ % ('Fex'+'%'))

    # gather all data from Fex metrics
    result = cursor.fetchall()

    # query to extract metrics of the switch details along with metrics like temp.
    cur_1.execute("""SELECT a.Caption, a.Vendor, a.IOSVersion, a.MachineType,
                        a.Asset_type, a.Site_ELK,
                        b.Manufacturer, b.Model, b.ServiceTag,
                        c.SensorDisplayName, c.SensorValue
                        FROM [NetPerfMonUS].[dbo].[Nodes] as a WITH (NOLOCK) 
                        INNER JOIN [NetPerfMonUS].[dbo].[HWH_HardwareInfo] as b WITH (NOLOCK) 
                        ON a.NodeID = b.ID
                        INNER JOIN [NetPerfMonUS].[dbo].[APM_HardwareSensorAlertData] as c WITH (NOLOCK) 
                        ON a.NodeID = c.NodeID
                        WHERE c.CategoryName = 'Temperature' AND c.SensorDisplayName like '%s'
                        OR c.SensorDisplayName like '%s'""" % ('%'+'Fan'+'%', '%'+'Port'+'%'))

    # gather all data for Switch metrics
    res_1 = cur_1.fetchall()

# catch the exception and send the error as-is
except Exception as e:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Error Report from Elastic Search'
    msg['From'] = me
    msg['To'] = ", ".join(you)
    text = "Connection to US-Sql Database Failed (Nodes)" + "\n" + "Error: " + repr(e)
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

# convert tuples to dictionaries
items = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result]

it_1 = [dict(zip([key[0].lower() for key in cur_1.description], row)) for row in res_1]

# close cursors and database connection after data extraction
cursor.close()
cur_1.close()
conn_ussql.close()

# convert all the tuple info into elastic dictionary
#convert solarwinds dictionary output to elastic search list
if result or res_1:
    # check if the number of interfaces received is <100
    limit = 100
    count = len(items)
    if count <= limit:

        # create the message to send report
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Error Report from Elastic Search'
        msg['From'] = me
        msg['To'] = ", ".join(you)
        text = "No. Of Entries from US-SQL <=100 (Nodes)"
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

    # go through all the items from fex dictionary and upload onto ELK
    for item in items:
        data_dict = item

        data_dict['node.network-node'] = data_dict['caption']
        del data_dict['caption']

        data_dict['node.vendor'] = data_dict['vendor']
        del data_dict['vendor']

    
        ios = str(data_dict['iosversion']).split(",") 
	data_dict['node.iosversion'] = ios[0]




	del data_dict['iosversion'] 





        data_dict['node.machinetype'] = data_dict['machinetype']
        del data_dict['machinetype']

        data_dict['node.asset_type'] = data_dict['asset_type']
        del data_dict['asset_type']

        data_dict['node.manufacturer'] = data_dict['manufacturer']
        del data_dict['manufacturer']

        data_dict['node.model'] = data_dict['model']
        del data_dict['model']

        data_dict['node.servicetag'] = data_dict['servicetag']
        del data_dict['servicetag']

        data_dict['node.sensorvalue'] = data_dict['sensorvalue']
        del data_dict['sensorvalue']

        data_dict['node.sensordisplayname'] = data_dict['sensordisplayname']
        del data_dict['sensordisplayname']

        data_dict['site'] = data_dict['site_elk']
        del data_dict['site_elk']

        # below code is for world map, change as required. currently checking based on the first two
        if data_dict["site"]:

            site_code = data_dict["site"]
            r = requests.get('https://lookup.synopsys.com/api' + '/sites/code/' + site_code,
                headers={'Authorization': 'Token token=' + token},
                verify=cert)
            d = r.json()


            data_dict['geoip.city'] = d['data'][0]['city']
            data_dict['geoip.state'] = d['data'][0]['state']
            st = site_code[:2] 
	    data_dict['geoip.country_code2'] = st 



        # capture fexname
        s = data_dict['node.sensordisplayname']
        s1 = s.split(" ")
        data_dict['node.fexname'] = s1[0]

        # convert datetime to UTC (datetime_to_utc() found in upload_functions.py file)
        date_time = str(now.utcnow())
        data_dict['datetime'] = date_time

        data_dict['type'] = type_name  # include type exclusively since _type will be deprecated soon

        # remove .internal.synopsys.com from network-node
        if data_dict['node.network-node']:
            d1 = data_dict['node.network-node'].split(".")
            data_dict['node.network-node'] = d1[0]
            d = d1[0]

        # field for counting devices in DC
        if data_dict['node.asset_type'] == 'DC': 
	    data_dict['key.device'] = d + "+" + s1[0]
        else:
	    data_dict['key.device'] = d

        # create the structure to set index and type name
        op_dict = {
                    "index": {

                            "_index": index_name,
                            "_type": type_name,
                            }
                    }
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)

    # set the messages for log (can be found in qa_node_us_log.log file)
    print('Bulk Data for US-Node created')
    print(now)

    # settings and mappings for fex/switch metrics (found in node_functions.py file)
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
            text = "Creating Index on Elasticsearch Failed (Node-US)" + "\n" + "Error: " + repr(et)
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
        print("Upload onto ES-US node done")
    except Exception as et:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Error Report from Elastic Search'
            msg['From'] = me
            msg['To'] = ", ".join(you)
            text = "Inserting on Elasticsearch Failed (Node-US)" + "\n" + "Error: " + repr(et)
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

    # -------- Switch Metrics Section Below ------------ #

    # loop over switch metrics
    bulk_data = []

    for it in it_1:
        data_dict = it

        data_dict['node.network-node'] = data_dict['caption']
        del data_dict['caption']

        data_dict['node.vendor'] = data_dict['vendor']
        del data_dict['vendor']

 	ios = str(data_dict['iosversion']).split(",")	
        data_dict['node.iosversion'] = ios[0] 
        del data_dict['iosversion']

        data_dict['node.machinetype'] = data_dict['machinetype']
        del data_dict['machinetype']

        data_dict['node.asset_type'] = data_dict['asset_type']
        del data_dict['asset_type']

        data_dict['node.manufacturer'] = data_dict['manufacturer']
        del data_dict['manufacturer']

        data_dict['node.model'] = data_dict['model']
        del data_dict['model']

        data_dict['node.servicetag'] = data_dict['servicetag']
        del data_dict['servicetag']

        data_dict['node.sensorvalue'] = data_dict['sensorvalue']
        del data_dict['sensorvalue']

        data_dict['node.sensordisplayname'] = data_dict['sensordisplayname']
        del data_dict['sensordisplayname']

        data_dict['site'] = data_dict['site_elk']
        del data_dict['site_elk']

        # below code is for world map, change as required. currently checking based on the first two
        if data_dict["site"]:

            site_code = data_dict["site"]
            r = requests.get('https://lookup.synopsys.com/api' + '/sites/code/' + site_code,
                headers={'Authorization': 'Token token=' + token},
                verify=cert)
            d = r.json()


            data_dict['geoip.city'] = d['data'][0]['city']
            data_dict['geoip.state'] = d['data'][0]['state']
            data_dict['geoip.country_code2'] = d['data'][0]['country']

        # capture sensor name
        s = data_dict['node.sensordisplayname']
        s1 = s.split(" ")
        data_dict['node.fexname'] = s1[0]

        # convert datetime to UTC (datetime_to_utc() found in upload_functions.py file)
        date_time = str(now.utcnow())
        data_dict['datetime'] = date_time

        data_dict['type'] = type_name  # include type exclusively since _type will be deprecated soon

        # remove .internal.synopsys.com from network-node
        if data_dict['node.network-node']:
            d1 = data_dict['node.network-node'].split(".")
            data_dict['node.network-node'] = d1[0]
            d = d1[0]

        # field for counting devices in DC
        data_dict['key.device'] = d + "+" + s1[0]

        # create the structure to set index and type name
        op_dict = {
                    "index": {

                            "_index": index_name,
                            "_type": type_name,
                            }
                    }
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)


    # set the messages for log (can be found in qa_node_us_log.log file)
    print('Bulk Data for US-Node created')
    print(now)



    # settings and mappings for fex/switch metrics (found in node_functions.py file)
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
            text = "Creating Index on Elasticsearch Failed (Node-US)" + "\n" + "Error: " + repr(et)
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
        print("Upload onto ES-US node done")
    except Exception as et:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Error Report from Elastic Search'
            msg['From'] = me
            msg['To'] = ", ".join(you)
            text = "Inserting on Elasticsearch Failed (Node-US)" + "\n" + "Error: " + repr(et)
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
    text = "No Result from SolarWinds-US-SQL (Node)" + "\n" + "Error: "
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




