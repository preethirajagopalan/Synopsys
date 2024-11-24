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
import csv

class Site:


    def site(self):
        password = get_password()


    # connection to US-SQL
        conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                    'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
        # cursor for the database
        cursor = conn_ussql.cursor()

        cursor.execute(
            """select distinct SITE as Site_Count from [dbo].[Nodes] where SITE is not null;""")
        # gather all data from Solarwinds-US-SQL
        result_us = cursor.fetchall()


        #print(result_us, result_int)
        r_us = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result_us]
        return r_us
myobjectx = Site()
print(myobjectx.r_us)



