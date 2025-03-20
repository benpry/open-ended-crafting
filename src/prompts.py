"""
This file contains prompts for the language model.
"""


def get_initialization_prompt():
    system_prompt = """
    You are controlling the dynamics of a cooking game. Your job is to output a list of six simple items that lots of interesting things could be created from.
    The game is meant to be fun and open-ended, with lots of potential for exploration, so you should choose items accordingly.

    Each item should have a value, representing how good it is to eat. Ingredients that can't be eaten on their own, like raw flour and raw eggs, should have a value of 0. The maximum possible value is 100. Starting items should have low values to create lots of room to make better items.

    For reference, raw vegetables should generally have values less than or equal to 10, and complex dishes that require a lot of parts, like crocombouche and pho, should have values greater than 50.

    You should also decide whether each item is consumable or not. Kitchen tools like ovens and blenders should not be consumable. Items that you only use a little bit of at a time, like salt and flour, should also be non-consumable. Items that you use up when you use them, like tomatoes, should be consumable.

    You should choose an appropriate single emoji for the item. Make sure the item gets just one emoji.


    Think step by step about what the items should be, what their values should be, and what emoji to use.
    """

    test_message = "Please return a list of basic items that the player can use to create a wide assortment of possible edible dishes."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": test_message},
    ]
    return messages


def get_combination_prompt(e1, e2, condition="base"):
    system_prompt = """
    You are controlling the dynamics of a cooking game. Given two items, your job is to generate the item you get from combining them, along with its value.

    You should be very literal in your response. For example, "apple" and "flour" should not make "apple pie" since apple pie requires more items. You would have to make a pie crust first. If the two ingredients are both raw, the resulting item should be raw too.

    Each item should have a value, representing how good it is to eat. Ingredients that can't be eaten on their own, like raw flour, should have a value of 0. The maximum possible value is 100. Combined items should generally have higher values than their ingredients, unless they are weird and bad combinations.

    You should also decide whether the resulting item is consumable or not. Kitchen tools like ovens and blenders should not be consumable. Items that you only use a little bit of at a time, like salt and flour, should also be non-consumable. Items that you use up when you use them, like tomatoes, should be consumable.

    Finally, you should choose an appropriate single emoji for the item. Make sure the item gets just one emoji.

    Think step by step about what the resulting item should be, what its value should be, and what emoji to use.
    """

    ic_message = """Item 1: {
        "name": "Raw steak",
        "value": 2,
        "consumable": True,
        "emoji": "🥩"
    }
    Item 2: {
        "name": "Oven",
        "value": 0,
        "consumable": False,
        "emoji": "🔥"
    }"""
    ic_response = """{
        "name": "Cooked steak",
        "value": 20,
        "consumable": True,
        "emoji": "🥩"
    }"""

    e1 = dict(e1)
    e2 = dict(e2)
    if "reasoning" in e1:
        del e1["reasoning"]
    if "reasoning" in e2:
        del e2["reasoning"]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": ic_message},
        {"role": "assistant", "content": ic_response},
        {"role": "user", "content": f"Item 1: {e1}\nItem 2: {e2}"},
    ]

    return messages
