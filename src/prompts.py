"""
This file contains prompts for the language model.
"""

from src.constants import SYSTEM_PROMPTS

items = {
    "apple": {
        "name": "apple",
        "value": 2,
        "durable": False,
        "emoji": "🍎",
    },
    "flour": {
        "name": "flour",
        "value": 1,
        "durable": True,
        "emoji": "🌾",
    },
    "raw meat": {
        "name": "raw meat",
        "value": 0,
        "durable": True,
        "emoji": "🥩",
    },
    "knife": {
        "name": "knife",
        "value": 0,
        "durable": True,
        "emoji": "🔪",
    },
    "salt": {
        "name": "salt",
        "value": 0,
        "durable": True,
        "emoji": "🧂",
    },
    "stove": {
        "name": "stove",
        "value": 0,
        "durable": True,
        "emoji": "🔥",
    },
    "water": {
        "name": "water",
        "value": 0,
        "durable": True,
        "emoji": "💧",
    },
    "floury apple": {
        "reasoning": "Combining apple and flour should make an apple with flour around it. This is probably worse than just eating the apple, so the value should be lower than the apple's original value.",
        "name": "floury apple.",
        "value": 1,
        "durable": False,
        "emoji": "🍎",
    },
    "breaded apple": {
        "reasoning": "Cooking the floury apple should crisp up the flour and make something crispy and delicious. The value should be higher than the floury apple's original value.",
        "name": "breaded apple",
        "value": 20,
        "durable": False,
        "emoji": "🍞🍎",
    },
    "sliced raw meat": {
        "reasoning": "Slicing raw meat will make it more uniform, so if gets cooked it will not be as good. This doesn't change the fact that it's raw and raw meat is inedible, so the value should still be 0",
        "name": "sliced raw meat",
        "value": 0,
        "durable": False,
        "emoji": "🔪🥩",
    },
    "cooked sliced meat": {
        "reasoning": "Cooking sliced meat makes it edible. But it's not as good as cooked non-sliced meat because it doesn't get the crust outside and the rare meat inside.",
        "name": "cooked sliced meat",
        "value": 35,
        "durable": False,
        "emoji": "🔪🍖",
    },
    "cooked meat": {
        "reasoning": "Cooking meat makes it edible and more delicious. The value should be higher than the raw meat's original value.",
        "name": "cooked meat.",
        "value": 40,
        "durable": False,
        "emoji": "🍖",
    },
    "sliced cooked meat": {
        "reasoning": "Slicing cooked meat makes it easier to eat. The value should be higher than the cooked meat's original value.",
        "name": "sliced cooked meat",
        "value": 50,
        "durable": False,
        "emoji": "🔪🍖",
    },
    "salted sliced cooked meat": {
        "reasoning": "Adding salt to sliced cooked meat makes it more delicious. The value should be higher than the sliced cooked meat's original value.",
        "name": "salted sliced cooked meat",
        "value": 55,
        "durable": False,
        "emoji": "🧂🔪🍖",
    },
    "too salty sliced cooked meat": {
        "reasoning": "Adding salt to sliced cooked meat that already has salt on it should make it too salty to eat. The value should be lower than the salted sliced cooked meat's original value.",
        "name": "too salty sliced cooked meat",
        "value": 20,
        "durable": False,
        "emoji": "🧂🧂🍖",
    },
    "banana": {
        "name": "banana",
        "emoji": "🍌",
        "value": 2,
        "durable": False,
    },
    "carrot": {
        "name": "carrot",
        "emoji": "🥕",
        "value": 2,
        "durable": False,
    },
    "carrot in water": {
        "reasoning": "Combining a carrot with water should just make a carrot in water. It's not a soup yet because it hasn't been cooked. Putting them in water makes them soggy and worse (until cooking).",
        "name": "carrot in water",
        "value": 1,
        "durable": False,
        "emoji": "🥕💧",
    },
    "carrot soup": {
        "reasoning": "Cooking carrot in water should make a soup. The value should be higher than the carrot in water's original value. But banana and carrot are kind of gross together, so the value should be lower than the carrot's original value.",
        "name": "carrot soup",
        "value": 18,
        "durable": False,
        "emoji": "🥕🍲",
    },
}

base_examples = [
    [items["apple"], items["flour"], items["floury apple"]],
    [items["floury apple"], items["stove"], items["breaded apple"]],
    [items["raw meat"], items["knife"], items["sliced raw meat"]],
    [items["sliced raw meat"], items["stove"], items["cooked sliced meat"]],
    [items["cooked meat"], items["knife"], items["sliced cooked meat"]],
]


def get_combination_prompt(e1, e2, game_type):
    system_prompt = SYSTEM_PROMPTS[game_type]
    ic_examples = []

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    for example in base_examples + ic_examples:

        item1, item2, outcome = example
        item1 = {
            "name": item1["name"],
            "emoji": item1["emoji"],
            "value": item1["value"],
            "durable": item1["durable"],
        }
        item2 = {
            "name": item2["name"],
            "emoji": item2["emoji"],
            "value": item2["value"],
            "durable": item2["durable"],
        }
        messages.append(
            {
                "role": "user",
                "content": f"Item 1: {item1}\nItem 2: {item2}",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": str(outcome),
            }
        )

    messages += [
        {"role": "user", "content": f"Item 1: {e1}\nItem 2: {e2}"},
    ]

    return messages
