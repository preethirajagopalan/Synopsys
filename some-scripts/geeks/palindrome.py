#Input: khokho
#Input:amaama

Input1 = "khokho"
Input2 = "amaama"

class palindrome:
    def __init__(self,input):
        r_input = input[::-1]
        if input == r_input:
            print("True Palindrome")
        else:
            print("False Not a palindrome")



obj = palindrome(Input1)
obj1 = palindrome(Input2)




