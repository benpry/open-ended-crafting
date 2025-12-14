import random

from oecraft.constants import Ingredient, Tool
from oecraft.game_descriptors import GAME_DESCRIPTORS


def test_combination_functions():
    for domain_name, descriptor in GAME_DESCRIPTORS.items():
        print(f"Testing domain: {domain_name}")

        # reconstruct objects from dicts
        ingredients = [Ingredient(**d) for d in descriptor.ingredients]
        tools = [Tool(**d) for d in descriptor.tools]
        inventory = ingredients + tools

        combination_fn = descriptor.combination_fn

        for _ in range(50):
            item1 = random.choice(inventory)
            item2 = random.choice(inventory)

            # print(f"item 1: {item1}")
            # print(f"item 2: {item2}")

            # combine them
            result = combination_fn(item1, item2)

            # check that the result is valid (None or has features)
            # print("result: ", result)
