#!/opt/python-2.7.13/bin/python -u
# -*- coding: utf-8 -*-
# code to collect data from lansweeper and store into ens-db
# Brief Description: As of now, it was found best to retrieve all data from lansweeperdb based on the combination
# mentioned in the SQL query. There were multiple mismatch in terms of hostname/dnsname between LS & SW due to which
# it's best to gather all and then derive a pattern match in the 11m script

import pyodbc
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import MySQLdb
from upload_functions import get_password, get_password_ls
import datetime

# Mail settings to send error reports
me = 'preeraja@synopsys.com'
you = ['preeraja@synopsys.com', 'preeraja@synopsys']
msg = MIMEMultipart('alternative')
msg['Subject'] = 'The contents of lansweeper file'
msg['From'] = me
msg['To'] = ", ".join(you)
print("Mail settings for lansweeper error report were set")

# datetime now
now = datetime.datetime.now()

# Start of Data from Lansweeper
# start of try-catch block for lansweeperdb
try:
    # retrieve password for lansweeperdb
    pass_ls = get_password_ls()

    # connect to Lansweeper DB
    conn_ls = pyodbc.connect(
        'Driver=/usr/lib64/libtdsodbc.so.0;Server=10.12.237.187;PORT=1433;'
        'Database=lansweeperdb;UID=Lansweeper;PWD=%s' % pass_ls)

    # create cursor for lansweeperdb
    cursor_ls = conn_ls.cursor()

    # retrieve data from Lansweeper for all Assets
    cursor_ls.execute("""SELECT DISTINCT a.AssetName as dnsname, b.IfDescription, b.IfMacaddress,
    c.AssetMacAddress, d.AssetName, d.IPAddress, d.AssetID, e.IPLocation, f.AssetTypename, g.Model, g.Manufacturer
    from [lansweeperdb].[dbo].[tblAssets] as a
    inner join [lansweeperdb].[dbo].[tblSNMPInfo] as b on a.AssetID = b.AssetID
    inner join [lansweeperdb].[dbo].[tblSNMPAssetMac] as c on b.IfIndex = c.IfIndex and b.AssetID = c.AssetID
    inner join [lansweeperdb].[dbo].[tblAssets] as d on c.AssetMacAddress = d.Mac
    inner join [lansweeperdb].[dbo].[tsysIPLocations] as e on d.LocationID = e.LocationID
    inner join [lansweeperdb].[dbo].[tsysAssetTypes] as f on d.Assettype = f.AssetType
    inner join [lansweeperdb].[dbo].[tblAssetCustom] as g on d.AssetID = g.AssetID""")

# capture the exception and send the error as-is
except Exception as e:
    text = "Connection to Lansweeper Failed" + repr(e)
    part1 = MIMEText(text, 'plain')
    msg.attach(part1)
    print(repr(e))

# fetchall based on the SQL query mentioned above
result_ls = cursor_ls.fetchall()
items_ls = [dict(zip([key[0].lower() for key in cursor_ls.description], row)) for row in result_ls]
# delete entries with empty interface description
for item in items_ls:
    if item['ifdescription'] is '' or item['ifdescription'] is None:
        del item

# store data from lansweeper onto the lansweeper_data table in NHS_db
# start of try-catch block for ens-db
try:
    # connection string to connect to ens-db
    conn_ens = MySQLdb.Connection(db='NHS_db', host='ens-db', user='winston', passwd='iltwas')

    # cursor to ens-db
    cursor_ens = conn_ens.cursor()

    # based on the test cases, it was found best to delete all entries from lansweeper_data, to accomodate
    # cases where the dns no longer exists in lansweeperdb
    cursor_ens.execute("""DELETE FROM lansweeper_data""")

# catch any exception and send the error as-is
except Exception as ec:
    text = "Connection to ens-db failed during clearing of ens-db" + repr(ec)
    part1 = MIMEText(text, 'plain')
    msg.attach(part1)
    print(repr(ec))


# insert all data retrieved from SQL query mentioned above onto ens-db
for item in items_ls:
    dnsnm = str(item['dnsname'].encode('utf-8'))
    ifdes = str(item['ifdescription'].encode('utf-8'))
    ifmac = str(item['ifmacaddress'])
    assetmac = str(item['assetmacaddress'])

    assetname = str(item['assetname'].encode('utf-8'))
    assetip = str(item['ipaddress'])
    assetloc = str(item['iplocation'])
    assettypename = str(item['assettypename'])

    assetmanufacturer = str(item['manufacturer'])
    assetmodel = str(item['model'])

    # start of try-catch block to insert data onto ens-db
    try:
        cursor_ens.execute("""INSERT INTO lansweeper_data(dnsname, ifdescription, ifmacaddress,
        assetmacaddress, assetname, ipaddress, iplocation, assettypename, assetmanufacturer, assetmodel)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (dnsnm, ifdes, ifmac, assetmac, assetname, assetip, assetloc, assettypename,
                            assetmanufacturer, assetmodel))

    # exception to handle failed insertion of data
    except Exception as exp:
        text = "Insert into ens-db not successful" + repr(exp)
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        print(repr(exp))

# for log purposes, display the following
print("Insert into ens-db (lansweeper_data table) was done at: ")
print(now)
