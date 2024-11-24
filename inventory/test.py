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
#from airwave_api import ap_count
import csv
now = datetime.datetime.utcnow()
#site_list = []

class site_class_test:

    def __init__(self, q=None):
        self.site_list = []
        self.q = q

    def site(self):
        print('hi', self.q)
        password = get_password()
        # connection to US-SQL
        conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                 'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
        # cursor for the database
        cursor = conn_ussql.cursor()
        cursor.execute(
            """select count (distinct SITE) as Site_Count from [dbo].[Nodes] where SITE is not null;""")
        # gather all data from Solarwinds-US-SQL
        result_us = cursor.fetchall()
        #print(result_us, result_int)
        r_us = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result_us]
        json_us = ast.literal_eval(json.dumps(r_us))
        for x in json_us:
            self.q = x.values()[0]
        us = {'type':'site','total items': self.q, 'network_device_type': 'site_count_us'}
        time_field = {'@timestamp': now}
        self.site_list.append(us)
        for b in self.site_list:
            b.update(time_field)
        keys = self.site_list[0].keys()
        with open('/network/scripts/inventory/Result/site_list_test.csv', 'wb') as csv_file:
            dict_writer = csv.DictWriter(csv_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.site_list)
        return self.site_list

if __name__ == "__main__":
    print('starting')
    classobject = site_class_test()
    classobject.site()
    print(classobject.q)
    print(classobject.site_list)
    print('ending')