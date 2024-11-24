#!/opt/python-2.7.13/bin/python -u

import re
mac_regex = "^[0-9a-f]{2}([:-]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"

def mac_check(mac):
    mac = mac.lower()
    if re.search(mac_regex,mac):
        print(mac,"valid mac")
    else:
        print(mac,"unvalid")

if __name__ == '__main__':
    mac_check("00:29:15:80:4E:4A")
    mac_check("00:29:804E4A")
    mac_check("00:29:80:4S:4A")