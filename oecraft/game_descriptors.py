import random
from dataclasses import asdict, replace
from inspect import getsource
from typing import Any

from oecraft.environment import GameDescriptor
from oecraft.types import (
    CombinedItem,
    ICExample,
    Ingredient,
    Item,
    ItemSemantics,
    NonTool,
    Tool,
)

cooking_ingredients = [
    Ingredient(
        name="raw fish",
        emoji="🐟",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "protein",
        },
    ),
    Ingredient(
        name="raw beef",
        emoji="🥩",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "protein",
        },
    ),
    Ingredient(
        name="raw bacon",
        emoji="🥓",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "protein",
        },
    ),
    Ingredient(
        name="raw beans",
        emoji="🫘",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "protein",
        },
    ),
    Ingredient(
        name="raw egg",
        emoji="🥚",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "protein",
        },
    ),
    Ingredient(
        name="carrot",
        emoji="🥕",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="lettuce",
        emoji="🥬",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="tomato",
        emoji="🍅",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="potato",
        emoji="🥔",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="mushroom",
        emoji="🍄",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="cucumber",
        emoji="🥒",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="broccoli",
        emoji="🥦",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="green beans",
        emoji="🫛",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="beet",
        emoji="🫜",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="pepper",
        emoji="🫑",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="corn",
        emoji="🌽",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "grain",
        },
    ),
    Ingredient(
        name="wheat",
        emoji="🌾",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "grain",
        },
    ),
    Ingredient(
        name="rice",
        emoji="🌾",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "grain",
        },
    ),
    Ingredient(
        name="tortilla",
        emoji="🫓",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "grain",
        },
    ),
    Ingredient(
        name="bread",
        emoji="🍞",
        value=0,
        features={
            "cook_level": 0,
            "water_level": 0,
            "type": "grain",
        },
    ),
]


cooking_tools = [
    Tool(name="stove", emoji="🔥"),
    Tool(name="water", emoji="💧"),
]


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

        bonuses = 20 * (n_distinct_ingredient_types - 1)
        if n_ingredients > 3:
            bonuses -= 100

        return sum(ingredient_values) + bonuses

    features = item.features
    value = 0

    # cook level bonuses
    if features["cook_level"] == 1:
        if (features["type"] == "grain" and features["water_level"] == 1) or (
            features["type"] != "grain" and features["water_level"] == 0
        ):
            value += 20
    elif features["cook_level"] == 2:
        value -= 15

    return round(value)


cooking_system_prompt = """
You are controlling the semantics of a cooking game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji to describe the item. The name should be informative and reasonable given the inputs and features. The emoji should describe the item. If the new item has different features than either of the items that combine to make it, it must get a new name.

Please keep the following rules in mind:
- If an item's cook level is cooked, its name should include "cooked". If it is overcooked, it should include "overcooked".
- If an item's water level is soaked, its name should include "soaked".
- If an item has been cooked, it should not include the word "raw" in the name.
- Give complex dishes descriptive names rather than just a list of their ingredients.
- A combined dish that has 4 or more ingredients in its ingredient list should have the word "overcomplicated" in the name.

Keep in mind that these rules only apply to the main item. For instance, if a dish has multiple ingredients, you don't need all of the descriptors for each ingredient in the overall name.

In general, the name should give the player some sense of why the item's value is the way it is.

Please respond in JSON format, with double quotes around all strings.
"""

cooking_feature_names = {
    "water_level": ["dry", "soaked"],
    "cook_level": ["raw", "cooked", "overcooked"],
}

cooking_naming_ic_examples = [
    ICExample(
        inputs=[
            Ingredient(
                name="cooked fish",
                emoji="🔥🐟",
                value=20,
                features={
                    "cook_level": 1,
                    "water_level": 0,
                    "type": "protein",
                },
            ),
            Ingredient(
                name="cooked rice",
                emoji="🍚",
                value=20,
                features={
                    "cook_level": 1,
                    "water_level": 1,
                    "type": "grain",
                },
            ),
        ],
        outcome=CombinedItem(
            ingredients=[
                Ingredient(
                    name="cooked fish",
                    emoji="🔥🐟",
                    value=20,
                    features={
                        "cook_level": 1,
                        "water_level": 0,
                        "type": "protein",
                    },
                ),
                Ingredient(
                    name="cooked rice",
                    emoji="🍚",
                    value=20,
                    features={
                        "cook_level": 1,
                        "water_level": 1,
                        "type": "grain",
                    },
                ),
            ],
            features={},
            value=60,
        ),
        semantics=ItemSemantics(emoji="🐟🍚", name="fish and rice dish"),
    ),
    ICExample(
        inputs=[
            Tool(
                name="stove",
                emoji="🔥",
            ),
            Ingredient(
                name="carrot",
                emoji="🥕",
                value=0,
                features={
                    "cook_level": 1,
                    "water_level": 0,
                    "type": "vegetable",
                },
            ),
        ],
        outcome=Ingredient(
            name="",
            emoji="",
            features={
                "cook_level": 1,
                "water_level": 0,
                "type": "vegetable",
            },
            value=20,
        ),
        semantics=ItemSemantics(emoji="🔥🥕", name="cooked carrot"),
    ),
]


def cooking_combination_function(item1: Item, item2: Item):
    """
    The overall combination function for the cooking domain.
    """

    def apply_tool(tool: Tool, item: NonTool) -> NonTool:
        if isinstance(item, CombinedItem):
            return replace(
                item,
                ingredients=[
                    apply_tool(tool, ingredient) for ingredient in item.ingredients
                ],
            )

        new_features = dict(item.features.copy())

        if tool.name == "water":
            # adding water always soaks something
            new_features["water_level"] = 1

        elif tool.name == "stove":
            # otherwise, cooking increases the cook level by 1, up to the max
            new_features["cook_level"] = min(
                item.features["cook_level"] + 1,
                2,  # max cook level is 2
            )

        return Ingredient(features=new_features)

    # if they're both tools, return None:
    if isinstance(item1, Tool) and isinstance(item2, Tool):
        return None

    # if one item is a tool, apply it to the other item.
    if isinstance(item1, Tool):
        new_item = apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        # combine two combined items
        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
        )
    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        new_item = CombinedItem(
            ingredients=item1.ingredients + (item2,),
        )
    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        new_item = CombinedItem(
            ingredients=item2.ingredients + (item1,),
        )
    else:
        # two ingredients
        new_item = CombinedItem(
            ingredients=[item1, item2],
        )

    return new_item


def cooking_get_inventory(n_items: int, all_ingredients: list[Ingredient]):
    # make sure that there is at least one protein, one vegetable, and one grain
    vegetables = [
        item for item in all_ingredients if item.features["type"] == "vegetable"
    ]
    proteins = [item for item in all_ingredients if item.features["type"] == "protein"]
    grains = [item for item in all_ingredients if item.features["type"] == "grain"]

    # sample a vegetable, a protein, and a grain
    vegetable = random.sample(vegetables, 1)[0]
    protein = random.sample(proteins, 1)[0]
    grain = random.sample(grains, 1)[0]
    inventory = [vegetable, protein, grain]
    if n_items > 3:
        # sample some more ingredients
        remaining_ingredients = [
            item for item in all_ingredients if item not in [vegetable, protein, grain]
        ]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 3)
        inventory += remaining_ingredients

    return inventory


def cooking_get_item_descriptor(item: NonTool, feature_names: dict) -> str:
    descriptors = []

    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {cooking_get_item_descriptor(x, feature_names)}"
            for x in item.ingredients
        ]
        return "\n".join(ingredient_descriptors)

    if item.features["cook_level"] > 0:
        descriptors.append(feature_names["cook_level"][item.features["cook_level"]])
    descriptors.append(item.features["type"])

    return ", ".join(descriptors)


cooking_game_descriptor = GameDescriptor(
    combination_fn=getsource(cooking_combination_function).replace(
        "cooking_combination_function", "combination_fn"
    ),
    value_fn=getsource(cooking_value_function).replace(
        "cooking_value_function", "value_fn"
    ),
    get_inventory_fn=getsource(cooking_get_inventory).replace(
        "cooking_get_inventory", "get_inventory_fn"
    ),
    descriptor_fn=getsource(cooking_get_item_descriptor).replace(
        "cooking_get_item_descriptor", "descriptor_fn"
    ),
    tools=[asdict(x) for x in cooking_tools],
    ingredients=[asdict(x) for x in cooking_ingredients],
    naming_system_prompt=cooking_system_prompt,
    feature_names=cooking_feature_names,
    naming_ic_examples=cooking_naming_ic_examples,
)


# DECORATIONS DOMAIN

decorations_ingredients = [
    Ingredient(
        name="leaf",
        emoji="🍃",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="rock",
        emoji="🪨",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="wood",
        emoji="🪵",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="paper",
        emoji="📄",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="yarn",
        emoji="🧶",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="flower",
        emoji="🌸",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="sunflower",
        emoji="🌻",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="thread",
        emoji="🧵",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="mushroom",
        emoji="🍄",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="feather",
        emoji="🪶",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="shell",
        emoji="🐚",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="pinecone",
        emoji="🌲",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="acorn",
        emoji="🌰",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="bark",
        emoji="🪵",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "natural",
        },
    ),
    Ingredient(
        name="beads",
        emoji="📿",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="ribbon",
        emoji="🎀",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="cardboard",
        emoji="📦",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="newspaper",
        emoji="📰",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="buttons",
        emoji="🔘",
        value=0,
        features={
            "hardness": "hard",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
    Ingredient(
        name="sponge",
        emoji="🧽",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": 0,
            "post_frame_messed_with": 0,
            "type": "artificial",
        },
    ),
]


decorations_tools = [
    Tool(name="scissors", emoji="✂️"),
    Tool(name="frame", emoji="🖼️"),
]


decorations_feature_names = {
    "cut_level": ["not cut", "cut", "finely cut"],
    "framed": ["not framed", "framed"],
    "post_frame_messed_with": ["frame intact", "ruined frame"],
}


decorations_system_prompt = """
You are controlling the semantics of a decoration-making game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji that describe the item. The name should be informative and make it possible for the player to know the relevant features so they can learn the rules. The emoji should describe the item and its features. When in doubt it is safe to combine the emoji of the two items. If the new item has different features than any of the original items, it must get a new name.

Please keep the following rules in mind:
- If an item's cut level is cut, its name should include "cut"
- If an item is framed, its name should include "framed."
- If an item has post-frame-messed-with, it should not have "framed" in its name anymore and have "with ruined frame" at the end of its name.
- Combined decorations should have descriptive names rather than just a list of their ingredients.
- A combined decoration that has 3 or more ingredients in its ingredient list should have the word "overcomplicated" in the name.

Keep in mind that these rules only apply to the main item. For instance, if a decoration has multiple ingredients, you don't need all of the descriptors for each ingredient in the overall name.

In general, the name should give the player some sense of why the item's value is the way it is.

Please respond in JSON format, with double quotes around all strings.
"""


decorations_naming_ic_examples = [
    ICExample(
        inputs=[
            Ingredient(
                name="finely-cut beads",
                emoji="📿🖊️",
                value=25,
                features={
                    "type": "artificial",
                    "hardness": "hard",
                    "cut_level": 2,
                    "framed": 0,
                    "post_frame_messed_with": 0,
                },
            ),
            Ingredient(
                name="newspaper",
                emoji="📰",
                value=0,
                features={
                    "type": "artificial",
                    "hardness": "soft",
                    "cut_level": 0,
                    "framed": 0,
                    "post_frame_messed_with": 0,
                },
            ),
        ],
        outcome=CombinedItem(
            ingredients=(
                Ingredient(
                    name="finely-cut beads",
                    emoji="📿🖊️",
                    value=25,
                    features={
                        "type": "artificial",
                        "hardness": "hard",
                        "cut_level": 2,
                        "framed": 0,
                        "post_frame_messed_with": 0,
                    },
                ),
                Ingredient(
                    name="newspaper",
                    emoji="📰",
                    value=0,
                    features={
                        "type": "artificial",
                        "hardness": "soft",
                        "cut_level": 0,
                        "framed": 0,
                        "post_frame_messed_with": 0,
                    },
                ),
            ),
            features={"framed": 0, "post_frame_messed_with": 0},
            value=25,
        ),
        semantics=ItemSemantics(
            emoji="📿📰🖊",
            name="newspaper dotted with finely-cut beads",
        ),
    ),
    ICExample(
        inputs=[
            Ingredient(
                name="sunflower",
                emoji="🌻",
                value=0,
                features={
                    "type": "natural",
                    "hardness": "soft",
                    "cut_level": 0,
                    "framed": 0,
                    "post_frame_messed_with": 0,
                },
            ),
            Tool(name="frame", emoji="🖼️"),
        ],
        outcome=Ingredient(
            features={
                "type": "natural",
                "hardness": "soft",
                "cut_level": 0,
                "framed": 0,
                "post_frame_messed_with": 0,
            },
            value=20,
        ),
        semantics=ItemSemantics(emoji="🖼️🌻", name="framed sunflower"),
    ),
]


def decorations_value_function(item: NonTool) -> int:
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

        if item.features["framed"]:
            if item.features["post_frame_messed_with"]:
                bonuses -= 50
            else:
                bonuses += 20

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


def decorations_combination_function(item1: Item, item2: Item) -> Item:
    """The overall combination function for the decorations domain."""

    def apply_tool(tool: Tool, item: NonTool) -> NonTool:
        """Apply a tool to a decoration item."""
        if isinstance(item, CombinedItem):
            if tool.name == "frame":
                if not item.features["framed"]:
                    return replace(
                        item, features={"framed": 1, "post_frame_messed_with": 0}
                    )
                else:
                    return replace(
                        item, features={"framed": 1, "post_frame_messed_with": 1}
                    )
            else:
                return replace(
                    item,
                    ingredients=[
                        apply_tool(tool, ingredient) for ingredient in item.ingredients
                    ],
                )

        new_features = dict(item.features.copy())

        if tool.name == "frame":
            # the frame frames things
            new_features["framed"] = 1

        elif tool.name == "scissors":
            # Only cut soft items, not hard ones
            new_features["cut_level"] = min(
                item.features["cut_level"] + 1,
                2,  # max cut level is 2
            )

        return Ingredient(features=new_features)

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
        new_item = apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        if item1.features["framed"] or item2.features["framed"]:
            new_features = {"framed": 1, "post_frame_messed_with": 1}
        else:
            new_features = {"framed": 0, "post_frame_messed_with": 0}

        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
            features=new_features,
        )

    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        if item1.features["framed"]:
            new_features = {"framed": 1, "post_frame_messed_with": 1}
        else:
            new_features = {"framed": 0, "post_frame_messed_with": 0}

        if item2.features["framed"]:
            item2_features = dict(item2.features.copy())
            item2_features["framed"] = 1
            item2_features["post_frame_messed_with"] = 1
            item2 = replace(
                item2,
                features=item2_features,
                name=item2.name.replace("framed", "") + " with ruined frame",
            )

        new_item = CombinedItem(
            ingredients=item1.ingredients + (item2,),
            features=new_features,
        )

    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        if item1.features["framed"]:
            item1_features = dict(item1.features.copy())
            item1_features["framed"] = 1
            item1_features["post_frame_messed_with"] = 1
            item1 = replace(
                item1,
                features=item1_features,
                name=item1.name.replace("framed", "") + " with ruined frame",
            )

        if item2.features["framed"]:
            new_features = {"framed": 1, "post_frame_messed_with": 1}
        else:
            new_features = {"framed": 0, "post_frame_messed_with": 0}

        new_item = CombinedItem(
            ingredients=item2.ingredients + (item1,),
            features=new_features,
        )
    else:
        if item1.features["framed"]:
            item1_features = dict(item1.features.copy())
            item1_features["framed"] = 1
            item1_features["post_frame_messed_with"] = 1
            item1 = replace(
                item1,
                features=item1_features,
            )

        if item2.features["framed"]:
            item2_features = dict(item2.features.copy())
            item2_features["framed"] = 1
            item2_features["post_frame_messed_with"] = 1
            item2 = replace(
                item2,
                features=item2_features,
            )

        new_item = CombinedItem(
            ingredients=(item1, item2),
            features={"framed": 0, "post_frame_messed_with": 0},
        )

    if already_framed:
        new_features = dict(new_item.features.copy())
        new_features["post_frame_messed_with"] = 1
        new_item = replace(new_item, features=new_features)

    return new_item


def decorations_get_inventory(n_items: int, all_ingredients: list[Ingredient]):
    natural_ingredients = [
        item for item in all_ingredients if item.features["type"] == "natural"
    ]
    artificial_ingredients = [
        item for item in all_ingredients if item.features["type"] == "artificial"
    ]

    # at least one natural and one artificial
    inventory = random.sample(natural_ingredients, 1)
    inventory += random.sample(artificial_ingredients, 1)

    if n_items > 2:
        remaining_ingredients = [
            item for item in all_ingredients if item not in inventory
        ]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 2)
        inventory += remaining_ingredients

    return inventory


def decorations_get_item_descriptor(item: NonTool, feature_names: dict) -> str:
    descriptors = []

    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {decorations_get_item_descriptor(x, feature_names)}"
            for x in item.ingredients
        ]
        return "\\n".join(ingredient_descriptors)

    features = item.features

    if features["type"] == "natural":
        descriptors.append("natural")
    elif features["type"] == "artificial":
        descriptors.append("artificial")

    descriptors.append(features["hardness"])
    if features["cut_level"] > 0:
        descriptors.append(feature_names["cut_level"][features["cut_level"]])

    if features["framed"]:
        descriptors.append("framed")

    if features["post_frame_messed_with"]:
        descriptors.append("ruined frame")

    return ", ".join(descriptors)


decorations_game_descriptor = GameDescriptor(
    combination_fn=getsource(decorations_combination_function).replace(
        "decorations_combination_function", "combination_fn"
    ),
    value_fn=getsource(decorations_value_function).replace(
        "decorations_value_function", "value_fn"
    ),
    get_inventory_fn=getsource(decorations_get_inventory).replace(
        "decorations_get_inventory", "get_inventory_fn"
    ),
    descriptor_fn=getsource(decorations_get_item_descriptor).replace(
        "decorations_get_item_descriptor", "descriptor_fn"
    ),
    tools=[asdict(x) for x in decorations_tools],
    ingredients=[asdict(x) for x in decorations_ingredients],
    naming_system_prompt=decorations_system_prompt,
    feature_names=decorations_feature_names,
    naming_ic_examples=decorations_naming_ic_examples,
)


# ANIMALS DOMAIN

animals_ingredients = [
    Ingredient(
        name="trout",
        emoji="🐟",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "water",
        },
    ),
    Ingredient(
        name="shark",
        emoji="🦈",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "water",
        },
    ),
    Ingredient(
        name="octopus",
        emoji="🐙",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "water",
        },
    ),
    Ingredient(
        name="squid",
        emoji="🦑",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "water",
        },
    ),
    Ingredient(
        name="crab",
        emoji="🦀",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "water",
        },
    ),
    Ingredient(
        name="pufferfish",
        emoji="🐡",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "water",
        },
    ),
    Ingredient(
        name="snake",
        emoji="🐍",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="frog",
        emoji="🐸",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="bird",
        emoji="🐦‍⬛",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "air",
        },
    ),
    Ingredient(
        name="bee",
        emoji="🐝",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "air",
        },
    ),
    Ingredient(
        name="butterfly",
        emoji="🦋",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "air",
        },
    ),
    Ingredient(
        name="lizard",
        emoji="🦎",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="elephant",
        emoji="🐘",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="whale",
        emoji="🐳",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "water",
        },
    ),
    Ingredient(
        name="panda",
        emoji="🐼",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="kangaroo",
        emoji="🦘",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="lion",
        emoji="🦁",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="giraffe",
        emoji="🦒",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="zebra",
        emoji="🦓",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
    Ingredient(
        name="monkey",
        emoji="🐒",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "growth_level": 0,
            "habitat": "land",
        },
    ),
]


animals_tools = [
    Tool(name="growth serum", emoji="🌡️"),
    Tool(name="mutation catalyst", emoji="🧬"),
]


animals_feature_names = {
    "mutation_level": ["not mutant", "mutant", "super-mutant", "corrupted"],
    "growth_level": ["not grown", "grown", "super-grown", "ultra-grown"],
}


animals_system_prompt = """
You are controlling the semantics of a hybrid animal creation game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji that describe the item. The name should be informative and make it possible for the player to know the relevant features so they can learn the rules. The emoji should describe the item and its features. When in doubt it is safe to combine the emoji of the two items. If the new item has different features than any of the original items, it must get a new name.

Please keep the following rules in mind:
- The animal's mutation level is "mutant", "super-mutant", or "corrupted", it should be included in the name.
- If an animal's growth level is "grown", "super-grown", or "ultra-grown", it should be included in the name.
- If an animal's list of habitats includes both land and water, its name should include "amphibious". If it includes air and something other than air, it should include "flying".
- Combined animals should have descriptive names rather than just a list of their ingredients.
- A combined animal that has 4 or more ingredients in its ingredient list should have the word "overcomplicated" in the name.

Keep in mind that these rules only apply to the main item. For instance, if an animal has multiple ingredients, you don't need all of the descriptors for each ingredient in the overall name.

In general, the name should give the player some sense of why the item's value is the way it is.

Please respond in JSON format, with double quotes around all strings.
"""


animals_naming_ic_examples = [
    ICExample(
        inputs=[
            Ingredient(
                name="elephant",
                emoji="🐘",
                value=0,
                features={
                    "size": "large",
                    "mutation_level": 0,
                    "growth_level": 0,
                    "habitat": "land",
                },
            ),
            Ingredient(
                name="giraffe",
                emoji="🦒",
                value=0,
                features={
                    "size": "large",
                    "mutation_level": 0,
                    "growth_level": 0,
                    "habitat": "land",
                },
            ),
        ],
        outcome=CombinedItem(
            ingredients=(
                Ingredient(
                    name="elephant",
                    emoji="🐘",
                    value=0,
                    features={
                        "size": "large",
                        "mutation_level": 0,
                        "growth_level": 0,
                        "habitat": "land",
                    },
                ),
                Ingredient(
                    name="giraffe",
                    emoji="🦒",
                    value=0,
                    features={
                        "size": "large",
                        "mutation_level": 0,
                        "growth_level": 0,
                        "habitat": "land",
                    },
                ),
            ),
            features={},
            value=0,
        ),
        semantics=ItemSemantics(emoji="🐘🦒", name="elepharaffe"),
    ),
    ICExample(
        inputs=[
            Tool(name="growth serum", emoji="🌡️"),
            Ingredient(
                name="mutant whale",
                emoji="🧬🐳",
                value=-15,
                features={
                    "size": "large",
                    "mutation_level": 1,
                    "growth_level": 0,
                    "habitat": "water",
                },
            ),
        ],
        outcome=Ingredient(
            features={
                "size": "large",
                "mutation_level": 1,
                "growth_level": 1,
                "habitat": "water",
            },
            value=-10,
        ),
        semantics=ItemSemantics(emoji="⬆️🧬🐳", name="giant mutant whale"),
    ),
]


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


def animals_combination_function(item1, item2):
    """The overall combination function for the animals domain."""

    # if they're both tools, return None:
    def apply_tool(tool, item):
        """Apply a genetic tool to an animal."""

        if isinstance(item, CombinedItem):
            return replace(
                item,
                ingredients=[
                    apply_tool(tool, ingredient) for ingredient in item.ingredients
                ],
            )

        new_features = dict(item.features.copy())

        if tool.name == "growth serum":
            new_features["growth_level"] = min(
                item.features["growth_level"] + 1,
                3,
            )

        elif tool.name == "mutation catalyst":
            new_features["mutation_level"] = min(
                item.features["mutation_level"] + 1,
                3,
            )

        return Ingredient(features=new_features)

    if isinstance(item1, Tool) and isinstance(item2, Tool):
        return None

    # if one item is a tool, apply it to the other item.
    if isinstance(item1, Tool):
        new_item = apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        # combine two combined items
        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
        )
    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        new_item = CombinedItem(
            ingredients=item1.ingredients + (item2,),
        )
    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        new_item = CombinedItem(
            ingredients=item2.ingredients + (item1,),
        )
    else:
        # two ingredients
        new_item = CombinedItem(
            ingredients=(item1, item2),
        )

    return new_item


habitat_descriptors = {
    "land": "lives on land",
    "water": "lives in the water",
    "air": "lives in the air",
}


def animals_get_item_descriptor(item: NonTool, feature_names: dict) -> str:
    habitat_descriptors = {
        "land": "lives on land",
        "water": "lives in the water",
        "air": "lives in the air",
    }
    descriptors = []

    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {animals_get_item_descriptor(x, feature_names)}"
            for x in item.ingredients
        ]
        return "\\n".join(ingredient_descriptors)

    descriptors.append(item.features["size"])
    if item.features["growth_level"] > 0:
        descriptors.append(feature_names["growth_level"][item.features["growth_level"]])

    if item.features["mutation_level"] > 0:
        descriptors.append(
            feature_names["mutation_level"][item.features["mutation_level"]]
        )

    descriptors.append(habitat_descriptors[item.features["habitat"]])

    return ", ".join(descriptors)


def animals_get_inventory(n_items: int, all_ingredients: list[Ingredient]):
    # one small, one large, two medium. At least one of each habitat.
    land_animals = [
        item for item in all_ingredients if item.features["habitat"] == "land"
    ]
    water_animals = [
        item for item in all_ingredients if item.features["habitat"] == "water"
    ]
    air_animals = [
        item for item in all_ingredients if item.features["habitat"] == "air"
    ]

    inventory = random.sample(land_animals, 1)
    inventory += random.sample(water_animals, 1)
    inventory += random.sample(air_animals, 1)

    if n_items > 3:
        remaining_ingredients = [
            item for item in all_ingredients if item not in inventory
        ]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 3)
        inventory += remaining_ingredients

    return inventory


animals_game_descriptor = GameDescriptor(
    combination_fn=getsource(animals_combination_function).replace(
        "animals_combination_function", "combination_fn"
    ),
    value_fn=getsource(animals_value_function).replace(
        "animals_value_function", "value_fn"
    ),
    get_inventory_fn=getsource(animals_get_inventory).replace(
        "animals_get_inventory", "get_inventory_fn"
    ),
    descriptor_fn=getsource(animals_get_item_descriptor).replace(
        "animals_get_item_descriptor", "descriptor_fn"
    ),
    tools=[asdict(x) for x in animals_tools],
    ingredients=[asdict(x) for x in animals_ingredients],
    naming_system_prompt=animals_system_prompt,
    feature_names=animals_feature_names,
    naming_ic_examples=animals_naming_ic_examples,
)


# POTIONS DOMAIN

potions_ingredients = [
    Ingredient(
        name="frog leg",
        emoji="🐸",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="bat wing",
        emoji="🦇",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="dragon scale",
        emoji="🐉",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="unicorn horn",
        emoji="🦄",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="mandrake root",
        emoji="🌱",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="mushroom",
        emoji="🍄",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="dandelion",
        emoji="🌼",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="rose petal",
        emoji="🌹",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="sunstone",
        emoji="☀️",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="obsidian",
        emoji="⚫",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="amber",
        emoji="🟠",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="whispering wind",
        emoji="🌬️",
        value=0,
        features={
            "state_of_matter": "gas",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="ghostly vapor",
        emoji="👻",
        value=0,
        features={
            "state_of_matter": "gas",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="volcanic fumes",
        emoji="🌋",
        value=0,
        features={
            "state_of_matter": "gas",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="dragon's breath",
        emoji="🔥",
        value=0,
        features={
            "state_of_matter": "gas",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="basilisk venom",
        emoji="⚗️",
        value=0,
        features={
            "state_of_matter": "liquid",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="morning dew",
        emoji="💧",
        value=0,
        features={
            "state_of_matter": "liquid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="kraken ink",
        emoji="🦑",
        value=0,
        features={
            "state_of_matter": "liquid",
            "magical": 1,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="honey nectar",
        emoji="🍯",
        value=0,
        features={
            "state_of_matter": "liquid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
    Ingredient(
        name="tree sap",
        emoji="🌳",
        value=0,
        features={
            "state_of_matter": "liquid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        },
    ),
]


potions_tools = [
    Tool(name="vial", emoji="🧪"),
    Tool(name="filter", emoji="🧫"),
]


potions_feature_names = {
    "magical": ["mundane", "magical"],
}


potions_system_prompt = """
You are controlling the semantics of a potion brewing game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji that describe the item. The name should be informative and make it possible for the player to know the relevant features so they can learn the rules. The emoji should describe the item and its features. When in doubt it is safe to combine the emoji of the two items. If the new item has different features than any of the original items, it must get a new name.

Please keep the following rules in mind:
- If an item's filtering is "filtered," its name should include "filtered." If it is "botched," its name should include "poorly-filtered"
- If an item's extraction is "extracted," its name should include the word "extract" or "extracted". If it is "botched," its name should include "with failed extraction"
- Combined potions should have descriptive names rather than just a list of their ingredients.
- A combined potion that has 3 or more ingredients in its ingredient list should have the word "overcomplicated" in the name.

Keep in mind that these rules only apply to the main item. For instance, if a potion has multiple ingredients, you don't need all of the descriptors for each ingredient in the overall name.

In general, the name should give the player some sense of why the item's value is the way it is.

Please respond in JSON format, with double quotes around all strings.
"""


potions_naming_ic_examples = [
    ICExample(
        inputs=[
            Ingredient(
                name="obsidian",
                emoji="⚫",
                value=0,
                features={
                    "state_of_matter": "solid",
                    "magical": 0,
                    "filtering": None,
                    "extraction": None,
                },
            ),
            Tool(name="filter", emoji="🧫"),
        ],
        outcome=Ingredient(
            features={
                "state_of_matter": "solid",
                "magical": 0,
                "filtering": "botched",
                "extraction": None,
            },
            value=-20,
        ),
        semantics=ItemSemantics(emoji="🧫⚫", name="poorly-filtered obsidian"),
    ),
    ICExample(
        inputs=[
            Ingredient(
                name="rose petal extract",
                emoji="🧪🌹",
                value=30,
                features={
                    "state_of_matter": "liquid",
                    "magical": 0,
                    "filtering": None,
                    "extraction": "extracted",
                },
            ),
            Ingredient(
                name="unicorn horn",
                emoji="🦄",
                value=0,
                features={
                    "state_of_matter": "solid",
                    "magical": 1,
                    "filtering": None,
                    "extraction": None,
                },
            ),
        ],
        outcome=CombinedItem(
            ingredients=(
                Ingredient(
                    name="rose petal extract",
                    emoji="🧪🌹",
                    value=30,
                    features={
                        "state_of_matter": "liquid",
                        "magical": 0,
                        "filtering": None,
                        "extraction": "extracted",
                    },
                ),
                Ingredient(
                    name="unicorn horn",
                    emoji="🦄",
                    value=0,
                    features={
                        "state_of_matter": "solid",
                        "magical": 1,
                        "filtering": None,
                        "extraction": None,
                    },
                ),
            ),
            features={},
            value=-30,
        ),
        semantics=ItemSemantics(
            emoji="🌹🦄",
            name="rose potion with chunks of unicorn horn",
        ),
    ),
]


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
    elif features["filtering"] == "botched":
        value -= 20

    return value


def potions_combination_function(item1, item2):
    """The overall combination function for the potions domain."""

    def apply_tool(tool: Tool, item: NonTool) -> NonTool:
        """Apply a tool to a potion ingredient."""

        if isinstance(item, CombinedItem):
            return replace(
                item,
                ingredients=[
                    apply_tool(tool, ingredient) for ingredient in item.ingredients
                ],
            )

        new_features = dict(item.features.copy())

        # the vial extracts plant things and makes them liquid
        if tool.name == "vial" and item.features["extraction"] is None:
            if (
                item.features["state_of_matter"] == "solid"
                and item.features["filtering"] is None
            ):
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

    if isinstance(item1, Tool) and isinstance(item2, Tool):
        return None

    # If they're both tools, return None
    if isinstance(item1, Tool):
        new_item = apply_tool(item1, item2)
    elif isinstance(item2, Tool):
        new_item = apply_tool(item2, item1)
    elif isinstance(item1, CombinedItem) and isinstance(item2, CombinedItem):
        # combine two combined items
        new_item = CombinedItem(
            ingredients=item1.ingredients + item2.ingredients,
        )
    elif isinstance(item1, CombinedItem) and isinstance(item2, Ingredient):
        new_item = CombinedItem(
            ingredients=item1.ingredients + (item2,),
        )
    elif isinstance(item1, Ingredient) and isinstance(item2, CombinedItem):
        new_item = CombinedItem(
            ingredients=item2.ingredients + (item1,),
        )
    else:
        # two ingredients
        new_item = CombinedItem(
            ingredients=(item1, item2),
        )

    return new_item


def potions_get_item_descriptor(item: dict[str, Any], feature_names: dict) -> list[str]:
    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {potions_get_item_descriptor(x, feature_names)}"
            for x in item.ingredients
        ]
        return "\\n".join(ingredient_descriptors)

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

    if item.features["magical"]:
        descriptors.append("magical")
    else:
        descriptors.append("mundane")

    return ", ".join(descriptors)


def potions_get_inventory(n_items: int, all_ingredients: list[Ingredient]):
    # one plant, one non-plant solid, one gas, one magical, one mundane
    magical_ingredients = [item for item in all_ingredients if item.features["magical"]]
    mundane_ingredients = [
        item for item in all_ingredients if not item.features["magical"]
    ]
    inventory = random.sample(magical_ingredients, 1)
    inventory += random.sample(mundane_ingredients, 1)

    if n_items > 2:
        remaining_ingredients = [
            item for item in all_ingredients if item not in inventory
        ]
        remaining_ingredients = random.sample(remaining_ingredients, n_items - 2)
        inventory += remaining_ingredients

    return inventory


potions_game_descriptor = GameDescriptor(
    combination_fn=getsource(potions_combination_function).replace(
        "potions_combination_function", "combination_fn"
    ),
    value_fn=getsource(potions_value_function).replace(
        "potions_value_function", "value_fn"
    ),
    get_inventory_fn=getsource(potions_get_inventory).replace(
        "potions_get_inventory", "get_inventory_fn"
    ),
    descriptor_fn=getsource(potions_get_item_descriptor).replace(
        "potions_get_item_descriptor", "descriptor_fn"
    ),
    tools=[asdict(x) for x in potions_tools],
    ingredients=[asdict(x) for x in potions_ingredients],
    naming_system_prompt=potions_system_prompt,
    feature_names=potions_feature_names,
    naming_ic_examples=potions_naming_ic_examples,
)

GAME_DESCRIPTORS = {
    "cooking": cooking_game_descriptor,
    "decorations": decorations_game_descriptor,
    "animals": animals_game_descriptor,
    "potions": potions_game_descriptor,
}
