#!/opt/python-2.7.13/bin/python -u

import socket
from ParseHelpers import parse_info
from RouterConnection import RouterConnection

def get_hostname_from_ip(ip):
    """
    :type ip: string
    :rtype: string

    Converts the given ip to a string hostname. Attempts to use socket module first. If this fails, then
    the function will actually connect to the device and get the name from the connection. Returns a string
    if successful and None otherwise.

    EXAMPLE USAGE:
    hostname = get_hostname_from_ip('198.182.41.251')
    """    
    # tries nslookup
    try:
        info = socket.getfqdn(ip)
    except:
        info = None

    if info != None:
        hostname_info = parse_info(r'(\S+).internal.synopsys.com', info, 1)
        if (len(hostname_info) == 1):
            return hostname_info[0].lower()
    
    # have to manually log in, try both ios and xe
    temp_connect = RouterConnection('cisco_ios', ip, need_src=False)
    if temp_connect.is_connected():
        name = temp_connect.get_name()
        temp_connect.disconnect()
        return name

    temp_connect = RouterConnection('cisco_xe', ip, need_src=False)
    if temp_connect.is_connected():
        name = temp_connect.get_name()
        temp_connect.disconnect()
        return name

    # if all else fails
    return None

    
def get_ip(connect):
    """
    :type connect: RouterConnection
    :rtype: string

    Gets the ip of a RouterConnection object. Uses the socket module and the name and alias of a connect object
    to attempt to resolve the hostname. If successful, returns a string. Else, returns None.

    EXAMPLE USAGE:
    connect = RouterConnection('cisco_ios', 'netlab-vpn-router')
    ip = get_ip(connect)
    """
    for name in [connect.get_alias(), connect.get_name()]:
        try:
            info = socket.gethostbyname(name)
        except:
            info = None

        if info != None:
            return info

    return None