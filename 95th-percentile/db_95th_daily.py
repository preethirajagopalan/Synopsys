#!/opt/python-2.7.13/bin/python -u

import pkg_resources, imp, datetime, sys
import MySQLdb
import pyodbc, socket
import numpy

sys.path.append('/network/scripts/helper_classes')
from TimezoneHelpers import SynopsysSite
from EmailHelpers import send_mail

# log files and emails to send to
LOG_FILE = 'db_95th_daily.log'
EMAILS = ['preeraja@synopsys.com']
#print SynopsysSite

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
	Connects to the circuits and 95th databases within ens-db. Reads the data each site table in circuits, calculates the 95th percentile of each site for 
	the previous day, and writes the data to the 95th 1-day table.
	"""
	# connect to tables in ensdb
	conn_ensdb = MySQLdb.Connection(db='circuits', host='ens-db', user='winston', passwd='iltwas')
	cursor_ensdb = conn_ensdb.cursor()
	
	conn_95th = MySQLdb.Connection(db='95th', host='ens-db', user='winston', passwd='iltwas')
	cursor_95th = conn_95th.cursor()

	cursor_ensdb.execute('show tables')
	circuits = cursor_ensdb.fetchall()

	with open(LOG_FILE, 'w') as f:
		# loop through each table
		for circuit_info in circuits:
			# skip template
			circuit = circuit_info[0]
			if circuit == 'TEMPLATE':
				continue

			# find the name and circuit of the site
			split_index = circuit.rfind('_')
			site = circuit[:split_index]
			router_type = circuit[split_index + 1:]
			#print site

			# no data for this site
			if site == '1531':
				continue

			# Run for specific site
			#if site != 'GB14':
			#	continue

			# get site and current timezone
			site_info = SynopsysSite(site, file_obj=f)
			#print site_info
			timezone = site_info.get_timezone()
			if not timezone:
				continue

			# fetch data from yesterday
			today = datetime.datetime.now(tz=timezone).date()
			yesterday = today - datetime.timedelta(days=1)

			cursor_ensdb.execute("""SELECT * from `%s`
									WHERE date > '%s' AND date < '%s'
									""" % (circuit, yesterday, today))
			data = cursor_ensdb.fetchall()
			#print(today, yesterday)

			data_len = len(data)
			circuit = circuit.upper()
			if data_len == 0:
				report_error(f, 'No data for {0}.'.format(circuit))
				continue

			# sort by date
			data_date = sorted(data, key = lambda a: a[2])

			# date of bandwidth change
			bw_change = '0'

			# if oldest date and newest date have different bandwidth values
			if data_date[0][3] != data_date[-1][3]:
				# find when bandwidth changed
				for i in xrange(data_len - 1): 
					if data_date[i][3] != data_date[i + 1][3]:
						bw_change = data_date[i + 1][2]
						break

			# most recent bandwidth
			bandwidth = data_date[-1][3]

			# get the in and out data in 1D lists
			in_data = [float(cell[0]) for cell in data]
			out_data = [float(cell[1]) for cell in data]

			in_95 = numpy.percentile(in_data, 95)
			out_95 = numpy.percentile(out_data, 95)

			in_95_per = int(in_95 / bandwidth * 100)
			out_95_per = int(out_95 / bandwidth * 100)
			print site,",", router_type,",",bandwidth,"," ,in_95, ",",in_95_per,",",out_95, "," ,out_95_per

			# put it into 1day table
			cursor_95th.execute("""INSERT IGNORE into 1day 
										(sitecode,circuit,in_95,out_95,in_95_per,out_95_per,date,bw_change,bandwidth)
										VALUES ('%s','%s',%s,%s,%s,%s,'%s','%s',%s)
										""" % (site,router_type,in_95,out_95,in_95_per,out_95_per,yesterday,bw_change,bandwidth))

	# reopen for reading, sending to emails
	with open(LOG_FILE, 'r') as f:
		text = f.read()
		if text != '':
			send_mail(EMAILS, '95th Report {0}'.format(datetime.date.today()), text)
	#print site,router_type, in_95_per, out_95_per
