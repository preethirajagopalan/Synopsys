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
now = datetime.datetime.utcnow()


def ipsla():
    password = get_password()
    # connection to US-SQL
    conn_ussql = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;'
                                'SERVER=10.200.17.64;PORT=1433;UID=SolarWindsOrionDatabaseUser;PWD=%s' % password)
    # cursor for the database
    cursor = conn_ussql.cursor()
    print("done")

    cursor.execute(
        """SELECT [NetPerfMonUS].[dbo].[VoipOperationResults].[VoipOperationInstanceID] , [NetPerfMonUS].[dbo].[VoipOperationResults].[AvgRoundTripTime], 
[NetPerfMonUS].[dbo].[VoipOperationResults].[DateTime], [NetPerfMonUS].[dbo].[VoIPOperationNames].[Source],
[NetPerfMonUS].[dbo].[VoIPOperationNames].[Target] FROM [NetPerfMonUS].[dbo].[VoipOperationResults] 
join [dbo].[VoIPOperationNames] on [NetPerfMonUS].[dbo].[VoipOperationResults].[VoipOperationInstanceID] = [NetPerfMonUS].[dbo].[VoIPOperationNames].[VoipOperationInstanceID]
where [NetPerfMonUS].[dbo].[VoIPOperationNames].[Source] = 'dc2-c6807-core.internal.synopsys.com' 
and [NetPerfMonUS].[dbo].[VoIPOperationNames].[Target] = 'ca06-vpn-router.internal.synopsys.com'
group by 
[NetPerfMonUS].[dbo].[VoIPOperationNames].[Source],[NetPerfMonUS].[dbo].[VoIPOperationNames].[Target], [NetPerfMonUS].[dbo].[VoipOperationResults].[VoipOperationInstanceID],
[NetPerfMonUS].[dbo].[VoipOperationResults].[AvgRoundTripTime], [NetPerfMonUS].[dbo].[VoipOperationResults].[DateTime];""")

    # gather all data from Solarwinds-US-SQL
    result_us = cursor.fetchall()

    # gather all data from Solarwinds-US-SQL
    result_us = cursor.fetchall()

    r_us = [dict(zip([key[0].lower() for key in cursor.description], row)) for row in result_us]

    json_us = ast.literal_eval(json.dumps(r_us))
    print(json_us)

if __name__ == "__main__":
    ipsla_all = ipsla()

