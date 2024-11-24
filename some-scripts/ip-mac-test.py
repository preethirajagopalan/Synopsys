import re
def ipcheck(g_ip):
    r_ip = "^(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])$"
    if re.search(r_ip,g_ip):
        print(g_ip + " is a match")
    else:
        print(g_ip + " is not a  match")
#01:12:25:4a:23:12
def mac_check(g_mac):
    r_mac = "^[0-9a-f]{2}([:-]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"

    if re.search(r_mac,g_mac):
        print("valid")
    else:
        print("not valid")
if __name__ == '__main__':
    ipcheck('10.20.30.1')
    ipcheck('500.20.1.2')
    ipcheck('250.200.45.200')
    mac_check("10:ab:cd:09:90:34")
    mac_check("452658912365")
    mac_check("a2:4d:1d:fs:98-09")