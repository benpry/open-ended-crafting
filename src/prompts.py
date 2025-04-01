"""
This file contains prompts for the language model.
"""


def get_combination_prompt(e1, e2, ic_examples):
    system_prompt = """
    You are controlling the dynamics of a cooking game. Given two items, your job is to generate the item you get from combining them, along with its value.

    You should be very literal in your response. For example, "apple" and "flour" should not make "apple pie" since apple pie requires more items. You would have to make a pie crust first. If the two ingredients are both raw, the resulting item should be raw too.

    Each item should have a value, representing how good it is to eat. Ingredients that can't be eaten on their own, like raw flour, should have a value of 0. The maximum possible value is 100. Combined items should generally have higher values than their ingredients, unless they are weird and bad combinations.

    You should also decide whether the resulting item is consumable or not. Consumable items are used up when you use them once. This is not the same as whether they're safe for human consumption. Kitchen tools like ovens and blenders should not be consumable. Items that you only use a little bit of at a time, like salt and flour, should also be non-consumable. Items that you use up when you use them, like tomatoes, should be consumable.

    Finally, you should choose an appropriate string of up to three emoji for the item.

    Some general rules should be true of the resulting items:
    1. Cooking sliced vegetables in the oven should be better than cooking whole vegetables in the oven.
    2. Slicing meat after cooking it should make it better. Cooking sliced meat should not be as good as cooking whole meat.
    3. Putting things in water should make them worse, unless they are sliced and cooked in the oven to make a soup.
    4. Adding salt should make things a bit better, but adding salt more than once should make them worse. Combinining two salted ingredients should make something that's too salty.
    5. Grains should be combined with water before being placed in the oven. Putting raw grains in the oven should toasted them, which makes them a little bit better, but roasted grains combined with water should not make anything good.

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
