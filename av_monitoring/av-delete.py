#!/opt/python-2.7.13/bin/python -u
import os
import glob
import datetime
from datetime import date
from datetime import datetime
now = datetime.datetime.utcnow()
print(str(now)+" av-delete.py")
def Delete_Input():
    mydir = '/network/scripts/av_monitoring/Input'
    filelist = glob.glob(os.path.join(mydir, "*.txt"))
    for f in filelist:
        os.remove(f)
    print('----deleting AV Input folder----')

if __name__ == "__main__":
    Delete_Input()