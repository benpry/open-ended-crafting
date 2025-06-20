import math


def cooking_value_function(item):
    # inedible things are worth 0
    if not item["edible"]:
        return 0

    value = 0

    # +5 per chop level
    value += item["chop_level"] * 5

    # cooked things are worth +5
    if item["cook_level"] == 1:
        value += 5

    # chopped and cooked things are worth +10
    if item["chop_level"] == 1 and item["cook_level"] == 1:
        value += 10

    # +5 for cooked things in water
    if item["cook_level"] == 1 and item["water_level"] == 1:
        value += 5

    # salted things are worth +5
    if item["salt_level"] == 1:
        value += 5

    # +5 for each additional ingredient type
    value += (len(item["ingredient_types"]) - 1) * 3

    # -5 for oversalted things
    if item["salt_level"] == 3:
        value -= 10

    # -10 for burnt things
    if item["cook_level"] == 2:
        value -= 10

    # -5 for raw things in water
    if item["water_level"] == 1 and item["cook_level"] == 0:
        value -= 10

    # -3 for each ingredient after 3
    if len(item["all_ingredients"]) > 3:
        value -= 8 * (len(item["all_ingredients"]) - 3)

    # -5 for eviscerated things
    if item["chop_level"] == 2:
        value -= 8

    return max(value, 0)


cooking_feature_names = {
    "water_level": ["dry", "soaked"],
    "chop_level": ["unchopped", "chopped", "minced"],
    "salt_level": ["unsalted", "salted", "oversalted"],
    "cook_level": ["raw", "cooked", "overcooked"],
}


def cooking_apply_tool(tool, item):
    new_item = item.copy()

    # remove features that we don't want to carry over
    del new_item["name"]
    del new_item["emoji"]
    if "value" in new_item:
        del new_item["value"]

    # ensure tool field is set to False for the result (it's not a tool)
    new_item["tool"] = False

    if tool["name"] == "water":
        # adding water always soaks something
        new_item["water_level"] = 1
        if item["cook_level"] < 2:
            new_item["cook_level"] = 0

    elif tool["name"] == "stove":
        # adjust the cook level
        new_item["edible"] = True
        if item["water_level"] == 1:
            # you can't burn a soaked thing
            new_item["cook_level"] = min(
                item["cook_level"] + 1, len(cooking_feature_names["cook_level"]) - 1
            )
        else:
            # otherwise, cooking increases the cook level by 1, up to the max
            new_item["cook_level"] = min(
                item["cook_level"] + 1, len(cooking_feature_names["cook_level"]) - 1
            )

    # Knife increases chop level. You can't chop a soaked thing.
    elif tool["name"] == "knife" and item["water_level"] == 0:
        # increase the chop level
        new_item["chop_level"] = min(
            item["chop_level"] + 1, len(cooking_feature_names["chop_level"]) - 1
        )

    elif tool["name"] == "salt":
        # increase the salt level
        new_item["salt_level"] = min(
            item["salt_level"] + 1, len(cooking_feature_names["salt_level"]) - 1
        )

    return new_item


def cooking_combination_function(item1, item2):
    """
    The overall combination function for the cooking domain.
    """

    # if they're both tools, return None:
    if item1["tool"] and item2["tool"]:
        return None

    # if one item is a tool, apply it to the other item.
    if item1["tool"]:
        new_item = cooking_apply_tool(item1, item2)
    elif item2["tool"]:
        new_item = cooking_apply_tool(item2, item1)
    else:
        # combine two non-tool items

        new_item = {}

        # the new salt level is the average of the two salt levels (rounding up)
        new_item["salt_level"] = math.ceil(
            (item1["salt_level"] + item2["salt_level"]) / 2
        )

        # cooked + raw gives raw, but anything + burnt gives burnt
        if item1["cook_level"] == 2 or item2["cook_level"] == 2:
            new_item["cook_level"] = 2
        else:
            new_item["cook_level"] = min(item1["cook_level"], item2["cook_level"])

        # the water level is the highest of the two water levels
        new_item["water_level"] = max(item1["water_level"], item2["water_level"])

        # the chop level is the lowest of the two chop levels
        new_item["chop_level"] = min(item1["chop_level"], item2["chop_level"])

        # anything inedible makes the whole thing inedible
        new_item["edible"] = item1["edible"] and item2["edible"]

        new_item["ingredient_types"] = list(
            set(item1["ingredient_types"]) | set(item2["ingredient_types"])
        )
        new_item["all_ingredients"] = (
            item1["all_ingredients"] + item2["all_ingredients"]
        )

    # you can't make new tools
    new_item["tool"] = False
    new_item["value"] = cooking_value_function(new_item)

    return new_item


COMBO_FUNCTIONS = {
    "cooking": cooking_combination_function,
}

FEATURE_NAMES = {
    "cooking": cooking_feature_names,
}
