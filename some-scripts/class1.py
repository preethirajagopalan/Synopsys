#!/opt/python-2.7.13/bin/python -u

class student():
    subject = "CSE"
    def __init__(self, roll):
        self.roll = roll



if __name__ == '__main__':
    obj = student(10)
    obj1 = student(20)
    print(obj.subject)
    print(obj1.subject)
    print(obj.roll)
    print(obj1.roll)
