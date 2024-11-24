#!/opt/python-2.7.13/bin/python -u

#250 to 255
#200 to 249
#0 to 199
#0a:0b:0c:1d:2e:fg

import re
regex_pattern = "^(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])$"
regex_mac_pattern = "^[0-9a-f]{2}([:-]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"

def check(ip):
    if re.search(regex_pattern,ip):
        print("valid IPv4")
    else:
        print("not valid IPv4")

def mac_check(mac):
    mac = mac.lower()
    if re.search(regex_mac_pattern, mac):
        print(mac, "its a mac address")
    else:
        print(mac, "its not a valid mac address")


if __name__  == '__main__':
    check("110.234.52.124")
    check("192.68.0.1")
    check("1.4.68.1")
    mac_check("01234abcde56")
    mac_check("00:29:15:80:4E:4A")
    mac_check("01-23-4f-gh-AS-56")
