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
        name="apple",
        emoji="🍎",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "fruit",
        },
    ),
    Ingredient(
        name="banana",
        emoji="🍌",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "fruit",
        },
    ),
    Ingredient(
        name="carrot",
        emoji="🥕",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="egg",
        emoji="🥚",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "eggs and dairy",
        },
    ),
    Ingredient(
        name="raw fish",
        emoji="🐟",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "meat",
        },
    ),
    Ingredient(
        name="raw meat",
        emoji="🥩",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "meat",
        },
    ),
    Ingredient(
        name="rice",
        emoji="🌾",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "grain",
        },
    ),
    Ingredient(
        name="wheat",
        emoji="🌾",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "grain",
        },
    ),
    Ingredient(
        name="cheese",
        emoji="🧀",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "eggs and dairy",
        },
    ),
    Ingredient(
        name="butter",
        emoji="🧈",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "eggs and dairy",
        },
    ),
    Ingredient(
        name="lettuce",
        emoji="🥬",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="tomato",
        emoji="🍅",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="onion",
        emoji="🧅",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "aromatic",
        },
    ),
    Ingredient(
        name="ginger",
        emoji="🫚",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "aromatic",
        },
    ),
    Ingredient(
        name="potato",
        emoji="🥔",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="mushroom",
        emoji="🍄",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "vegetable",
        },
    ),
    Ingredient(
        name="pepper",
        emoji="🌶️",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "aromatic",
        },
    ),
    Ingredient(
        name="coconut",
        emoji="🥥",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "fruit",
        },
    ),
    Ingredient(
        name="pineapple",
        emoji="🍍",
        value=0,
        features={
            "salt_level": 0,
            "cook_level": 0,
            "water_level": 0,
            "chop_level": 0,
            "type": "fruit",
        },
    ),
]

cooking_tools = [
    Tool(name="water", emoji="💧"),
    Tool(name="knife", emoji="🔪"),
    Tool(name="stove", emoji="🔥"),
    Tool(name="salt", emoji="🧂"),
]

decorations_tools = [
    Tool(name="scissors", emoji="✂️"),
    Tool(name="paint", emoji="🎨"),
    Tool(name="frame", emoji="🖼️"),
    Tool(name="pen", emoji="🖊️"),
]

decorations_ingredients = [
    Ingredient(
        name="leaf",
        emoji="🍃",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="rock",
        emoji="🪨",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="wood",
        emoji="🪵",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="paper",
        emoji="📄",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="yarn",
        emoji="🧶",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="flower",
        emoji="🌸",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="sunflower",
        emoji="🌻",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="thread",
        emoji="🧵",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="mushroom",
        emoji="🍄",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="feather",
        emoji="🪶",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="shell",
        emoji="🐚",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="pinecone",
        emoji="🌲",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="acorn",
        emoji="🌰",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="bark",
        emoji="🪵",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
        },
    ),
    Ingredient(
        name="beads",
        emoji="📿",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="ribbon",
        emoji="🎀",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="cardboard",
        emoji="📦",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="newspaper",
        emoji="📰",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="buttons",
        emoji="🔘",
        value=0,
        features={
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
    Ingredient(
        name="glitter",
        emoji="✨",
        value=0,
        features={
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 0,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["artificial"],
        },
    ),
]

animals_tools = [
    Tool(name="growth serum", emoji="🌡️"),
    Tool(name="mutation catalyst", emoji="🧬"),
    Tool(name="respiratory reconfigurer", emoji="🌀"),
    Tool(name="metabolic accelerator", emoji="⚡"),
]


animals_ingredients = [
    Ingredient(
        name="trout",
        emoji="🐟",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "respiratory_type": "gills",
            "original_respiratory_types": ["gills"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["water"],
        },
    ),
    Ingredient(
        name="shark",
        emoji="🦈",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "respiratory_type": "gills",
            "original_respiratory_types": ["gills"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["water"],
        },
    ),
    Ingredient(
        name="octopus",
        emoji="🐙",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "respiratory_type": "gills",
            "original_respiratory_types": ["gills"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["water"],
        },
    ),
    Ingredient(
        name="squid",
        emoji="🦑",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "respiratory_type": "gills",
            "original_respiratory_types": ["gills"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["water"],
        },
    ),
    Ingredient(
        name="crab",
        emoji="🦀",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "respiratory_type": "gills",
            "original_respiratory_types": ["gills"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["water"],
        },
    ),
    Ingredient(
        name="pufferfish",
        emoji="🐡",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "respiratory_type": "gills",
            "original_respiratory_types": ["gills"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["water"],
        },
    ),
    Ingredient(
        name="snake",
        emoji="🐍",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="frog",
        emoji="🐸",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="bird",
        emoji="🐦‍⬛",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "omnivore",
            "habitats": ["air"],
        },
    ),
    Ingredient(
        name="bee",
        emoji="🐝",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "herbivore",
            "habitats": ["air"],
        },
    ),
    Ingredient(
        name="butterfly",
        emoji="🦋",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "herbivore",
            "habitats": ["air"],
        },
    ),
    Ingredient(
        name="lizard",
        emoji="🦎",
        value=0,
        features={
            "size": "small",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="elephant",
        emoji="🐘",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "herbivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="whale",
        emoji="🐳",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["water"],
        },
    ),
    Ingredient(
        name="panda",
        emoji="🐼",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "herbivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="kangaroo",
        emoji="🦘",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "herbivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="lion",
        emoji="🦁",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "carnivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="giraffe",
        emoji="🦒",
        value=0,
        features={
            "size": "large",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "herbivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="zebra",
        emoji="🦓",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "herbivore",
            "habitats": ["land"],
        },
    ),
    Ingredient(
        name="monkey",
        emoji="🐒",
        value=0,
        features={
            "size": "medium",
            "mutation_level": 0,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 0,
            "diet_type": "omnivore",
            "habitats": ["land"],
        },
    ),
]


potions_tools = [
    Tool(name="vial", emoji="🧪"),
    Tool(name="mortar", emoji="🏺"),
    Tool(name="wand", emoji="🪄"),
    Tool(name="filter", emoji="🧫"),
]

potions_ingredients = [
    Ingredient(
        name="frog leg",
        emoji="🐸",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": False,
            "ingredient_types": ["animal"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="bat wing",
        emoji="🦇",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": False,
            "ingredient_types": ["animal"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="dragon scale",
        emoji="🐉",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": True,
            "ingredient_types": ["animal"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="unicorn horn",
        emoji="🦄",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": True,
            "ingredient_types": ["animal"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="mandrake root",
        emoji="🌱",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": False,
            "ingredient_types": ["plant"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="mushroom",
        emoji="🍄",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": False,
            "ingredient_types": ["plant"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="dandelion",
        emoji="🌼",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": False,
            "ingredient_types": ["plant"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="rose petal",
        emoji="🌹",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": False,
            "ingredient_types": ["plant"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="sunstone",
        emoji="☀️",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": True,
            "ingredient_types": ["mineral"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="obsidian",
        emoji="⚫",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": True,
            "ingredient_types": ["mineral"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="amber",
        emoji="🟠",
        value=0,
        features={
            "states_of_matter": ["solid"],
            "is_hard": True,
            "ingredient_types": ["mineral"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="whispering wind",
        emoji="🌬️",
        value=0,
        features={
            "states_of_matter": ["gas"],
            "is_hard": False,
            "ingredient_types": ["essence"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="ghostly vapor",
        emoji="👻",
        value=0,
        features={
            "states_of_matter": ["gas"],
            "is_hard": False,
            "ingredient_types": ["essence"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="volcanic fumes",
        emoji="🌋",
        value=0,
        features={
            "states_of_matter": ["gas"],
            "is_hard": False,
            "ingredient_types": ["essence"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="dragon's breath",
        emoji="🔥",
        value=0,
        features={
            "states_of_matter": ["gas"],
            "is_hard": False,
            "ingredient_types": ["essence"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="basilisk venom",
        emoji="⚗️",
        value=0,
        features={
            "states_of_matter": ["liquid"],
            "is_hard": False,
            "ingredient_types": ["animal"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="morning dew",
        emoji="💧",
        value=0,
        features={
            "states_of_matter": ["liquid"],
            "is_hard": False,
            "ingredient_types": ["essence"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="kraken ink",
        emoji="🦑",
        value=0,
        features={
            "states_of_matter": ["liquid"],
            "is_hard": False,
            "ingredient_types": ["animal"],
            "magicalities": [True],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="honey nectar",
        emoji="🍯",
        value=0,
        features={
            "states_of_matter": ["liquid"],
            "is_hard": False,
            "ingredient_types": ["plant"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
        },
    ),
    Ingredient(
        name="tree sap",
        emoji="🌳",
        value=0,
        features={
            "states_of_matter": ["liquid"],
            "is_hard": False,
            "ingredient_types": ["plant"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": None,
            "extraction": None,
            "grind": None,
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
You are controlling the semantics of a cooking game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji that describe the item. The name should be informative and make it possible for the player to know the relevant features so they can learn the rules. The emoji should describe the item and its features. When in doubt it is safe to combine the emoji of the two items. If the new item has different features than any of the original items, it must get a new name.

Please keep the following rules in mind:
- If an item's salt level is salted, its name should include "salted". If it is oversalted, it should include "oversalted".
- If an item's cook level is cooked, its name should include "cooked". If it is overcooked, it should include "overcooked".
- If an item's water level is soaked, its name should include "soaked".
- If an item's chop level is chopped, its name should include "chopped".
- If an item has been cooked, it should not include the word "raw" in the name.
- Give complex dishes descriptive names rather than just listing their ingredients.

In general, the name should give the participant some sense of why the item's value is the way it is.

Please respond in JSON format, with double quotes around all strings.
"""

decorations_system_prompt = """
You are controlling the semantics of a decoration-making game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji that describe the item. The name should be informative and make it possible for the player to know the relevant features so they can learn the rules. The emoji should describe the item and its features. When in doubt it is safe to combine the emoji of the two items. If the new item has different features than any of the original items, it must get a new name.

Please keep the following rules in mind:
- If an item's paint level is painted, its name should include "painted". If it is overpainted, it should include "messy".
- If an item's cut level is cut, its name should include "cut"
- If an item's drawn level is drawn and it is on an artificial material, its name should include "drawn-on." If it is on a natural material, it should include "scribbled-on."
- If an item is framed, its name should include "framed."
- If an item has post-frame-messed-with, it should not have "framed" in its name anymore and have "with ruined frame" at the end of its name.
- Combinations of different decoration parts should retain at least parts of the names of the original parts.

In general, the name should give the participant some sense of why the item's value is the way it is.

Please respond in JSON format, with double quotes around all strings.
"""

animals_system_prompt = """
You are controlling the semantics of a hybrid animal creation game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji that describe the item. The name should be informative and make it possible for the player to know the relevant features so they can learn the rules. The emoji should describe the item and its features. When in doubt it is safe to combine the emoji of the two items. If the new item has different features than any of the original items, it must get a new name.

Please keep the following rules in mind:
- If an animal's respiratory type is not the same as its original respiratory type, its name should include "with gills" or "with lungs", depending on the new respiratory type. If the respiratory type is "confused", it should include "with breathing problems".
- The animal's mutation level is mutant, super-mutant, or corrupted, it should be included in the name.
- If an animal's growth level is jumbo or colossal, its name should include the growth level.
- If an animal is a herbivore and its metabolic level is "accelerated", its name should include "starving". If it is a carnivore or omnivore, it should include "energetic".
- If an animal's list of habitats includes both land and water, its name should include "amphibious".
- Combinations of different animals should retain at least parts of the names of the original animals.

In general, the name should give the participant some sense of why the item's value is the way it is.

Please respond in JSON format, with double quotes around all strings.
"""

potions_system_prompt = """
You are controlling the semantics of a potion brewing game. You will see two items and the features of the item you get from combining them. Your job is to generate an appropriate name and string of up to three emoji that describe the item. The name should be informative and make it possible for the player to know the relevant features so they can learn the rules. The emoji should describe the item and its features. When in doubt it is safe to combine the emoji of the two items. If the new item has different features than any of the original items, it must get a new name.

Please keep the following rules in mind:
- An item that has an enchantment level of "flickering," "glowing," or "corrupted" should have its enchantment level in the name.
- If an item's filtering is "filtered," its name should include "filtered." If it is "botched," its name should include "with failed filtering"
- If an item's extraction is "extracted," its name should include "extracted." If it is "botched," its name should include "with botched extraction"
- If an item's grind is "ground," its name should include "ground". If it is "botched," its name should include "poorly ground"
- Combinations of different ingredients should retain at least parts of the names of the original ingredients.

In general, the name should give the participant some sense of why the item's value is the way it is.

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
                name="Chopped Potato",
                emoji="🔪🥔",
                value=0,
                features={
                    "salt_level": 0,
                    "cook_level": 0,
                    "water_level": 0,
                    "chop_level": 1,
                    "type": "vegetable",
                },
            ),
            Ingredient(
                name="Chopped Onion",
                emoji="🔪🧅",
                value=0,
                features={
                    "salt_level": 0,
                    "cook_level": 0,
                    "water_level": 0,
                    "chop_level": 1,
                    "type": "aromatic",
                },
            ),
        ],
        "outcome": CombinedItem(
            ingredients=[
                Ingredient(
                    name="Chopped Potato",
                    emoji="🔪🥔",
                    value=0,
                    features={
                        "salt_level": 0,
                        "cook_level": 0,
                        "water_level": 0,
                        "chop_level": 1,
                        "type": "vegetable",
                    },
                ),
                Ingredient(
                    name="Chopped Onion",
                    emoji="🔪🧅",
                    value=0,
                    features={
                        "salt_level": 0,
                        "cook_level": 0,
                        "water_level": 0,
                        "chop_level": 1,
                        "type": "aromatic",
                    },
                ),
            ],
            features={},
            value=0,
        ),
        "semantics": {"emoji": "🥔🧅", "name": "Chopped potato and onion"},
    },
    {
        "input": [
            Tool(
                name="stove",
                emoji="🔥",
            ),
            Ingredient(
                name="Chopped Carrot",
                emoji="🔪🥕",
                value=0,
                features={
                    "salt_level": 0,
                    "cook_level": 0,
                    "water_level": 0,
                    "chop_level": 1,
                    "type": "vegetable",
                },
            ),
        ],
        "outcome": Ingredient(
            features={
                "salt_level": 0,
                "cook_level": 1,
                "water_level": 0,
                "chop_level": 1,
                "type": "vegetable",
            },
            value=50,
        ),
        "semantics": {"emoji": "🥕🔥", "name": "Cooked Chopped Carrot"},
    },
    {
        "input": [
            Tool(
                name="water",
                emoji="💧",
            ),
            Ingredient(
                name="Rice",
                emoji="🌾",
                value=0,
                features={
                    "salt_level": 0,
                    "cook_level": 0,
                    "water_level": 0,
                    "chop_level": 0,
                    "type": "grain",
                },
            ),
        ],
        "outcome": Ingredient(
            features={
                "salt_level": 0,
                "cook_level": 0,
                "water_level": 1,
                "chop_level": 0,
                "type": "grain",
            },
        ),
        "semantics": {"emoji": "🌾💧", "name": "Soaked Rice"},
    },
]

animals_ic_examples = [
    {
        "input": [
            {
                "name": "elephant",
                "emoji": "🐘",
                "tool": False,
                "size": "large",
                "mutation_level": 0,
                "respiratory_type": "lungs",
                "original_respiratory_types": ["lungs"],
                "metabolic_level": 0,
                "growth_level": 0,
                "diet_type": "herbivore",
                "habitats": ["land"],
                "value": 0,
            },
            {
                "name": "giraffe",
                "emoji": "🦒",
                "tool": False,
                "size": "large",
                "mutation_level": 0,
                "respiratory_type": "lungs",
                "original_respiratory_types": ["lungs"],
                "metabolic_level": 0,
                "growth_level": 0,
                "diet_type": "herbivore",
                "habitats": ["land"],
                "value": 0,
            },
        ],
        "outcome": {
            "habitats": ["land", "land"],
            "size": "large",
            "growth_level": 0,
            "mutation_level": 0,
            "metabolic_level": 0,
            "respiratory_type": "lungs",
            "diet_type": "herbivore",
            "original_respiratory_types": ["lungs", "lungs"],
            "tool": False,
            "value": 0,
        },
        "semantics": {"emoji": "🐘🦒", "name": "elepharaffe"},
    },
    {
        "input": [
            {"name": "growth serum", "emoji": "🌡️", "tool": True},
            {
                "tool": False,
                "size": "large",
                "mutation_level": 1,
                "respiratory_type": "lungs",
                "original_respiratory_types": ["lungs"],
                "metabolic_level": 0,
                "growth_level": 0,
                "diet_type": "carnivore",
                "habitats": ["water"],
                "value": -15,
                "name": "mutant whale",
                "emoji": "🐳🧬",
            },
        ],
        "outcome": {
            "tool": False,
            "size": "large",
            "mutation_level": 1,
            "respiratory_type": "lungs",
            "original_respiratory_types": ["lungs"],
            "metabolic_level": 0,
            "growth_level": 1,
            "diet_type": "carnivore",
            "habitats": ["water"],
            "value": -30,
        },
        "semantics": {"emoji": "🐳🧬🌡", "name": "overgrown mutant whale"},
    },
]

potions_ic_examples = [
    {
        "input": [
            {
                "name": "obsidian",
                "emoji": "⚫",
                "tool": False,
                "states_of_matter": ["solid"],
                "is_hard": True,
                "ingredient_types": ["mineral"],
                "magicalities": [False],
                "enchantment_level": 0,
                "filtering": None,
                "extraction": None,
                "grind": None,
                "value": 0,
            },
            {"name": "filter", "emoji": "🧫", "tool": True},
        ],
        "outcome": {
            "tool": False,
            "states_of_matter": ["solid"],
            "is_hard": True,
            "ingredient_types": ["mineral"],
            "magicalities": [False],
            "enchantment_level": 0,
            "filtering": "botched",
            "extraction": None,
            "grind": None,
            "value": -25,
        },
        "semantics": {"emoji": "🧫⚫", "name": "obsidian with failed filtering"},
    },
    {
        "input": [
            {
                "tool": False,
                "states_of_matter": ["solid"],
                "is_hard": False,
                "ingredient_types": ["plant"],
                "magicalities": [False],
                "enchantment_level": 0,
                "filtering": "botched",
                "extraction": None,
                "grind": None,
                "value": -25,
                "name": "botched rose petal residue",
                "emoji": "🧫🌹",
            },
            {
                "name": "unicorn horn",
                "emoji": "🦄",
                "tool": False,
                "states_of_matter": ["solid"],
                "is_hard": True,
                "ingredient_types": ["animal"],
                "magicalities": [True],
                "enchantment_level": 0,
                "filtering": None,
                "extraction": None,
                "grind": None,
                "value": 0,
            },
        ],
        "outcome": {
            "states_of_matter": ["solid", "solid"],
            "is_hard": False,
            "ingredient_types": ["plant", "animal"],
            "magicalities": [False, True],
            "enchantment_level": 0,
            "filtering": "botched",
            "extraction": None,
            "grind": None,
            "tool": False,
            "value": 0,
        },
        "semantics": {
            "emoji": "🌹🦄",
            "name": "unicorn potion with botched rose petal residue",
        },
    },
]

decorations_ic_examples = [
    {
        "input": [
            {
                "tool": False,
                "hardness": "hard",
                "paint_level": 0,
                "cut_level": 0,
                "drawn_level": 1,
                "framed": False,
                "post_frame_messed_with": False,
                "material_types": ["artificial"],
                "value": 25,
                "name": "drawn-on beads",
                "emoji": "📿🖊️",
            },
            {
                "name": "newspaper",
                "emoji": "📰",
                "tool": False,
                "hardness": "soft",
                "paint_level": 0,
                "cut_level": 0,
                "drawn_level": 0,
                "framed": False,
                "post_frame_messed_with": False,
                "material_types": ["artificial"],
                "value": 0,
            },
        ],
        "outcome": {
            "hardness": "hard",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 1,
            "material_types": ["artificial", "artificial"],
            "framed": False,
            "post_frame_messed_with": False,
            "tool": False,
            "value": 25,
        },
        "semantics": {
            "emoji": "📿📰🖊",
            "name": "newspaper decoration with drawn-on beads",
        },
    },
    {
        "input": [
            {
                "name": "sunflower",
                "emoji": "🌻",
                "tool": False,
                "hardness": "soft",
                "paint_level": 0,
                "cut_level": 0,
                "drawn_level": 0,
                "framed": False,
                "post_frame_messed_with": False,
                "material_types": ["natural"],
                "value": 0,
            },
            {"name": "pen", "emoji": "🖊️", "tool": True},
        ],
        "outcome": {
            "tool": False,
            "hardness": "soft",
            "paint_level": 0,
            "cut_level": 0,
            "drawn_level": 1,
            "framed": False,
            "post_frame_messed_with": False,
            "material_types": ["natural"],
            "value": -25,
        },
        "semantics": {"emoji": "🌻🖊️", "name": "scribbled-on sunflower"},
    },
]

IC_EXAMPLES = {
    "cooking": cooking_ic_examples,
    "decorations": decorations_ic_examples,
    "animals": animals_ic_examples,
    "potions": potions_ic_examples,
}
