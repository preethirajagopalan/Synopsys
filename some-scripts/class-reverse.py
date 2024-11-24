class list_rev:
    def __init__(self,a):
        i = 0
        j = len(a)-1
        while i<j:
            a[i], a[j] = a[j],a[i]
            i += 1
            j -= 1
        self.a = a


if __name__ == '__main__':
    b = list_rev([1,2,3,4])
    print(b.a)
