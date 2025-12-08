from dataclasses import dataclass, field
from typing import Any, Union

from frozendict import frozendict


@dataclass(frozen=True)
class Item:
    name: str = ""
    emoji: str = ""


@dataclass(frozen=True)
class Tool(Item):
    tool: bool = True
    pass


@dataclass(frozen=True)
class NonTool(Item):
    value: int = 0
    features: Union[dict[str, Any], frozendict] = field(default_factory=dict)
    description: str = ""
    tool: bool = False


@dataclass(frozen=True)
class Ingredient(NonTool):
    pass


@dataclass(frozen=True)
class CombinedItem(NonTool):
    ingredients: list[Ingredient] = field(default_factory=list)


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

decorations_tools = [
    Tool(name="scissors", emoji="✂️"),
    Tool(name="frame", emoji="🖼️"),
]

decorations_ingredients = [
    Ingredient(
        name="leaf",
        emoji="🍃",
        value=0,
        features={
            "hardness": "soft",
            "cut_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
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
            "framed": False,
            "post_frame_messed_with": False,
            "type": "artificial",
        },
    ),
]

animals_tools = [
    Tool(name="growth serum", emoji="🌡️"),
    Tool(name="mutation catalyst", emoji="🧬"),
]

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


potions_tools = [
    Tool(name="vial", emoji="🧪"),
    Tool(name="filter", emoji="🧫"),
]

potions_ingredients = [
    Ingredient(
        name="frog leg",
        emoji="🐸",
        value=0,
        features={
            "state_of_matter": "solid",
            "magical": False,
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
            "magical": False,
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
            "magical": True,
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
            "magical": True,
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
            "magical": True,
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
            "magical": False,
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
            "magical": False,
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
            "magical": False,
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
            "magical": True,
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
            "magical": False,
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
            "magical": False,
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
            "magical": True,
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
            "magical": True,
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
            "magical": False,
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
            "magical": True,
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
            "magical": True,
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
            "magical": False,
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
            "magical": True,
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
            "magical": False,
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
            "magical": False,
            "filtering": None,
            "extraction": None,
        },
    ),
]


TOOLS = {
    "cooking": cooking_tools,
    "decorations": decorations_tools,
    "animals": animals_tools,
    "potions": potions_tools,
}

INGREDIENTS = {
    "cooking": cooking_ingredients,
    "decorations": decorations_ingredients,
    "animals": animals_ingredients,
    "potions": potions_ingredients,
}


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

SYSTEM_PROMPTS = {
    "cooking": cooking_system_prompt,
    "decorations": decorations_system_prompt,
    "animals": animals_system_prompt,
    "potions": potions_system_prompt,
}

cooking_ic_examples = [
    {
        "input": [
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
        "outcome": CombinedItem(
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
        "semantics": {"emoji": "🐟🍚", "name": "fish and rice dish"},
    },
    {
        "input": [
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
        "outcome": Ingredient(
            name="",
            emoji="",
            features={
                "cook_level": 1,
                "water_level": 0,
                "type": "vegetable",
            },
            value=20,
        ),
        "semantics": {"emoji": "🔥🥕", "name": "cooked carrot"},
    },
]

animals_ic_examples = [
    {
        "input": [
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
        "outcome": CombinedItem(
            ingredients=[
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
            features={},
            value=0,
        ),
        "semantics": {"emoji": "🐘🦒", "name": "elepharaffe"},
    },
    {
        "input": [
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
        "outcome": Ingredient(
            features={
                "size": "large",
                "mutation_level": 1,
                "growth_level": 1,
                "habitat": "water",
            },
            value=-10,
        ),
        "semantics": {"emoji": "⬆️🧬🐳", "name": "giant mutant whale"},
    },
]

potions_ic_examples = [
    {
        "input": [
            Ingredient(
                name="obsidian",
                emoji="⚫",
                value=0,
                features={
                    "state_of_matter": "solid",
                    "magical": False,
                    "filtering": None,
                    "extraction": None,
                },
            ),
            Tool(name="filter", emoji="🧫"),
        ],
        "outcome": Ingredient(
            features={
                "state_of_matter": "solid",
                "magical": False,
                "filtering": "botched",
                "extraction": None,
            },
            value=-20,
        ),
        "semantics": {"emoji": "🧫⚫", "name": "poorly-filtered obsidian"},
    },
    {
        "input": [
            Ingredient(
                name="rose petal extract",
                emoji="🧪🌹",
                value=30,
                features={
                    "state_of_matter": "liquid",
                    "magical": False,
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
                    "magical": True,
                    "filtering": None,
                    "extraction": None,
                },
            ),
        ],
        "outcome": CombinedItem(
            ingredients=[
                Ingredient(
                    name="rose petal extract",
                    emoji="🧪🌹",
                    value=30,
                    features={
                        "state_of_matter": "liquid",
                        "magical": False,
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
                        "magical": True,
                        "filtering": None,
                        "extraction": None,
                    },
                ),
            ],
            features={},
            value=-30,
        ),
        "semantics": {
            "emoji": "🌹🦄",
            "name": "rose potion with chunks of unicorn horn",
        },
    },
]

decorations_ic_examples = [
    {
        "input": [
            Ingredient(
                name="finely-cut beads",
                emoji="📿🖊️",
                value=25,
                features={
                    "type": "artificial",
                    "hardness": "hard",
                    "cut_level": 2,
                    "framed": False,
                    "post_frame_messed_with": False,
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
                    "framed": False,
                    "post_frame_messed_with": False,
                },
            ),
        ],
        "outcome": CombinedItem(
            ingredients=[
                Ingredient(
                    name="finely-cut beads",
                    emoji="📿🖊️",
                    value=25,
                    features={
                        "type": "artificial",
                        "hardness": "hard",
                        "cut_level": 2,
                        "framed": False,
                        "post_frame_messed_with": False,
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
                        "framed": False,
                        "post_frame_messed_with": False,
                    },
                ),
            ],
            features={"framed": False, "post_frame_messed_with": False},
            value=25,
        ),
        "semantics": {
            "emoji": "📿📰🖊",
            "name": "newspaper dotted with finely-cut beads",
        },
    },
    {
        "input": [
            Ingredient(
                name="sunflower",
                emoji="🌻",
                value=0,
                features={
                    "type": "natural",
                    "hardness": "soft",
                    "cut_level": 0,
                    "framed": False,
                    "post_frame_messed_with": False,
                },
            ),
            Tool(name="frame", emoji="🖼️"),
        ],
        "outcome": Ingredient(
            features={
                "type": "natural",
                "hardness": "soft",
                "cut_level": 0,
                "framed": False,
                "post_frame_messed_with": False,
            },
            value=20,
        ),
        "semantics": {"emoji": "🖼️🌻", "name": "framed sunflower"},
    },
]

IC_EXAMPLES = {
    "cooking": cooking_ic_examples,
    "decorations": decorations_ic_examples,
    "animals": animals_ic_examples,
    "potions": potions_ic_examples,
}
