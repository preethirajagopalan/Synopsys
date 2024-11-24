#!/opt/python-2.7.13/bin/python -u
# a = 'badc'
# s = len(a)
# for i in range(s):
# 	new = a[i+1:]
# 	if new == new[::-1]:
# 		print("yes palindrome")
# 		break;
# 	else:
# 		print("no",i)


def validPalindrome(s):
    left= 0
    right = len(s) - 1
    while left < right:
        if s[left] != s[right]:
            one = s[left:right]
            two = s[left + 1:right + 1]
            return one == one[::-1] or two == two[::-1]
        left, right = left + 1, right - 1
    return True
if __name__ == "__main__":
    validPalindrome("badc")




#
# def isPalindrome(string: str, low: int, high: int) -> bool:
#     while low < high:
#         if string[low] != string[high]:
#             return False
#         low += 1
#         high -= 1
#     return True
# string = "abcd"
# isPalindrome(string, 0, 3)