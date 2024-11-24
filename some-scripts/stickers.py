import math
import unittest

WORD = "facebook "

def foo(s):

    count = {}
    for c in WORD:
        count[c] = (count[c]+1) if (c in count) else 1

    input_count = {}
    for c in s:
        input_count[c] = (input_count[c]+1) if (c in input_count) else 1

    max_stickers = 0
    for letter in input_count:
        num_needed = input_count[letter]
        for i in count:
            if letter == i:
                num_in_one_sticker = count[i]
        num_stickers_needed = int(math.ceil(float(num_needed) / float(num_in_one_sticker)))
        max_stickers = max(num_stickers_needed, max_stickers)
    print(max_stickers)

    return max_stickers
if __name__ == '__main__':
    foo("coffee kebab")
    foo("facebook facebook")
    foo("faceboook")
    foo("face book")




# class Test(unittest.TestCase):
#     def testExample(self):
#         self.assertEquals(3, foo("coffee kebab"))
#         self.assertEquals(1, foo("facebook"))
#         self.assertEquals(2, foo("facebook facebook"))
#         self.assertEquals(1, foo("face book"))
#         self.assertEquals(3, foo("facefacebookface"))
#         self.assertEquals(2, foo("faceboook"))
# if __name__ == "__main__":
#     #import sys;sys.argv = ['', 'Test.testName']
#     unittest.main()
