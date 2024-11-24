#!/opt/python-2.7.13/bin/python -u

import requests
import os, sys
import json, ast
import subprocess
import threading
from datetime import date
from datetime import datetime
import datetime
from dateutil.tz import tzutc
import csv
import ast
now = datetime.datetime.utcnow()
print(str(now)+" av-crk-newfile.py")

def output_2_new_file():
    # Remove First two lines and last line  from the original output.txt file
    with open('/network/scripts/av_monitoring/Input/crk_output.json') as json_file:
        data = json.load(json_file)
        lines = data["items"]
        line = ast.literal_eval(json.dumps(lines))
        w = open("/network/scripts/av_monitoring/Input/crk_output1.txt", 'w')
        w.write('[')
        w.writelines([str(l) + "," for l in line])
        w.close()
    readFile = open("/network/scripts/av_monitoring/Input/crk_output1.txt")
    lines = readFile.readlines()
    readFile.close()
    w = open("/network/scripts/av_monitoring/Input/crk_output2.txt", 'w')
    w.writelines([sub[: -1] for sub in lines])
    w.write("]")
    w.close()



if __name__ == "__main__":
    output_2_new_file()