#!/opt/python-2.7.13/bin/python -u
import ast
import statistics
from functools import reduce
lst = []
def i_file():
    with open("/network/scripts/Zscaler/input.txt", "r") as inFile:
        data = inFile.read().strip(' ')
        data1 = ast.literal_eval(data)
        for i in data1:
                lst.append(i[0])
        lst1 = filter(lambda a: a != -1.0, lst)
        # print(lst1)
        avg = sum(lst1)/len(lst1)
        print(avg)

i_file()

