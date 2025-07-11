import math


def cooking_value_function(item):
    # Base value: only edible things have value
    if not item["edible"]:
        return 0

    value = 0

    # Positive utility:
    if item["cook_level"] == 1 and set(item["ingredient_types"]) != {
        "fruit"
    }:  # Cooked things are good, unless they're fruit
        value += 15

    if (
        item["chop_level"] == 1 and "grain" not in item["ingredient_types"]
    ):  # Chopped things are good, except for meat and grains
        value += 15

    if (
        item["water_level"] == 1
        and item["cook_level"] == 1
        and "fruit" not in item["ingredient_types"]
    ):  # Soup is good
        value += 30

    if item["salt_level"] == 1:  # Salted things are good
        value += 15

    # combining two ingredient types is good
    n_distinct_ingredient_types = len(set(item["ingredient_types"]))
    value += 25 * (n_distinct_ingredient_types - 1)

    # Negative utility:
    if item["cook_level"] == 2:  # Overcooked things are bad
        value -= 40

    if item["salt_level"] == 2:  # Over-salted things are bad
        value -= 40

    if (
        item["water_level"] == 1 and item["cook_level"] == 0
    ):  # Uncooked soaked things are bad
        value -= 25

    # nobody likes fruit soup
    if "fruit" in item["ingredient_types"] and "water" in item["ingredient_types"]:
        value -= 25

    # more than one ingredient of the same type is bad
    for ingredient_type in item["ingredient_types"]:
        if item["ingredient_types"].count(ingredient_type) > 1:
            value -= 30

    return value


cooking_feature_names = {
    "water_level": ["dry", "soaked"],
    "chop_level": ["unchopped", "chopped"],
    "salt_level": ["unsalted", "salted", "oversalted"],
    "cook_level": ["raw", "cooked", "overcooked"],
}


def cooking_apply_tool(tool, item):
    new_item = item.copy()

    # remove features that we don't want to carry over
    if "name" in new_item:
        del new_item["name"]
    if "emoji" in new_item:
        del new_item["emoji"]
    if "value" in new_item:
        del new_item["value"]

    # ensure tool field is set to False for the result (it's not a tool)
    new_item["tool"] = False

    if tool["name"] == "water":
        # adding water always soaks something
        new_item["water_level"] = 1
        # If the item is cooked, soaking un-cooks it (but doesn't rescue burnt things)
        if item["cook_level"] == 1:
            new_item["cook_level"] = 0

    elif tool["name"] == "stove":
        # adjust the cook level
        new_item["edible"] = True  # cooking makes inedible things edible

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

        new_item["ingredient_types"] = (
            item1["ingredient_types"] + item2["ingredient_types"]
        )
        new_item["all_ingredients"] = (
            item1["all_ingredients"] + item2["all_ingredients"]
        )

    # you can't make new tools
    new_item["tool"] = False
    new_item["value"] = cooking_value_function(new_item)

    return new_item


# DECORATIONS DOMAIN FUNCTIONS

decorations_feature_names = {
    "paint_level": ["unpainted", "painted", "over-painted"],
    "cut_level": ["uncut", "cut"],
    "drawn_level": ["undrawn", "drawn"],
}


def decorations_value_function(item):
    """Calculate the value of a decoration based on its features."""
    value = 0  # No base value

    # POSITIVE UTILITY

    # Drawing on artificial materials is good
    if "artificial" in item["material_types"] and item["drawn_level"] == 1:
        value += 25

    # Cutting soft materials is good
    if item["hardness"] == "soft" and item["cut_level"] == 1:
        value += 25

    # Painting is good
    if item["paint_level"] == 1:
        value += 15

    # framing helps, provided we didn't mess with something after framing
    if item["framed"] and not item["post_frame_messed_with"]:
        value += 20

    # combining natural and artificial materials is good
    if "natural" in item["material_types"] and "artificial" in item["material_types"]:
        value += 40

    # NEGATIVE UTILITY

    # messing with things after framing is bad
    if item["post_frame_messed_with"]:
        value -= 50

    # over-painting is bad
    if item["paint_level"] == 2:
        value -= 25

    # cutting hard materials is bad
    if item["hardness"] == "hard" and item["cut_level"] == 1:
        value -= 25

    # combining artificial and natural materials is bad
    if "artificial" not in item["material_types"] and item["drawn_level"] == 1:
        value -= 25

    # combining more than 2 basic items is bad
    if len(item["basic_items"]) > 2:
        value -= 30

    return value


def decorations_apply_tool(tool, item):
    """Apply a tool to a decoration item."""
    new_item = item.copy()

    # Remove features that we don't want to carry over
    if "name" in new_item:
        del new_item["name"]
    if "emoji" in new_item:
        del new_item["emoji"]
    if "value" in new_item:
        del new_item["value"]

    # Ensure tool field is set to False for the result
    new_item["tool"] = False

    new_item["post_frame_messed_with"] = item["framed"]

    if tool["name"] == "pen":
        new_item["drawn_level"] = 1

    elif tool["name"] == "frame":
        new_item["framed"] = True

    elif tool["name"] == "scissors":
        # Only cut soft items, not hard ones
        new_item["cut_level"] = 1

    elif tool["name"] == "paint":
        new_item["paint_level"] = min(
            item["paint_level"] + 1, len(decorations_feature_names["paint_level"]) - 1
        )

    return new_item


def decorations_combination_function(item1, item2):
    """The overall combination function for the decorations domain."""

    # If they're both tools, return None
    if item1["tool"] and item2["tool"]:
        return None

    # If one item is a tool, apply it to the other item
    if item1["tool"]:
        new_item = decorations_apply_tool(item1, item2)
    elif item2["tool"]:
        new_item = decorations_apply_tool(item2, item1)
    else:
        # Combine two non-tool items
        new_item = {}

        # the hardness is the harder of the two
        new_item["hardness"] = (
            "hard"
            if item1["hardness"] == "hard" or item2["hardness"] == "hard"
            else "soft"
        )

        # the paint level is the highest of the two
        new_item["paint_level"] = max(item1["paint_level"], item2["paint_level"])

        # the cut level the lowest of the two
        new_item["cut_level"] = min(item1["cut_level"], item2["cut_level"])

        # the drawn level is the highest of the two
        new_item["drawn_level"] = max(item1["drawn_level"], item2["drawn_level"])

        new_item["material_types"] = item1["material_types"] + item2["material_types"]
        new_item["basic_items"] = item1["basic_items"] + item2["basic_items"]

        # if either is framed, the result is framed, but also messed with
        new_item["framed"] = item1["framed"] or item2["framed"]
        new_item["post_frame_messed_with"] = item1["framed"] or item2["framed"]

    # Calculate value
    new_item["tool"] = False
    new_item["value"] = decorations_value_function(new_item)

    return new_item


# ANIMALS DOMAIN FUNCTIONS

animals_feature_names = {
    "mutation_level": ["normal", "mutant", "super-mutant", "corrupted"],
    "growth_level": ["normal", "jumbo", "colossal"],
    "metabolic_level": ["normal", "accelerated"],
}


def animals_value_function(item):
    """Calculate the value of a genetic creation based on its features."""
    value = 0  # No base value for animals

    # POSITIVE UTILITY

    # small species get better with two levels of growth
    if item["size"] == "small":
        value += 15 * item["growth_level"]
    # medium species get better with one level of growth
    elif item["size"] == "medium":
        if item["growth_level"] == 1:
            value += 15
        elif item["growth_level"] == 2:
            value -= 15
    # large species get worse with any level of growth
    elif item["size"] == "large":
        value -= 15 * item["growth_level"]

    # second mutation is good
    if item["mutation_level"] == 2:
        value += 30

    # metabolic level is good for carnivores and omnivores
    if item["diet_type"] in ["carnivore", "omnivore"]:
        value += 30 * item["metabolic_level"]

    # different unique habitats are good
    n_unique_habitats = len(set(item["habitats"]))
    value += 20 * (n_unique_habitats - 1)

    # different original respiratory systems are good
    n_unique_original_respiratory_types = len(set(item["original_respiratory_types"]))
    value += 30 * (n_unique_original_respiratory_types - 1)

    # NEGATIVE UTILITY

    # combining more than two basic animals is bad
    if len(item["basic_animals"]) > 2:
        value -= 30 * (len(item["basic_animals"]) - 2)

    # confused breathing is bad
    if item["respiratory_type"] == "confused":
        value -= 30

    # metabolic acceleration is bad for herbivores
    elif item["diet_type"] == "herbivore":
        value -= 20 * item["metabolic_level"]

    # first mutation is bad
    if item["mutation_level"] == 1:
        value -= 15

    # third mutation is bad again
    elif item["mutation_level"] == 3:
        value -= 15

    return value


def animals_apply_tool(tool, item):
    """Apply a genetic tool to an animal."""
    new_item = item.copy()

    # Remove features that we don't want to carry over
    if "name" in new_item:
        del new_item["name"]
    if "emoji" in new_item:
        del new_item["emoji"]
    if "value" in new_item:
        del new_item["value"]

    # Ensure tool field is set to False for the result
    new_item["tool"] = False

    # the growth serum increases the growth level by 1
    if tool["name"] == "growth serum":
        new_item["growth_level"] = min(item["growth_level"] + 1, 2)

    # the mutation catalyst increases the mutation level by 1
    elif tool["name"] == "mutation catalyst":
        new_item["mutation_level"] = min(item["mutation_level"] + 1, 3)

    # the respiratory reconfigurer toggles the respiratory type
    elif tool["name"] == "respiratory reconfigurer":
        if item["respiratory_type"] == "gills":
            new_item["respiratory_type"] = "lungs"
        else:
            new_item["respiratory_type"] = "gills"

    # the metabolic accelerator sets the metabolic level to 1
    elif tool["name"] == "metabolic accelerator":
        new_item["metabolic_level"] = 1

    return new_item


def animals_combination_function(item1, item2):
    """The overall combination function for the animals domain."""

    # If they're both tools, return None
    if item1["tool"] and item2["tool"]:
        return None

    # If one item is a tool, apply it to the other item
    if item1["tool"]:
        new_item = animals_apply_tool(item1, item2)
    elif item2["tool"]:
        new_item = animals_apply_tool(item2, item1)
    else:
        # Combine two animals
        new_item = {}

        # the habitats are the union of the two
        new_item["habitats"] = item1["habitats"] + item2["habitats"]

        # the size is the smaller of the two
        size_map = {"small": 0, "medium": 1, "large": 2}
        inverse_size_map = {v: k for k, v in size_map.items()}
        new_item["size"] = inverse_size_map[
            min(size_map[item1["size"]], size_map[item2["size"]])
        ]

        # the growth level is the average of the two
        new_item["growth_level"] = math.floor(
            (item1["growth_level"] + item2["growth_level"]) / 2
        )

        # the mutation level is the higher of the two
        new_item["mutation_level"] = max(
            item1["mutation_level"], item2["mutation_level"]
        )

        # the metabolic level is the higher of the two
        new_item["metabolic_level"] = max(
            item1["metabolic_level"], item2["metabolic_level"]
        )

        # Handle respiratory type
        if item1["respiratory_type"] == item2["respiratory_type"]:
            new_item["respiratory_type"] = item1["respiratory_type"]
        else:
            new_item["respiratory_type"] = "confused"

        # Determine diet type (carnivore + herbivore makes omnivore)
        if item1["diet_type"] != item2["diet_type"]:
            new_item["diet_type"] = "omnivore"
        else:
            new_item["diet_type"] = item1["diet_type"]

        # Combine basic animals
        new_item["basic_animals"] = item1["basic_animals"] + item2["basic_animals"]

        new_item["original_respiratory_types"] = (
            item1["original_respiratory_types"] + item2["original_respiratory_types"]
        )

    # Calculate value
    new_item["tool"] = False
    new_item["value"] = animals_value_function(new_item)

    return new_item


# POTIONS DOMAIN FUNCTIONS

potions_feature_names = {
    "enchantment_level": ["unenchanted", "flickering", "glowing", "corrupted"],
}


def potions_value_function(item):
    """Calculate the value of a potion based on its features."""
    value = 0  # No base value for potions

    # POSITIVE UTILITY

    # Extracted, filtered, and ground things are good
    if item["extraction"] == "extracted":
        value += 20
    if item["filtering"] == "filtered":
        value += 20
    if item["grind"] == "ground":
        value += 20

    # twice enchanted things are good
    if item["enchantment_level"] == 2:
        value += 15

    # combining magical and non-magical things is good
    if True in item["magicalities"] and False in item["magicalities"]:
        value += 30

    # different states of matter are good
    value += 20 * (len(set(item["states_of_matter"])) - 1)

    # NEGATIVE UTILITY

    # botched things are bad
    if item["extraction"] == "botched":
        value -= 25
    if item["filtering"] == "botched":
        value -= 25
    if item["grind"] == "botched":
        value -= 25

    # first and third enchantments is bad
    if item["enchantment_level"] == 1:
        value -= 10
    if item["enchantment_level"] == 3:
        value -= 20

    # more than two ingredients is bad
    if len(item["basic_ingredients"]) > 2:
        value -= 20 * (len(item["basic_ingredients"]) - 2)

    return value


def potions_apply_tool(tool, item):
    """Apply a tool to a potion ingredient."""
    new_item = item.copy()

    # Remove features that we don't want to carry over
    if "name" in new_item:
        del new_item["name"]
    if "emoji" in new_item:
        del new_item["emoji"]
    if "value" in new_item:
        del new_item["value"]

    # Ensure tool field is set to False for the result
    new_item["tool"] = False

    # the vial extracts plant things and makes them liquid
    if tool["name"] == "vial" and item["extraction"] is None:
        if set(item["ingredient_types"]) == {"plant"}:
            new_item["extraction"] = "extracted"
        else:
            new_item["extraction"] = "botched"

        new_item["states_of_matter"] = ["liquid"]

    # the mortar grinds hard things
    elif tool["name"] == "mortar" and item["grind"] is None:
        if item["is_hard"]:
            # it becomes a ground powder
            new_item["grind"] = "ground"
        else:
            new_item["grind"] = "botched"

    # wand increases enchantment level
    elif tool["name"] == "wand":
        new_item["enchantment_level"] = min(item.get("enchantment_level", 0) + 1, 3)

    # the filter makes liquid things filtered
    elif tool["name"] == "filter" and item["filtering"] is None:
        if set(item["states_of_matter"]) == {"liquid"}:
            new_item["filtering"] = "filtered"
        else:
            new_item["filtering"] = "botched"

    new_item["value"] = potions_value_function(new_item)

    return new_item


def potions_combination_function(item1, item2):
    """The overall combination function for the potions domain."""

    # If they're both tools, return None
    if item1["tool"] and item2["tool"]:
        return None

    # If one item is a tool, apply it to the other item
    if item1["tool"]:
        new_item = potions_apply_tool(item1, item2)
    elif item2["tool"]:
        new_item = potions_apply_tool(item2, item1)
    else:
        # Combine two ingredients
        new_item = {}

        # add the states of matter
        new_item["states_of_matter"] = (
            item1["states_of_matter"] + item2["states_of_matter"]
        )

        # the result is hard if both ingredients are hard
        new_item["is_hard"] = item1["is_hard"] and item2["is_hard"]

        # add the ingredient types
        new_item["ingredient_types"] = (
            item1["ingredient_types"] + item2["ingredient_types"]
        )

        # the result is magical if either ingredient is magical
        new_item["magicalities"] = item1["magicalities"] + item2["magicalities"]

        # the enchantment level is the average of the two, rounded down
        new_item["enchantment_level"] = math.floor(
            (item1["enchantment_level"] + item2["enchantment_level"]) / 2
        )

        # if neither ingredient is filtered, the result is unfiltered
        if item1["filtering"] is None and item2["filtering"] is None:
            new_item["filtering"] = None
        elif item1["filtering"] == "botched" or item2["filtering"] == "botched":
            new_item["filtering"] = "botched"
        else:
            new_item["filtering"] = "filtered"

        # extraction works like filtering
        if item1["extraction"] is None and item2["extraction"] is None:
            new_item["extraction"] = None
        elif item1["extraction"] == "botched" or item2["extraction"] == "botched":
            new_item["extraction"] = "botched"
        else:
            new_item["extraction"] = "extracted"

        # grind works like extraction
        if item1["grind"] is None and item2["grind"] is None:
            new_item["grind"] = None
        elif item1["grind"] == "botched" or item2["grind"] == "botched":
            new_item["grind"] = "botched"
        else:
            new_item["grind"] = "ground"

        new_item["basic_ingredients"] = (
            item1["basic_ingredients"] + item2["basic_ingredients"]
        )

    # Calculate value
    new_item["tool"] = False
    new_item["value"] = potions_value_function(new_item)

    return new_item


COMBO_FUNCTIONS = {
    "cooking": cooking_combination_function,
    "decorations": decorations_combination_function,
    "animals": animals_combination_function,
    "potions": potions_combination_function,
}

FEATURE_NAMES = {
    "cooking": cooking_feature_names,
    "decorations": decorations_feature_names,
    "animals": animals_feature_names,
    "potions": potions_feature_names,
}

VALUE_FUNCTIONS = {
    "cooking": cooking_value_function,
    "decorations": decorations_value_function,
    "animals": animals_value_function,
    "potions": potions_value_function,
}
