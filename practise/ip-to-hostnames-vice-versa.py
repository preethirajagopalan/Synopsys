import socket
#ip to hostname
with open("test.txt", "r") as ins:
    for line in ins:
        print(socket.getfqdn(line.strip()))


# hostname to ip
with open("test.txt", "r") as ins:
    for line in ins:
        print(socket.gethostbyname(line.strip()))