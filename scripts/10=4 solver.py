"""moblie game.
you get 4 numbers, from 1 to 9 (order changeable), and four basics operators: +-/*.
in addition, you can use once (). you need to get to 10 every time.
for example: lvl 335:
3 1 2 2:
(3+2)*2*1
this program will solve stupidly (the naive way) every lvl
input: string built like: '<num><space><num><space><num><space><num><space>'
        for example 2 2 2 2
output: string describing the actions needed to happen in order to solve the level"""

from typing import List

NUMBERS_COUNT = 4


def parse_input(numbers: str) -> List:
    str_length = len(numbers)
    expected_length = NUMBERS_COUNT*2-1
    if str_length == expected_length:  # space between every number
        try:
            numbers_list = [int(number) for number in numbers.split(' ')]
        except ValueError as e:
            print("you entered a char that is not a number")
        else:
            if any((number < 0 or number > 9) for number in numbers_list):
                print("you entered a negative or too big number")
            else:
                return numbers_list
    else:
        print(f"you eneterd {str_length} length string, i expected {expected_length}.\n"
              f"are you sure you entered {NUMBERS_COUNT} numbers with spaces between them?")
    return []




def main():
    numbers = parse_input(input("enter your 4 digits with spaces between them:\n"))
    if numbers:
        print(numbers)


if __name__ == '__main__':
    main()