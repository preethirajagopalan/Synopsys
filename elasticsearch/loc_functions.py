#!/opt/python-2.7.13/bin/python -u

import pytz
import base64

# function to set the settings along with mappings for Elastic Search - Locations

def set_map():
    # if the code is 'us' then set the settings and mappings for us
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
                "lookup": {
                    "properties": {
                        "datetime": {"type": "date",
                                     "format": "yyyy-MM-dd HH:mm:ss.SSSSSS"},
                        "geo": {"properties": { "location": { "type": "geo_point"}}},
                        "state": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "city": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "type": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "site": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "country_code2": {"type": "keyword", "normalizer": "lower_case_normalizer"},
                        "asset_type": {"type": "keyword", "normalizer": "lower_case_normalizer"},
		 	"network-node": {"type": "keyword", "normalizer": "lower_case_normalizer"}, 

                    }
                }

            },
        }
    return settings

# retrieve password to connect to US-SQL and Intl-SQL from their respective files
# currently US-SQL and Intl-SQL have the same password, in future if the password differs
# include a parameter to read the different regions and perform the operations mentioned below
def get_password():
    # read the info stored in file check_test.txt to gather password for solarwinds-sql
    # convert from base64 to get the actual value
    f = open("//network//scripts//elasticsearch//check_test.txt", "r")
    read = f.read()
    return base64.b64decode(read)
