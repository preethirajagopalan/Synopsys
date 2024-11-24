# #!/opt/python-2.7.13/bin/python -u
import pytz, datetime
now = datetime.datetime.now()
print(now)
def timefunc(a):
    local = pytz.timezone ("America/Los_Angeles")
    #a = dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f")
    naive = datetime.datetime.strptime (a, "%Y-%m-%d %H:%M:%S.%f")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    time = utc_dt.strftime ("%Y-%m-%d %H:%M:%S.%f")
    return time
# #!/opt/python-2.7.13/bin/python -u
import pytz, datetime

def timefunc_cet(a):
    local = pytz.timezone ("CET")
    #a = dateutil.parser.parse(x['datetime']).strftime("%Y-%m-%d %H:%M:%S.%f")
    naive = datetime.datetime.strptime (a, "%Y-%m-%d %H:%M:%S.%f")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    time = utc_dt.strftime ("%Y-%m-%d %H:%M:%S.%f")
    return time


