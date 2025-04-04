"""
This file contains prompts for the language model.
"""

items = {
    "apple": {
        "name": "apple",
        "value": 2,
        "consumable": True,
        "emoji": "🍎",
    },
    "flour": {
        "name": "flour",
        "value": 1,
        "consumable": False,
        "emoji": "🌾",
    },
    "raw meat": {
        "name": "raw meat",
        "value": 0,
        "consumable": False,
        "emoji": "🥩",
    },
    "knife": {
        "name": "knife",
        "value": 0,
        "consumable": False,
        "emoji": "🔪",
    },
    "salt": {
        "name": "salt",
        "value": 0,
        "consumable": False,
        "emoji": "🧂",
    },
    "stove": {
        "name": "stove",
        "value": 0,
        "consumable": False,
        "emoji": "🔥",
    },
    "water": {
        "name": "water",
        "value": 0,
        "consumable": False,
        "emoji": "💧",
    },
    "floury apple": {
        "reasoning": "Combining apple and flour should make an apple with flour around it. This is probably worse than just eating the apple, so the value should be lower than the apple's original value.",
        "name": "floury apple.",
        "value": 1,
        "consumable": True,
        "emoji": "🍎",
    },
    "breaded apple": {
        "reasoning": "Cooking the floury apple should crisp up the flour and make something crispy and delicious. The value should be higher than the floury apple's original value.",
        "name": "breaded apple",
        "value": 20,
        "consumable": True,
        "emoji": "🍞🍎",
    },
    "sliced raw meat": {
        "reasoning": "Slicing raw meat will make it more uniform, so if gets cooked it will not be as good. This doesn't change the fact that it's raw and raw meat is inedible, so the value should still be 0",
        "name": "sliced raw meat",
        "value": 0,
        "consumable": True,
        "emoji": "🔪🥩",
    },
    "cooked sliced meat": {
        "reasoning": "Cooking sliced meat makes it edible. But it's not as good as cooked non-sliced meat because it doesn't get the crust outside and the rare meat inside.",
        "name": "cooked sliced meat",
        "value": 35,
        "consumable": True,
        "emoji": "🔪🍖",
    },
    "cooked meat": {
        "reasoning": "Cooking meat makes it edible and more delicious. The value should be higher than the raw meat's original value.",
        "name": "cooked meat.",
        "value": 40,
        "consumable": True,
        "emoji": "🍖",
    },
    "sliced cooked meat": {
        "reasoning": "Slicing cooked meat makes it easier to eat. The value should be higher than the cooked meat's original value.",
        "name": "sliced cooked meat",
        "value": 50,
        "consumable": True,
        "emoji": "🔪🍖",
    },
    "salted sliced cooked meat": {
        "reasoning": "Adding salt to sliced cooked meat makes it more delicious. The value should be higher than the sliced cooked meat's original value.",
        "name": "salted sliced cooked meat",
        "value": 55,
        "consumable": True,
        "emoji": "🧂🔪🍖",
    },
    "too salty sliced cooked meat": {
        "reasoning": "Adding salt to sliced cooked meat that already has salt on it should make it too salty to eat. The value should be lower than the salted sliced cooked meat's original value.",
        "name": "too salty sliced cooked meat",
        "value": 20,
        "consumable": True,
        "emoji": "🧂🧂🍖",
    },
    "banana": {
        "name": "banana",
        "emoji": "🍌",
        "value": 2,
        "consumable": True,
    },
    "carrot": {
        "name": "carrot",
        "emoji": "🥕",
        "value": 2,
        "consumable": True,
    },
    "banana and carrot": {
        "reasoning": "It's not clear how to combine a banana and a carrot, so we will just return a banana and a carrot individually, with a value that is the sum of the two values.",
        "name": "banana and carrot",
        "value": 4,
        "consumable": True,
        "emoji": "🍌🥕",
    },
    "banana and carrot in water": {
        "reasoning": "Combining banana and carrot with water should just make banana and carrot in water. It's not a soup yet because it hasn't been cooked. Putting them in water makes them soggy and worse (until cooking).",
        "name": "banana and carrot in water",
        "value": 2,
        "consumable": True,
        "emoji": "🍌🥕💧",
    },
    "banana and carrot soup": {
        "reasoning": "Cooking banana and carrot in water should make a soup. The value should be higher than the banana and carrot in water's original value. But banana and carrot are kidn",
        "name": "banana and carrot soup",
        "value": 18,
        "consumable": True,
        "emoji": "🍌🥕🍲",
    },
}

base_examples = [
    [items["apple"], items["flour"], items["floury apple"]],
    [items["floury apple"], items["stove"], items["breaded apple"]],
    [items["raw meat"], items["knife"], items["sliced raw meat"]],
    [items["sliced raw meat"], items["stove"], items["cooked sliced meat"]],
    [items["cooked meat"], items["knife"], items["sliced cooked meat"]],
    [items["sliced cooked meat"], items["salt"], items["salted sliced cooked meat"]],
    [items["sliced cooked meat"], items["salt"], items["too salty sliced cooked meat"]],
    [items["banana"], items["carrot"], items["banana and carrot"]],
    [items["banana and carrot"], items["water"], items["banana and carrot in water"]],
    [
        items["banana and carrot in water"],
        items["stove"],
        items["banana and carrot soup"],
    ],
]


def get_combination_prompt(e1, e2, ic_examples):
    system_prompt = """
    You are controlling the dynamics of a cooking game. Given two items, your job is to generate the item you get from combining them, along with its value.

    You should be very literal in your response. For example, "apple" and "flour" should not make "apple pie" since apple pie requires more items. You would have to make a pie crust first. If the two ingredients are both raw, the resulting item should be raw too. If the items are two things that don't clearly combine (like banana and carrot) the resulting item should just be the two things together (like "banana and carrot") but if the items could plausibly be combined to make a dish, the resulting item should be a dish.

    Each item should have a value, representing how good it is to eat. Ingredients that can't be eaten on their own, like raw flour, should have a value of 0.

    Things that sound like real dishes should have much higher values than things that don't. For instance, "tomato soup" should be much more valuable than "tomato" or "sliced tomato and onion." The value of these real dishes should be above 10.

    You should also decide whether the resulting item is consumable or not. Consumable items are used up when you use them once. This is not the same as whether they're safe for human consumption. Kitchen tools like stoves and knives should not be consumable. Items that you only use a little bit of at a time, like salt and spices, should also be non-consumable. Items that you use up when you use them, like tomatoes, should be consumable.

    Finally, you should choose an appropriate string of up to three emoji for the item.

    Some general rules should be true of the resulting items:
    1. Cooking sliced vegetables on the stove should be better than cooking whole vegetables on the stove.
    2. Slicing meat after cooking it should make it better. Cooking sliced meat should not be as good as cooking whole meat.
    3. Putting things in water should make them worse, unless they are sliced and cooked on the stove to make a soup.
    4. Adding salt should make things a bit better, but adding salt more than once should make them worse. Combinining two salted ingredients should make something that's too salty.
    5. Grains should be combined with water before being placed on the stove. Putting raw grains on the stove should toast them, which makes them a little bit better, but roasted grains combined with water should not make anything good.
    6. Adding something inedible, like raw rice or raw meat, to something edible should drop the value dramatically. The value should come up again if the dish gets cooked again on the stove.
    7. If something is already a dish, you should be very judicious in deciding whether adding a new thing improves it. Adding items where the flavor makes sense, or common aromatics like ginger and garlic, should improve it. But adding random ingredients should not improve it.

    Think step by step about what the resulting item should be, what its value should be, and what emoji to use.
    """

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    for example in base_examples + ic_examples:

        item1, item2, outcome = example
        item1 = {
            "name": item1["name"],
            "emoji": item1["emoji"],
            "value": item1["value"],
            "consumable": item1["consumable"],
        }
        item2 = {
            "name": item2["name"],
            "emoji": item2["emoji"],
            "value": item2["value"],
            "consumable": item2["consumable"],
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

    print(messages)

    return messages
