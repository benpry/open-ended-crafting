"""
This file contains prompts for the language model.
"""


def get_combination_prompt(e1, e2, ic_examples):
    system_prompt = """
    You are controlling the dynamics of a cooking game. Given two items, your job is to generate the item you get from combining them, along with its value.

    You should be very literal in your response. For example, "apple" and "flour" should not make "apple pie" since apple pie requires more items. You would have to make a pie crust first. If the two ingredients are both raw, the resulting item should be raw too.

    Each item should have a value, representing how good it is to eat. Ingredients that can't be eaten on their own, like raw flour, should have a value of 0. The maximum possible value is 100. Combined items should generally have higher values than their ingredients, unless they are weird and bad combinations.

    You should also decide whether the resulting item is consumable or not. Kitchen tools like ovens and blenders should not be consumable. Items that you only use a little bit of at a time, like salt and flour, should also be non-consumable. Items that you use up when you use them, like tomatoes, should be consumable.

    Finally, you should choose an appropriate string of up to three emoji for the item.

    Think step by step about what the resulting item should be, what its value should be, and what emoji to use.
    """

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    for items, outcome in ic_examples:
        messages.append(
            {
                "role": "user",
                "content": f"Item 1: {items[0]}\nItem 2: {items[1]}",
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
