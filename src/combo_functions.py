from dataclasses import replace
from typing import Any

from src.constants import CombinedItem, Ingredient, Item, NonTool, Tool


def cooking_value_function(item: NonTool) -> int:
    if isinstance(item, CombinedItem):
        ingredient_values = [
            cooking_value_function(ingredient) for ingredient in item.ingredients
        ]

        # bonus for combining different ingredient types
        n_ingredients = len(item.ingredients)
        n_distinct_ingredient_types = len(
            set(x.features["type"] for x in item.ingredients)
        )
        n_duplicate_ingredient_types = n_ingredients - n_distinct_ingredient_types

        bonuses = 20 * (n_distinct_ingredient_types - 1)
        if n_ingredients > 3:
            bonuses -= 30 * (n_ingredients - 3)
        bonuses -= 20 * n_duplicate_ingredient_types

        return sum(ingredient_values) + bonuses

    features = item.features
    value = 0

    # cook level bonuses
    if features["cook_level"] == 1:
        if (
            features["type"] in {"vegetable", "aromatic"}
            and features["chop_level"] == 1
        ):
            value += 25
        elif features["type"] == "meat" and features["chop_level"] == 0:
            value += 25
        elif features["type"] == "grain" and features["water_level"] == 1:
            value += 30
        else:
            value -= 10
    elif features["cook_level"] == 2:
        value -= 30

    # chop level bonuses
    if features["chop_level"] == 1:
        if features["type"] in {"vegetable", "aromatic"}:
            value += 15
        else:
            value -= 10

    # salt bonuses
    if features["salt_level"] == 1:
        value += 20
    elif features["salt_level"] == 2:
        value -= 20

    if features["water_level"] == 1 and features["type"] != "grain":
        value -= 15

    return value


cooking_feature_names = {
    "water_level": ["dry", "soaked"],
    "chop_level": ["unchopped", "chopped"],
    "salt_level": ["unsalted", "salted", "oversalted"],
    "cook_level": ["raw", "cooked", "overcooked"],
}


def cooking_apply_tool(tool: Tool, item: NonTool) -> NonTool:
    if isinstance(item, CombinedItem):
        return replace(
            item,
            ingredients=[
                cooking_apply_tool(tool, ingredient) for ingredient in item.ingredients
            ],
        )

    new_features = item.features.copy()

    if tool.name == "water":
        # adding water always soaks something
        new_features["water_level"] = 1
        # If the item is cooked, soaking un-cooks it (but doesn't rescue burnt things)
        if item.features["cook_level"] == 1:
            new_features["cook_level"] = 0

    elif tool.name == "stove":
        # adjust the cook level
        new_features["edible"] = True  # cooking makes inedible things edible

        # otherwise, cooking increases the cook level by 1, up to the max
        new_features["cook_level"] = min(
            item.features["cook_level"] + 1,
            len(cooking_feature_names["cook_level"]) - 1,
        )

    # Knife increases chop level. You can't chop a soaked thing.
    elif tool.name == "knife":
        # increase the chop level
        new_features["chop_level"] = min(
            item.features["chop_level"] + 1,
            len(cooking_feature_names["chop_level"]) - 1,
        )

    elif tool.name == "salt":
        # increase the salt level
        new_features["salt_level"] = min(
            item.features["salt_level"] + 1,
            len(cooking_feature_names["salt_level"]) - 1,
        )

    return Ingredient(features=new_features)


def cooking_combination_function(item1: Item, item2: Item):
    """
    The overall combination function for the cooking domain.
    """

    # if they're both tools, return None:
    if isinstance(item1, Tool) and isinstance(item2, Tool):
        return None

    # if one item is a tool, apply it to the other item.
    if isinstance(item1, Tool):
        new_item = cooking_apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = cooking_apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        # combine two combined items
        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
        )
    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        new_item = CombinedItem(
            ingredients=item1.ingredients + [item2],
        )
    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        new_item = CombinedItem(
            ingredients=item2.ingredients + [item1],
        )
    else:
        # two ingredients
        new_item = CombinedItem(
            ingredients=[item1, item2],
        )

    new_item = replace(new_item, value=cooking_value_function(new_item))

    return new_item


# DECORATIONS DOMAIN FUNCTIONS

decorations_feature_names = {
    "paint_level": ["unpainted", "painted", "over-painted"],
    "cut_level": ["not cut", "cut"],
    "drawn_level": ["not drawn", "drawn"],
    "framed": {True: "framed", False: "not framed"},
    "post_frame_messed_with": {False: None, True: "ruined frame"},
}


def decorations_value_function(item):
    """Calculate the value of a decoration based on its features."""
    value = 0  # No base value

    if isinstance(item, CombinedItem):
        ingredient_values = [
            decorations_value_function(ingredient) for ingredient in item.ingredients
        ]

        # bonus for combining natural and artificial things
        bonuses = 0
        ingredient_types = set(x.features["type"] for x in item.ingredients)
        if "natural" in ingredient_types and "artificial" in ingredient_types:
            bonuses += 30

        if len(item.ingredients) > 2:
            bonuses -= 30 * (len(item.ingredients) - 2)

        return sum(ingredient_values) + bonuses

    features = item.features

    if features["cut_level"] == 1:
        if features["hardness"] == "soft":
            value += 20
        else:
            value -= 20

    if features["drawn_level"] == 1:
        if features["type"] == "artificial":
            value += 20
        else:
            value -= 20

    if features["paint_level"] == 1:
        value += 15
    elif features["paint_level"] == 2:
        value -= 25

    if features["framed"]:
        if features["post_frame_messed_with"]:
            value -= 50
        else:
            value += 25

    return value


def decorations_apply_tool(tool: Tool, item: NonTool) -> NonTool:
    """Apply a tool to a decoration item."""
    if isinstance(item, CombinedItem):
        if tool.name == "frame":
            if not item.features["framed"]:
                return replace(
                    item, features={"framed": True, "post_frame_messed_with": False}
                )
            else:
                return replace(
                    item, features={"framed": True, "post_frame_messed_with": True}
                )
        else:
            return replace(
                item,
                ingredients=[
                    decorations_apply_tool(tool, ingredient)
                    for ingredient in item.ingredients
                ],
            )

    new_features = item.features.copy()

    if tool.name == "pen":
        # the pen draws on something
        new_features["drawn_level"] = 1

    elif tool.name == "frame":
        # the frame frames things
        new_features["framed"] = True

    elif tool.name == "scissors":
        # Only cut soft items, not hard ones
        new_features["cut_level"] = 1

    elif tool.name == "paint":
        # paint increases the paint level
        new_features["paint_level"] = min(
            item.features["paint_level"] + 1,
            len(decorations_feature_names["paint_level"]) - 1,
        )

    return Ingredient(features=new_features)


def decorations_combination_function(item1: Item, item2: Item) -> Item:
    """The overall combination function for the decorations domain."""

    already_framed = (
        isinstance(item1, NonTool)
        and "framed" in item1.features
        and item1.features["framed"]
    ) or (
        isinstance(item2, NonTool)
        and "framed" in item2.features
        and item2.features["framed"]
    )

    # If they're both tools, return None
    if isinstance(item1, Tool) and isinstance(item2, Tool):
        return None

    # if one item is a tool, apply it to the other item.
    if isinstance(item1, Tool):
        new_item = decorations_apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = decorations_apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        # combine two combined items
        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
            features={"framed": False, "post_frame_messed_with": False},
        )
    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        new_item = CombinedItem(
            ingredients=item1.ingredients + [item2],
            features={"framed": False, "post_frame_messed_with": False},
        )
    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        new_item = CombinedItem(
            ingredients=item2.ingredients + [item1],
            features={"framed": False, "post_frame_messed_with": False},
        )
    else:
        # two ingredients
        new_item = CombinedItem(
            ingredients=[item1, item2],
            features={"framed": False, "post_frame_messed_with": False},
        )

    if already_framed:
        new_item.features["post_frame_messed_with"] = True

    new_item = replace(new_item, value=decorations_value_function(new_item))

    return new_item


# ANIMALS DOMAIN FUNCTIONS
animals_feature_names = {
    "mutation_level": ["not mutant", "mutant", "super-mutant", "corrupted"],
    "growth_level": ["not grown", "grown", "colossally grown"],
    "metabolic_level": ["normal metabolism", "accelerated metabolism"],
}


def animals_value_function(item):
    """Calculate the value of a genetic creation based on its features."""

    if isinstance(item, CombinedItem):
        ingredient_values = [
            animals_value_function(ingredient) for ingredient in item.ingredients
        ]

        # bonus for combining different ingredient types
        n_unique_habitats = len(set(x.features["habitat"] for x in item.ingredients))
        # respiratory types should be the same
        n_unique_respiratory_types = len(
            set(x.features["respiratory_type"] for x in item.ingredients)
        )

        bonuses = 0

        # different habitats are good
        bonuses += 20 * (n_unique_habitats - 1)

        # different respiratory systems are bad
        if n_unique_respiratory_types > 1:
            bonuses -= 30

        # combining more than two basic animals is bad
        if len(item.ingredients) > 3:
            bonuses -= 35 * (len(item.ingredients) - 2)

        return sum(ingredient_values) + bonuses

    features = item.features
    value = 0  # No base value for animals

    if features["growth_level"] == 1:
        if features["size"] == "small":
            value += 15
        elif features["size"] == "medium":
            value += 15
        else:
            value -= 15
    elif features["growth_level"] == 2:
        if features["size"] == "small":
            value += 25
        elif features["size"] == "medium":
            value -= 15
        else:
            value -= 30

    # second mutation is good
    if features["mutation_level"] == 1:
        value -= 15
    elif features["mutation_level"] == 2:
        value += 20
    elif features["mutation_level"] == 3:
        value -= 25

    # metabolic level is good for carnivores and omnivores
    if features["diet_type"] in ["carnivore", "omnivore"]:
        value += 20 * features["metabolic_level"]

    # metabolic acceleration is bad for herbivores
    elif features["diet_type"] == "herbivore":
        value -= 20 * features["metabolic_level"]

    return value


def animals_apply_tool(tool, item):
    """Apply a genetic tool to an animal."""

    if isinstance(item, CombinedItem):
        return replace(
            item,
            ingredients=[
                animals_apply_tool(tool, ingredient) for ingredient in item.ingredients
            ],
        )

    new_features = item.features.copy()

    if tool.name == "growth serum":
        new_features["growth_level"] = min(
            item.features["growth_level"] + 1,
            len(animals_feature_names["growth_level"]) - 1,
        )

    elif tool.name == "mutation catalyst":
        new_features["mutation_level"] = min(
            item.features["mutation_level"] + 1,
            len(animals_feature_names["mutation_level"]) - 1,
        )

    # the respiratory reconfigurer toggles the respiratory type
    elif tool.name == "respiratory reconfigurer":
        if item.features["respiratory_type"] == "gills":
            new_features["respiratory_type"] = "lungs"
        else:
            new_features["respiratory_type"] = "gills"

    # the metabolic accelerator sets the metabolic level to 1
    elif tool.name == "metabolic accelerator":
        new_features["metabolic_level"] = 1

    return Ingredient(features=new_features)


def animals_combination_function(item1, item2):
    """The overall combination function for the animals domain."""
    # if they're both tools, return None:
    if isinstance(item1, Tool) and isinstance(item2, Tool):
        return None

    # if one item is a tool, apply it to the other item.
    if isinstance(item1, Tool):
        new_item = animals_apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = animals_apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        # combine two combined items
        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
        )
    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        new_item = CombinedItem(
            ingredients=item1.ingredients + [item2],
        )
    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        new_item = CombinedItem(
            ingredients=item2.ingredients + [item1],
        )
    else:
        # two ingredients
        new_item = CombinedItem(
            ingredients=[item1, item2],
        )

    new_item = replace(new_item, value=animals_value_function(new_item))

    return new_item


# POTIONS DOMAIN FUNCTIONS

potions_feature_names = {
    "enchantment_level": ["unenchanted", "flickering", "glowing", "corrupted"],
}


def potions_value_function(item: Item) -> int:
    """Calculate the value of a potion based on its features."""

    if isinstance(item, CombinedItem):
        ingredient_values = [
            potions_value_function(ingredient) for ingredient in item.ingredients
        ]
        n_ingredients = len(item.ingredients)
        n_states_of_matter = len(
            set(x.features["state_of_matter"] for x in item.ingredients)
        )
        magicalities = set(x.features["magical"] for x in item.ingredients)
        bonus = 0
        if len(magicalities) == 2:
            bonus += 30

        # different states of matter are good
        bonus += 15 * (n_states_of_matter - 1)

        # combining more than two ingredients is bad
        if n_ingredients > 3:
            bonus -= 20 * (n_ingredients - 3)

        return sum(ingredient_values) + bonus

    features = item.features

    value = 0  # No base value for potions

    # Extracted, filtered, and ground things are good
    if features["extraction"] == "extracted":
        value += 20
    elif features["extraction"] == "botched":
        value -= 20
    if features["filtering"] == "filtered":
        value += 20
    elif features["extraction"] == "botched":
        value -= 20
    if features["grind"] == "ground":
        value += 20
    elif features["grind"] == "botched":
        value -= 20

    # twice enchanted things are good
    if features["enchantment_level"] == 1:
        value -= 15
    elif features["enchantment_level"] == 2:
        value += 15
    elif features["enchantment_level"] == 3:
        value -= 20

    return value


def potions_apply_tool(tool: Tool, item: NonTool) -> NonTool:
    """Apply a tool to a potion ingredient."""

    if isinstance(item, CombinedItem):
        return replace(
            item,
            ingredients=[
                potions_apply_tool(tool, ingredient) for ingredient in item.ingredients
            ],
        )

    new_features = item.features.copy()

    # the vial extracts plant things and makes them liquid
    if tool.name == "vial" and item.features["extraction"] is None:
        if item.features["type"] == "plant":
            new_features["extraction"] = "extracted"
            new_features["state_of_matter"] = "liquid"
        else:
            new_features["extraction"] = "botched"

    # the mortar grinds hard things
    elif tool.name == "mortar" and item.features["grind"] is None:
        if item.features["state_of_matter"] == "solid":
            # it becomes a ground powder
            new_features["grind"] = "ground"
        else:
            new_features["grind"] = "botched"

    # wand increases enchantment level
    elif tool.name == "wand":
        new_features["enchantment_level"] = min(
            item.features["enchantment_level"] + 1,
            len(potions_feature_names["enchantment_level"]) - 1,
        )

    # the filter makes liquid things filtered
    elif tool.name == "filter" and item.features["filtering"] is None:
        if item.features["state_of_matter"] == "liquid":
            new_features["filtering"] = "filtered"
        else:
            new_features["filtering"] = "botched"

    return Ingredient(features=new_features)


def potions_combination_function(item1, item2):
    """The overall combination function for the potions domain."""

    if isinstance(item1, Tool) and isinstance(item2, Tool):
        return None

    # If they're both tools, return None
    if isinstance(item1, Tool):
        new_item = potions_apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = potions_apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        # combine two combined items
        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
        )
    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        new_item = CombinedItem(
            ingredients=item1.ingredients + [item2],
        )
    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        new_item = CombinedItem(
            ingredients=item2.ingredients + [item1],
        )
    else:
        # two ingredients
        new_item = CombinedItem(
            ingredients=[item1, item2],
        )

    new_item = replace(new_item, value=potions_value_function(new_item))

    return new_item


def cooking_get_item_descriptor(item: NonTool) -> str:
    descriptors = []

    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {cooking_get_item_descriptor(x)}"
            for x in item.ingredients
        ]
        return "\n".join(ingredient_descriptors)

    if item.features["cook_level"] > 0:
        descriptors.append(
            cooking_feature_names["cook_level"][item.features["cook_level"]]
        )
    if item.features["water_level"] > 0:
        descriptors.append(
            cooking_feature_names["water_level"][item.features["water_level"]]
        )
    if item.features["chop_level"] > 0:
        descriptors.append(
            cooking_feature_names["chop_level"][item.features["chop_level"]]
        )
    if item.features["salt_level"] > 0:
        descriptors.append(
            cooking_feature_names["salt_level"][item.features["salt_level"]]
        )
    descriptors.append(item.features["type"])

    return ", ".join(descriptors)


def decorations_get_item_descriptor(item: dict[str, Any]) -> list[str]:
    descriptors = []

    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {decorations_get_item_descriptor(x)}"
            for x in item.ingredients
        ]
        return "\n".join(ingredient_descriptors)

    features = item.features

    if features["type"] == "natural":
        descriptors.append("natural")
    elif features["type"] == "artificial":
        descriptors.append("artificial")

    descriptors.append(features["hardness"])
    if features["paint_level"] > 0:
        descriptors.append(
            decorations_feature_names["paint_level"][features["paint_level"]]
        )
    if features["cut_level"] > 0:
        descriptors.append(
            decorations_feature_names["cut_level"][features["cut_level"]]
        )
    if features["drawn_level"] > 0:
        descriptors.append(
            decorations_feature_names["drawn_level"][features["drawn_level"]]
        )

    if features["framed"]:
        descriptors.append("framed")

    if features["post_frame_messed_with"]:
        descriptors.append("ruined frame")

    return ", ".join(descriptors)


habitat_descriptors = {
    "land": "lives on land",
    "water": "lives in the water",
    "air": "lives in the air",
}


def animals_get_item_descriptor(item: NonTool) -> str:
    descriptors = []

    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {animals_get_item_descriptor(x)}"
            for x in item.ingredients
        ]
        return "\n".join(ingredient_descriptors)

    descriptors.append(item.features["size"])
    descriptors.append(item.features["diet_type"])
    descriptors.append(item.features["respiratory_type"])
    if item.features["growth_level"] > 0:
        descriptors.append(
            animals_feature_names["growth_level"][item.features["growth_level"]]
        )
    if item.features["metabolic_level"] > 0:
        descriptors.append(
            animals_feature_names["metabolic_level"][item.features["metabolic_level"]]
        )
    if item.features["mutation_level"] > 0:
        descriptors.append(
            animals_feature_names["mutation_level"][item.features["mutation_level"]]
        )

    descriptors.append(habitat_descriptors[item.features["habitat"]])

    return ", ".join(descriptors)


def potions_get_item_descriptor(item: dict[str, Any]) -> list[str]:
    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {potions_get_item_descriptor(x)}"
            for x in item.ingredients
        ]
        return "\n".join(ingredient_descriptors)

    descriptors = []
    descriptors.append(item.features["state_of_matter"])

    if item.features["extraction"] is not None:
        if item.features["extraction"] == "botched":
            descriptors.append("botched extraction")
        else:
            descriptors.append("extracted")
    if item.features["filtering"] is not None:
        if item.features["filtering"] == "botched":
            descriptors.append("botched filtering")
        else:
            descriptors.append("filtered")
    if item.features["grind"] is not None:
        if item.features["grind"] == "botched":
            descriptors.append("botched grinding")
        else:
            descriptors.append("ground")
    if item.features["enchantment_level"] > 0:
        descriptors.append(
            potions_feature_names["enchantment_level"][
                item.features["enchantment_level"]
            ]
        )

    if item.features["magical"]:
        descriptors.append("magical")
    else:
        descriptors.append("mundane")

    descriptors.append(item.features["type"])

    return ", ".join(descriptors)


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

DESCRIPTOR_FUNCTIONS = {
    "cooking": cooking_get_item_descriptor,
    "decorations": decorations_get_item_descriptor,
    "animals": animals_get_item_descriptor,
    "potions": potions_get_item_descriptor,
}
