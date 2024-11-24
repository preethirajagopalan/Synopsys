#!/opt/python-2.7.13/bin/python -u

import socket
with open('output.txt') as f:
    for ip in f:
        out = socket.getaddrinfo(ip, 0)
        print(out)