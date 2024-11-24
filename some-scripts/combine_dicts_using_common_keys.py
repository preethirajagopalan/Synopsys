"""Program1"""


l1 = [{'id': 9, 'av': 4}, {'id': 10, 'av': 0}, {'id': 8, 'av': 0}]

l2 = [{'id': 9, 'nv': 45}, {'id': 10, 'nv': 0}, {'id': 8, 'nv': 30}]


l3 = {}
for x in l1:
    l3.update({x['id']: {'av': x['av']}})
for d in l2:
    l3[d['id']].update(nv=d['nv'])
print(l3)

"""Program2"""

Input1 = [{'roll_no': ['123445', '1212'], 'school_id': 1},
          {'roll_no': ['HA-4848231'], 'school_id': 2}]
Input2 = [{'roll_no': ['473427'], 'school_id': 2},
          {'roll_no': ['092112'], 'school_id': 5}]

for y in Input2:
    for x in Input1:
        if x['school_id'] == y['school_id']:
            x['roll_id'].extend(y['roll_id'])
        break
    else:
        Input1.append(y)
print(Input1)