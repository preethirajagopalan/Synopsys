#!/opt/python-2.7.13/bin/python -u

from elasticsearch import Elasticsearch
import pyodbc
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loc_functions import set_map, get_password
import requests

# create the object for elastic search
es = Elasticsearch(hosts=[{'host': 'snpstemp054', 'port': 9200}], timeout=400)

# find the current date
now = datetime.datetime.now()
now_str = now.strftime("%Y.%m.%d")

# set the index and type name (include datetime with index name)
index_name = 'network-loc' + '-' + now_str
type_name = 'lookup'

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
    # connection to Int-SQL
    conn_intsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseuser;PWD=%s' % password)

    # cursors for the database
    cur_us = conn_ussql.cursor()
    cur_int = conn_intsql.cursor()

    # query to extract the Sites and Site Code from US-SQL
    cur_us.execute("""SELECT Caption, Asset_type, Site_ELK FROM [NetPerfMonUS].[dbo].[Nodes] WITH (NOLOCK) 
    WHERE ObjectSubType = 'SNMP' AND Site_ELK IS NOT NULL""")

    # fetch all data
    result_us = cur_us.fetchall()

    # query to extract the Sites and Site Code from Intl-SQL
    cur_int.execute("""SELECT Caption, Asset_type, Site_ELK FROM [NetPerfMonInt].[dbo].[Nodes] WITH (NOLOCK) 
    WHERE ObjectSubType = 'SNMP' AND Site_ELK IS NOT NULL AND Region NOT LIKE 'US'""")

    # fetch all data
    result_int = cur_int.fetchall()


# catch the exception and send the error as-is
except Exception as e:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Error Report from Elastic Search - Loc'
    msg['From'] = me
    msg['To'] = ", ".join(you)
    text = "Connection to US/Int SQL DB Failed" + "\n" + "Error: " + repr(e)
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
it_us = [dict(zip([key[0].lower() for key in cur_us.description], row)) for row in result_us]
it_int = [dict(zip([key[0].lower() for key in cur_int.description], row)) for row in result_int]

# close cursors and database connection after data extraction
cur_us.close()
cur_int.close()
conn_ussql.close()
conn_intsql.close()

# filter out duplicates
for int in it_int:
    if 'US' in int['site_elk'] or 'CA' in int['site_elk'] or 'CL' in int['site_elk']: 
        del int
    	



# collect all machines with incorrect site_elk field on solarwinds
incorrect = {} 

# convert all the tuple info into dictionary
if result_us or result_int:

    bulk_data = []  # create the list to upload data on ELK

    # go through all the items from US-SQL
    for it in it_us:
        data_dict = it

        if it['site_elk']:
            data_dict['site'] = it['site_elk']
            del data_dict['site_elk']
            data_dict['network-node'] = data_dict['caption']
            del data_dict['caption']	
            site_code = data_dict['site']
            r = requests.get('https://lookup.synopsys.com/api' + '/sites/code/' + site_code,
                             headers={'Authorization': 'Token token=' + token},
                             verify=cert)
            d = r.json()
	    if d['data']: 
	        lat =  str(d['data'][0]['latitude'])
	        lon = str(d['data'][0]['longitude']) 
                data_dict['geo'] = { 'location': lat + "," + lon }
                data_dict['city'] = d['data'][0]['city']
                data_dict['state'] = d['data'][0]['state']
                data_dict['datetime'] = str(now.utcnow())
                data_dict['type'] = type_name
                data_dict['asset_type'] = it['asset_type']

                ct = site_code[:2]
                if ct == 'HK':
                    ct = 'CN'
                data_dict['country_code2'] = ct
	    

         	op_dict = {
                    "index": {
                         "_index": index_name,

                         "_type": type_name,

                    }
                }

                bulk_data.append(op_dict)
                bulk_data.append(data_dict)

	    else:
	        incorrect.update({data_dict['network-node']: site_code})
	        del data_dict
        else:
            del data_dict












    
    # go through all the items from Intl-SQL
    for it in it_int:
        data_dict = it

        if it['site_elk']:
            data_dict['site'] = it['site_elk']
            del data_dict['site_elk']
	    data_dict['network-node'] = data_dict['caption']
            del data_dict['caption']
            site_code = data_dict['site']
            r = requests.get('https://lookup.synopsys.com/api' + '/sites/code/' + site_code,
                             headers={'Authorization': 'Token token=' + token},
                             verify=cert)
            d = r.json()

	    if d['data']: 
                data_dict['geo'] = { 'location': str(d['data'][0]['latitude'])+","+str(d['data'][0]['longitude']) }
                data_dict['city'] = d['data'][0]['city']
                data_dict['state'] = d['data'][0]['state']
                data_dict['datetime'] = str(now.utcnow())
                data_dict['type'] = type_name
                data_dict['asset_type'] = it['asset_type']

                ct = site_code[:2]
                if ct == 'HK':
                    ct = 'CN'
                data_dict['country_code2'] = ct
                op_dict = {
                     "index": {
                         "_index": index_name,
                         "_type": type_name,
    
                         }
                      }

                bulk_data.append(op_dict)
                bulk_data.append(data_dict)

            else:
	        incorrect.update({data_dict['network-node']: site_code})
                del data_dict
        else:
	    del data_dict
        
	 



                   
   







    # set the messages for log (can be found in log file)
    print('Bulk Data Created for Location')
    print(now)
    if incorrect:
    # send email with the list of incorrect site codes
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Error  Report from Elastic Search-Loc'
        msg['From'] = me
        msg['To'] = ", ".join(you)
        inc = "Switch and its corresponding Site_ELK on Solarwinds\n"
        for i in incorrect:
            inc = inc + "\n" + "Network-Node: " + str(i) + "\t" + "Site_ELK: " + str(incorrect[i]) 

        text = str(inc)
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
    

    # settings and mappings for fex/switch metrics (found in loc_functions.py file)
    settings = set_map()

    # check if the index name exists, if yes then proceed with bulk upload, else create index before bulk upload
    if not es.indices.exists(index_name):
        # try-catch block to check if index was successfully created
        try:
            es.indices.create(index=index_name, body=settings)
            print('Created Index')
        except Exception as et:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Error Report from Elastic Search-Loc'
            msg['From'] = me
            msg['To'] = ", ".join(you)
            text = "Creating Index on Elasticsearch Failed (Location)" + "\n" + "Error: " + repr(et)
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
        print("Upload onto ES-Locations Done")
    except Exception as et:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Error Report from Elastic Search-Loc'
        msg['From'] = me
        msg['To'] = ", ".join(you)
        text = "Inserting on Elasticsearch Failed (Location)" + "\n" + "Error: " + repr(et)
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
    msg['Subject'] = 'Error Report from Elastic Search-Loc'
    msg['From'] = me
    msg['To'] = ", ".join(you)
    text = "No Result from SQL" + "\n" + "Error: "
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
        
        
