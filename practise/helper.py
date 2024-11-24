import pytz
import base64


def get_password():
    # read the info stored in file check_test.txt to gather password for solarwinds-us-sql
    # convert from base64 to get the actual value
    f = open("//network//scripts//elasticsearch//check_test.txt", "r")
    read = f.read()
    return base64.b64decode(read)