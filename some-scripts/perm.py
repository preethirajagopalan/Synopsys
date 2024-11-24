#!/opt/python-2.7.13/bin/python -u

from itertools import combinations
# Get all permutations of [1, 2, 3]
# comb = combinations(['ethernet1/1',
# # # 'ethernet1/2',
# # # 'ethernet1/3',
# # # 'ethernet1/4',
# # # 'ethernet1/9',
# # # 'ethernet1/10',
# # # 'ethernet1/11',
# # # 'ethernet1/12'], 3)

comb = combinations(['ethernet1/5',
'ethernet1/6',
'ethernet1/7',
'ethernet1/8',
'ethernet1/13',
'ethernet1/14',
'ethernet1/15',
'ethernet1/16'], 3)


# Print the obtained permutations
for i in list(comb):
    print(i)