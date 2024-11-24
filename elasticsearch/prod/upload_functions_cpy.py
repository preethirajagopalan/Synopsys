#!/opt/python-2.7.13/bin/python -u

import pytz
import base64

# function to set the settings along with mappings for Elastic Search
# mappings are set based on whether the fields are for interface, node or from lansweeper


def set_map(code):
    # if the code is 'us' then set the settings and mappings for us
    if code.lower() == 'us':
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "normalizer": {
                        "lower_case_normalizer": {
                            "type": "custom",
                            "filter": [
                                "lowercase"
                            ]
                        }

                    }
                },
            },
            "mappings": {
                "interface-metrics": {
                    "properties": {
                        "node.nodeid": {"type": "integer"},
                        "interface.interfaceid": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.in_averagebps": {"type": "long"},
                        "interface.out_averagebps": {"type": "long"},
                        "interface.in_maxbps": {"type": "long"},
                        "interface.out_maxbps": {"type": "long"},
                        "interface.in_minbps": {"type": "long"},
                        "interface.out_minbps": {"type": "long"},
                        "datetime": {"type": "date",
                                     "format": "yyyy-MM-dd HH:mm:ss.SSSSSS"},
                        "interface.interfacename": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.inpercentutil": {"type": "integer"},
                        "interface.outpercentutil": {"type": "integer"},
                        "interface.indiscardsthishour": {"type": "long"},
                        "interface.inerrorsthishour": {"type": "long"},
                        "interface.outdiscardsthishour": {"type": "long"},
                        "interface.outerrorsthishour": {"type": "long"},
                        "interface.interfacespeed": {"type": "long"},
                        "interface.inbandwidth": {"type": "long"},
                        "interface.outbandwidth": {"type": "long"},
                        "node.ip_address": {"type": "ip"},
                        "geoip.country_code2": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.network-node": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.dns": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.dc_site": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.snmp_location": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "type": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.rack_location": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.interface_tier_level": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.node_tier_level": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.asset_type": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "site": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.switch.dnsname": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.if.description": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.if.macaddress": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.asset.macaddress": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.hostname": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.ipaddress": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.iplocation": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.asset.manufacturer": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.asset.model": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.packetloss": {"type": "long"},
                        "node.avgresponsetime": {"type": "long"},
                        "node.avgcpuload": {"type": "long"},
                        "node.memoryused": {"type": "long"},

                    }
                }

            },
        }
        return settings
    elif code.lower() == 'intl':
        # if the code is 'intl' then place the settings and mappings for intl
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "normalizer": {
                        "lower_case_normalizer": {
                            "type": "custom",
                            "filter": [
                                "lowercase"
                            ]
                        }

                    }
                },
            },
            "mappings": {
                "interface-metrics": {
                    "properties": {
                        "node.nodeid": {"type": "integer"},
                        "interface.interfaceid": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.in_averagebps": {"type": "long"},
                        "interface.out_averagebps": {"type": "long"},
                        "interface.in_maxbps": {"type": "long"},
                        "interface.out_maxbps": {"type": "long"},
                        "interface.in_minbps": {"type": "long"},
                        "interface.out_minbps": {"type": "long"},
                        "datetime": {"type": "date",
                                     "format": "yyyy-MM-dd HH:mm:ss.SSSSSS"},
                        "interface.interfacename": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.inpercentutil": {"type": "integer"},
                        "interface.outpercentutil": {"type": "integer"},
                        "interface.indiscardsthishour": {"type": "long"},
                        "interface.inerrorsthishour": {"type": "long"},
                        "interface.outdiscardsthishour": {"type": "long"},
                        "interface.outerrorsthishour": {"type": "long"},
                        "interface.interfacespeed": {"type": "long"},
                        "interface.inbandwidth": {"type": "long"},
                        "interface.outbandwidth": {"type": "long"},
                        "node.ip_address": {"type": "ip"},
                        "geoip.country_code2": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.network-node": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.dns": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.dc_site": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.snmp_location": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "type": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.rack_location": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "interface.interface_tier_level": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.node_tier_level": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.asset_type": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "site": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.switch.dnsname": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.if.description": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.if.macaddress": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.asset.macaddress": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.hostname": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.ipaddress": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.iplocation": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.asset.manufacturer": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "lansweeper.asset.model": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "node.packetloss": {"type": "long"},
                        "node.avgresponsetime": {"type": "long"},
                        "node.avgcpuload": {"type": "long"},
                        "node.memoryused": {"type": "long"},

                    }
                }

            },
        }
        return settings


# datetime conversion to UTC (Necessary for Elastic Search)
def datetime_to_utc(datetime, code):
    # data from solarwinds-us-sql follows PST, therefore convert to UTC
    # as ELK follows UTC time zone
    if code.lower() == 'us':
        naive = datetime
        tz = pytz.timezone("America/Los_Angeles")
        aware = tz.localize(naive)
        utc = aware.astimezone(pytz.timezone("UTC"))
        date = str(utc.date())
        time = str(utc.time())
        dt = date + " " + time
        return dt
    # data from solarwinds-intl-sql follows CET, therefore convert to UTC
    # as ELK follows UTC time zone
    elif code.lower() == 'intl':
        naive = datetime
        tz = pytz.timezone("Europe/Berlin")
        aware = tz.localize(naive)
        utc = aware.astimezone(pytz.timezone("UTC"))
        date = str(utc.date())
        time = str(utc.time())
        dt = date + " " + time
        return dt


# retrieve password to connect to US-SQL and Intl-SQL from their respective files
# currently US-SQL and Intl-SQL have the same password, in future if the password differs
# include a parameter to read the different regions and perform the operations mentioned below
def get_password():
    # read the info stored in file check_test.txt to gather password for solarwinds-us-sql
    # convert from base64 to get the actual value
    f = open("//network//scripts//elasticsearch//check_test.txt", "r")
    read = f.read()
    return base64.b64decode(read)


# retrieve password to connect to Lansweeper
def get_password_ls():
    # read the info stored in file check_test.txt to gather password for lansweeperdb
    # convert from base64 to get the actual value
    f = open("//network//scripts//elasticsearch//check_ls.txt", "r")
    read = f.read()
    return base64.b64decode(read)


# retrieve password to connect to ens-db
def get_password_ens():
    # read the info stored in file check_test.txt to gather password for ens-db
    # convert from base64 to get the actual value
    f = open("//network//scripts//elasticsearch//check_ens.txt", "r")
    read = f.read()
    return base64.b64decode(read)

