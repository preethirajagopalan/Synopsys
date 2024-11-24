#!/opt/python-2.7.13/bin/python -u
# Gathers interface utilization data from solarwinds sql database and stores it in ens-db circuits database

import sys, pkg_resources, imp
import MySQLdb
import pyodbc, socket, smtplib
from warnings import filterwarnings
import MySQLdb as Database
import datetime

sys.path.append('/network/scripts/helper_classes')
from TimezoneHelpers import SynopsysSite
from EmailHelpers import send_mail

filterwarnings('ignore', category = Database.Warning)

# log file and emails to send reports to
LOG_FILE = 'db_grab_data.log'
EMAILS = ['preeraja@synopsys.com']

def report_error(file_obj, message):
	"""
	Prints message to console and writes message to given file object.
	:type file_obj: file
	:type message: string
	:rtype: void
	"""
	print message
	file_obj.write('{0}\n'.format(message))


if __name__ == '__main__':
	"""
	Connects to Solarwinds and ens-db databases. Grabs data from Solarwinds regarding utilization and bandwidth, and inserts parsed rows into the corresponding
	table for the site in ens-db circuits. Creates the table using the circuit type and site name if the table does not currently exist in the circuits database.
	"""

	# Connect to solarwinds-us database
	conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseuser;PWD=fsck16')
	cursor_ussql = conn_ussql.cursor()

	# Connect to solarwinds-intl database
	conn_intlsql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;SERVER=10.225.16.15;PORT=1433;UID=SolarWindsOrionDatabaseuser;PWD=fsck16')
	cursor_intlsql = conn_intlsql.cursor()

	# Connect to ens-db database
	conn_ensdb = MySQLdb.Connection(db='mice', host='ens-db', user='winston', passwd='iltwas')
	cursor_ensdb = conn_ensdb.cursor()

	conn_ensdb2= MySQLdb.Connection(db='circuits', host='ens-db', user='winston', passwd='iltwas')
	cursor_ensdb2 = conn_ensdb2.cursor()

	# open up file
	with open(LOG_FILE, 'w') as f:

		cursor_ensdb.execute("SELECT interfaceid, server, site, service from services")	
		circuit_info = cursor_ensdb.fetchall()

		# stores the last site and offset to prevent repetitive creation of SynopsysSite 
		last_site = None
		offset = None
	
		# sort by site
		for row in sorted(circuit_info, key = lambda entry : entry[2]):
			interface_id, server, site, service = row
			site = site.upper()
		#print site	
			if site == '1531':
				continue

			# To test a specific site
			#if site != 'CA06':
			#	continue
			# print site
			# print last_site
			# new site, have to get information about offset
			if site != last_site:
				site_info = SynopsysSite(site, file_obj=f)
				offset = site_info.get_offset()
				#print(offset)

				# set new site
				last_site = site
			
			if offset == None:
				continue

			# determine correct variables to use
			if server == 'solarwinds-intl':
				perf_name = 'NetPerfMonInt'
				cursor = cursor_intlsql
				euinfo = SynopsysSite('DE02', file_obj=f)
				# offset for local time solarwinds-us
				newoffset = euinfo.get_offset()
			else:
				perf_name = 'NetPerfMonUS'
				cursor = cursor_ussql
				usinfo = SynopsysSite('US02', file_obj=f)
				# offset for local time solarwinds-intl
				newoffset = usinfo.get_offset()

			offset[0] = offset[0] - newoffset[0]
			offset[1] = offset[1] - newoffset[1]

			# correct the UTC times by adding offset
			corrected_date = 'DATEADD(HH, {0}, DATEADD(MI, {1}, TimeStamp))'.format(offset[0], offset[1])
			cursor_ensdb2.execute("""
				CREATE TABLE if not exists `%s_%s` LIKE TEMPLATE
				""" % (site, service))

			# get work day / hour information
			query = """
				SELECT In_Averagebps, Out_Averagebps, {0}
				FROM [{1}].[dbo].[InterfaceTraffic_CS_Detail]

				WHERE DATEPART(dw, {0}) != '1' and DATEPART(dw, {0}) != '7'
				and DATEPART(hh, {0}) > 8 and DATEPART(hh, {0}) < 19

				and InterfaceID = {2}
				""".format(corrected_date, perf_name, interface_id)

			#print query

			cursor.execute(query)
			sql_circuit = cursor.fetchall()

			# get bandwidth information
			cursor.execute("""
                SELECT InBandwidth FROM [%s].[dbo].[Interfaces]
                WHERE InterfaceID = %s
                """ % (perf_name, interface_id))
			bandwidth = cursor.fetchone()			

			# check that data exists
			num_entries = len(sql_circuit)
			if num_entries == 0:
				report_error(f, '{0} {1} circuit (id {2}) has no bps data. Please check!'.format(site, service, interface_id))
				continue

			if bandwidth == None:
				report_error(f, '{0} {1} circuit (id {2}) has no bandwidth info. Please check!'.format(site, service, interface_id))
				continue

			# insert data into ens-db circuits table
			for i in range(num_entries):
				inbps = sql_circuit[i][0]
				outbps = sql_circuit[i][1]

				if inbps != None and outbps != None:
					cursor_ensdb2.execute("""
						INSERT IGNORE into `%s_%s` (inbps,outbps,date,bandwidth) 
						VALUES (%s,%s,'%s',%f)
						""" % (site, service, inbps, outbps, sql_circuit[i][2], bandwidth[0]))	

	# reopen file for reading, send email
	with open(LOG_FILE, 'r') as f:
		text = f.read()
		if text != '':
			send_mail(EMAILS, 'Grab Data Report {0}'.format(datetime.date.today()), text)
	
