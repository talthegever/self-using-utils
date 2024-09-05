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
from itertools import permutations, product
from sympy import simplify, SympifyError
from tqdm import tqdm

NUMBERS_COUNT = 4
TARGET = 10
OPERATIONS = {"repeatable": "+-*/", "non-repeatable": "()"}


def parse_input(numbers: str) -> List:
    """
    input: str that represent the 4 numbers expected
    handle wrong input
    return: list of the 4 numbers
    """
    str_length = len(numbers)
    expected_length = NUMBERS_COUNT * 2 - 1
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


def try_all_orders(numbers: List, operators_options: List) -> str:
    """
    input: list of 4 numbers, and all options to order operators
    changes the order of the numbers till the combination is possible
    return: str that represents the operations needed to be done in order to reach target
    """
    for order in tqdm(set(permutations(numbers))):
        result = try_all_operations_on_specific_order(list(order), operators_options)
        if result:
            return result
    return ''


def try_all_operations_on_specific_order(numbers: List, operators_options: List) -> str:
    """
    input: 4 numbers list and all options to order the operators
    trying all operations on this specific order of numbers
    return:str of the solution, if there is one
    """
    for option in operators_options:
        exercise_str = create_exercise_from_operators_and_numbers(numbers, option)
        parentheses_options = exercise_with_parentheses(exercise_str)
        parentheses_options.insert(0, exercise_str)
        for exercise_option in parentheses_options:
            if calc_str_equal_target(exercise_option):
                return exercise_option
    return ''


def exercise_with_parentheses(exercise: str) -> List:
    all_options = []
    for i in range(len(exercise)):
        for j in range(i + 1, len(exercise) + 1):
            all_options.append(
                exercise[:i] + OPERATIONS["non-repeatable"][0] + exercise[i:j] + OPERATIONS["non-repeatable"][
                    1] + exercise[j:])
    return all_options


def create_exercise_from_operators_and_numbers(numbers: List, operators: List) -> str:
    exercise = ''
    for i in range(len(operators)):
        exercise += str(numbers[i]) + operators[i]
    exercise += str(numbers[-1])
    return exercise


def get_all_operation_order_options() -> List:
    """
    return: list of all options to place the math operators, without using parentheses
    """
    return list(product(list(OPERATIONS["repeatable"]), repeat=NUMBERS_COUNT - 1))


def calc_str_equal_target(excercise: str) -> int:
    try:
        return simplify(excercise) == TARGET
    except (SympifyError, TypeError):
        return False


def main():
    while True:
        numbers = parse_input(input("enter your 4 digits with spaces between them:\n"))
        if numbers:
            solution = try_all_orders(numbers, get_all_operation_order_options())
            print(solution) if solution else print("couldn't find solution")


if __name__ == '__main__':
    main()
