#!/opt/python-2.7.13/bin/python -u
import requests
import calendar
import datetime
start_time = datetime.datetime.utcnow() - datetime.timedelta(1)
start = calendar.timegm(start_time.utctimetuple()) * 1000

end_time = datetime.datetime.utcnow()
end = calendar.timegm(end_time.utctimetuple()) * 1000

url='https://liveaction:8093/v1/reports/flow/59/runTimeSeries.csv?startTime={}&endTime={}&direction=both&&&&&flexSearch=flow.ip%3D13.107.6.152%2F31%7C%20flow.ip%3D13.107.18.10%2F31%7C%20flow.ip%3D13.107.128.0%2F22%7C%20flow.ip%3D23.103.160.0%2F20%7C%20flow.ip%3D40.96.0.0%2F13%7C%20flow.ip%3D40.104.0.0%2F15%7C%20flow.ip%3D52.96.0.0%2F14%7C%20flow.ip%3D131.253.33.215%2F32%7C%20flow.ip%3D132.245.0.0%2F16%7C%20flow.ip%3D150.171.32.0%2F22%7C%20flow.ip%3D191.234.140.0%2F22%7C%20flow.ip%3D204.79.197.215%2F32&&&businessHours=none&binDuration=auto&topAnalysisDisplayType=bytes&useFastLane=false'.format(start, end)

headers = {'Authorization': 'Bearer QI7dXQyCMcDOL0oubfLVhzrFc0E2jfb7pSdp/m58nmk=', 'Content-Type':'text/csv'}

response = requests.get(url, headers, verify=False)

print(response.status_code)
print(response.text)