#!/opt/python-2.7.13/bin/python -u

import pkg_resources, imp, datetime, sys
import MySQLdb
import pyodbc, socket


conn_95th = MySQLdb.Connection(db='95th', host='ens-db', user='winston', passwd='iltwas')
cursor_95th = conn_95th.cursor()

cursor_95th.execute("SELECT * from 1day WHERE sitecode='US95' and circuit='VPN'")
data = cursor_95th.fetchall()

for each in data:
	site,circuit,in_95,out_95,in_95_per,out_95_per,date,bw_ch,bw=each[0],each[1],each[2],each[3],each[4],each[5],each[6],each[7],each[8]

	new_in_95_per = int(in_95/bw*100)
	new_out_95_per = int(out_95/bw*100)

	print new_in_95_per,new_out_95_per

	cursor_95th.execute("""UPDATE 1day SET in_95_per=%s, out_95_per=%s WHERE
									sitecode='%s' and circuit='%s' and date='%s'
									""" % (new_in_95_per,new_out_95_per,site,circuit,date))
