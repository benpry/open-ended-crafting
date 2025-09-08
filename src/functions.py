import random
from dataclasses import replace
from typing import Any

from src.constants import INGREDIENTS, CombinedItem, Ingredient, Item, NonTool, Tool


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

        bonuses = (13 + 1 / 3) * (n_distinct_ingredient_types - 1)
        if n_ingredients > 3:
            bonuses -= 100

        return sum(ingredient_values) + bonuses

    features = item.features
    value = 0

    # cook level bonuses
    if features["cook_level"] == 1:
        if (
            features["type"] == "grain"
            and features["water_level"] == 1
            or features["grain"] == "wheat"
            and features["water_level"] == 0
        ):
            value += 20
        else:
            value -= 15

    return value


cooking_feature_names = {
    "water_level": ["dry", "soaked"],
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

    elif tool.name == "stove":
        # otherwise, cooking increases the cook level by 1, up to the max
        new_features["cook_level"] = min(
            item.features["cook_level"] + 1,
            len(cooking_feature_names["cook_level"]) - 1,
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


decorations_feature_names = {
    "cut_level": ["not cut", "cut"],
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
            bonuses -= 100

        return sum(ingredient_values) + bonuses

    features = item.features

    if features["cut_level"] == 1:
        if features["hardness"] == "soft":
            value += 25
        else:
            value -= 30
    elif features["cut_level"] == 2:
        if features["hardness"] == "hard":
            value += 25
        else:
            value -= 30

    if features["framed"]:
        if features["post_frame_messed_with"]:
            value -= 50
        else:
            value += 20

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

    if tool.name == "frame":
        # the frame frames things
        new_features["framed"] = True

    elif tool.name == "scissors":
        # Only cut soft items, not hard ones
        new_features["cut_level"] = 1

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
    "growth_level": ["not grown", "grown", "super-grown", "ultra-grown"],
}


def animals_value_function(item):
    """Calculate the value of a genetic creation based on its features."""

    if isinstance(item, CombinedItem):
        ingredient_values = [
            animals_value_function(ingredient) for ingredient in item.ingredients
        ]

        # bonus for combining different ingredient types
        n_unique_habitats = len(set(x.features["habitat"] for x in item.ingredients))

        bonuses = 0

        # different habitats are good
        bonuses += 5 * (n_unique_habitats - 1)

        # combining more than two basic animals is bad
        if len(item.ingredients) > 3:
            bonuses -= 100

        return sum(ingredient_values) + bonuses

    features = item.features
    value = 0  # No base value for animals

    if features["growth_level"] == 1:
        if features["size"] == "large":
            value += 15
        elif features["size"] == "medium":
            value += 10
        else:
            value += 5

    elif features["growth_level"] == 2:
        if features["size"] == "large":
            value -= 15
        elif features["size"] == "medium":
            value += 15
        else:
            value += 10

    elif features["growth_level"] == 3:
        if features["size"] == "large":
            value -= 25
        elif features["size"] == "medium":
            value -= 15
        else:
            value += 15

    # second mutation is good
    if features["mutation_level"] == 1:
        value -= 15
    elif features["mutation_level"] == 2:
        value += 15
    elif features["mutation_level"] == 3:
        value -= 25

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

potions_feature_names = {}


def potions_value_function(item: Item) -> int:
    """Calculate the value of a potion based on its features."""

    if isinstance(item, CombinedItem):
        ingredient_values = [
            potions_value_function(ingredient) for ingredient in item.ingredients
        ]
        n_ingredients = len(item.ingredients)
        states_of_matter = set(x.features["state_of_matter"] for x in item.ingredients)
        magicalities = set(x.features["magical"] for x in item.ingredients)
        bonus = 0

        if len(magicalities) == 2:
            bonus += 40

        # including non-liquid things is bad
        if states_of_matter != {"liquid"} or n_ingredients > 2:
            bonus -= 100

        return sum(ingredient_values) + bonus

    features = item.features

    value = 0  # No base value for potions

    # Extracted, filtered, and ground things are good
    if features["extraction"] == "extracted":
        value += 30
    elif features["extraction"] == "botched":
        value -= 20
    if features["filtering"] == "filtered":
        value += 30
    elif features["extraction"] == "botched":
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
        if item.features["type"] == "plant" and item.features["filtering"] is None:
            new_features["extraction"] = "extracted"
            new_features["state_of_matter"] = "liquid"
        else:
            new_features["extraction"] = "botched"

    # the filter filters things and makes them liquid
    elif tool.name == "filter" and item.features["filtering"] is None:
        if (
            item.features["state_of_matter"] in ("liquid", "gas")
            and item.features["extraction"] is None
        ):
            new_features["filtering"] = "filtered"
            new_features["state_of_matter"] = "liquid"
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
    if features["cut_level"] > 0:
        descriptors.append(
            decorations_feature_names["cut_level"][features["cut_level"]]
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
    if item.features["growth_level"] > 0:
        descriptors.append(
            animals_feature_names["growth_level"][item.features["growth_level"]]
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


def cooking_get_inventory(n_items: int):
    # make sure that there is at least one meat, one vegetable, and one grain
    ingredients = INGREDIENTS["cooking"]
    vegetables = [item for item in ingredients if item.features["type"] == "vegetable"]
    meats = [item for item in ingredients if item.features["type"] == "meat"]
    grains = [item for item in ingredients if item.features["type"] == "grain"]

    # sample a vegetable, a meat, and a fruit
    vegetable = random.sample(vegetables, 1)[0]
    meat = random.sample(meats, 1)[0]
    grain = random.sample(grains, 1)[0]
    inventory = [vegetable, meat, grain]
    if n_items > 3:
        # sample some more ingredients
        remaining_ingredients = [
            item for item in ingredients if item not in [vegetable, meat, grain]
        ]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 3)
        inventory += remaining_ingredients

    return inventory


def decorations_get_inventory(n_items: int):
    ingredients = INGREDIENTS["decorations"]

    natural_ingredients = [
        item for item in ingredients if item.features["type"] == "natural"
    ]
    artificial_ingredients = [
        item for item in ingredients if item.features["type"] == "artificial"
    ]

    # at least one natural and one artificial
    inventory = random.sample(natural_ingredients, 1)
    inventory += random.sample(artificial_ingredients, 1)

    if n_items > 2:
        remaining_ingredients = [item for item in ingredients if item not in inventory]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 2)
        inventory += remaining_ingredients

    return inventory


def animals_get_inventory(n_items: int):
    # one small, one large, two medium. At least one of each habitat.
    ingredients = INGREDIENTS["animals"]
    inventory = random.sample(ingredients, 4)
    n_habitats = len(set([item.features["habitat"] for item in inventory]))
    n_small = len([item for item in inventory if item.features["size"] == "small"])
    n_large = len([item for item in inventory if item.features["size"] == "large"])
    n_medium = len([item for item in inventory if item.features["size"] == "medium"])
    while n_habitats < 3 or n_small < 1 or n_large < 1 or n_medium < 2:
        inventory = random.sample(ingredients, 4)
        n_habitats = len(set([item.features["habitat"] for item in inventory]))
        n_small = len([item for item in inventory if item.features["size"] == "small"])
        n_large = len([item for item in inventory if item.features["size"] == "large"])
        n_medium = len(
            [item for item in inventory if item.features["size"] == "medium"]
        )

    if n_items > 4:
        remaining_ingredients = [item for item in ingredients if item not in inventory]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 4)
        inventory += remaining_ingredients

    return inventory


def potions_get_inventory(n_items: int):
    # one plant, one non-plant solid, one gas, one magical, one mundane
    ingredients = INGREDIENTS["potions"]
    inventory = random.sample(ingredients, 3)
    n_plants = len([item for item in inventory if item.features["type"] == "plant"])
    n_non_plant_solids = len(
        [
            item
            for item in inventory
            if item.features["type"] != "plant"
            and item.features["state_of_matter"] == "solid"
        ]
    )
    n_gases = len(
        [item for item in inventory if item.features["state_of_matter"] == "gas"]
    )
    n_magical = len([item for item in inventory if item.features["magical"]])
    n_mundane = len([item for item in inventory if not item.features["magical"]])
    while (
        n_plants < 1
        or n_non_plant_solids < 1
        or n_gases < 1
        or n_magical < 1
        or n_mundane < 1
    ):
        inventory = random.sample(ingredients, 3)
        n_plants = len([item for item in inventory if item.features["type"] == "plant"])
        n_non_plant_solids = len(
            [
                item
                for item in inventory
                if item.features["type"] != "plant"
                and item.features["state_of_matter"] == "solid"
            ]
        )
        n_gases = len(
            [item for item in inventory if item.features["state_of_matter"] == "gas"]
        )
        n_magical = len([item for item in inventory if item.features["magical"]])
        n_mundane = len([item for item in inventory if not item.features["magical"]])

    if n_items > 3:
        remaining_ingredients = [item for item in ingredients if item not in inventory]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 3)
        inventory += remaining_ingredients

    return inventory


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

GET_INVENTORY_FUNCTIONS = {
    "cooking": cooking_get_inventory,
    "decorations": decorations_get_inventory,
    "animals": animals_get_inventory,
    "potions": potions_get_inventory,
}
