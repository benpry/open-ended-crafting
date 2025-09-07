import random

from src.constants import cooking_ingredients, cooking_tools
from src.functions import cooking_apply_tool, cooking_combination_function

cooking_inv = cooking_ingredients + cooking_tools


def test_cooking_combination_function():
    # grab two random items

    for _ in range(100):
        item1 = random.choice(cooking_inv)
        item2 = random.choice(cooking_inv)

        print(f"item 1: {item1}")
        print(f"item 2: {item2}")

        # combine them
        result = cooking_combination_function(item1, item2)

        # check that the result is a valid item
        print("result: ", result)


def test_cooking_apply_tool():
    # grab two random items

    for _ in range(100):
        tool = random.choice(cooking_tools)
        item = random.choice(cooking_ingredients)

        print(f"tool: {tool}")
        print(f"item: {item}")

        # combine them
        result = cooking_apply_tool(tool, item)

        # check that the result is a valid item
        print("result: ", result)
        print("result: ", result)
