import math


def cooking_value_function(item):
    # inedible things are worth 0
    if not item["edible"]:
        return 0

    value = 0

    # Base value for edible items
    value += 2

    # CORE COOKING PRINCIPLES (high rewards for understanding these)

    # Perfect Preparation Bonus: Chopped (1) + Cooked (1) = +25 points
    if item["chop_level"] == 1 and item["cook_level"] == 1:
        value += 25

    # Soup Mastery: Cooked (1) + Water (1) = +20 points
    if item["cook_level"] == 1 and item["water_level"] == 1:
        value += 20

    # Seasoning Mastery: Salt (1) + any preparation = +15 points
    if item["salt_level"] == 1 and (item["chop_level"] > 0 or item["cook_level"] > 0):
        value += 15

    # Ultimate Dish: Chopped + Cooked + Water + Salt = +50 points total
    if (
        item["chop_level"] == 1
        and item["cook_level"] == 1
        and item["water_level"] == 1
        and item["salt_level"] == 1
    ):
        value += 10  # Additional bonus on top of individual bonuses

    # Ingredient Harmony: Exactly 2 different ingredient types = +10
    ingredient_type_count = len(item["ingredient_types"])
    if ingredient_type_count == 2:
        value += 10

    # HARSH PENALTIES FOR POOR UNDERSTANDING

    # Raw disasters
    if item["cook_level"] == 0 and len(item["all_ingredients"]) > 1:
        value -= 15  # Raw mixed dishes are terrible

    # Water misuse
    if item["water_level"] == 1 and item["cook_level"] == 0:
        value -= 20  # Raw soggy food is awful

    # Overcooking disasters
    if item["cook_level"] == 2:  # burnt
        value -= 25  # Burnt food is really bad

    # Over-seasoning disasters
    if item["salt_level"] >= 2:  # oversalted
        value -= 20

    # Over-chopping disasters
    if item["chop_level"] == 2:  # eviscerated
        value -= 15

    # Ingredient chaos - too many types
    if ingredient_type_count > 2:
        value -= 10 * (ingredient_type_count - 2)

    # Too many total ingredients
    if len(item["all_ingredients"]) > 3:
        value -= 15 * (len(item["all_ingredients"]) - 3)

    # Single ingredient type penalty (no harmony)
    if ingredient_type_count == 1 and len(item["all_ingredients"]) > 1:
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


# DECORATIONS DOMAIN FUNCTIONS

decorations_feature_names = {
    "paint_level": ["unpainted", "painted", "over-painted"],
    "cut_level": ["uncut", "cut"],
    "decorated_level": ["undecorated", "decorated"],
}


def decorations_value_function(item):
    """Calculate the value of a decoration based on its features."""
    value = 1  # Base value

    # MASTERY BONUSES (high rewards for understanding material properties)

    # Artistic Mastery: Pen on artificial materials = +20
    if (
        item.get("material_type") == "artificial"
        and item.get("decorated_level", 0) == 1
    ):
        value += 20

    # Woodworking Mastery: Saw on wood = +25
    if item.get("material_type") == "wood" and item.get("cut_level", 0) == 1:
        value += 25

    # Precision Cutting: Scissors on soft materials = +20
    if (
        item.get("hardness") == "soft"
        and item.get("cut_level", 0) == 1
        and item.get("material_type") != "wood"
    ):  # Not wood (that's for saw)
        value += 20

    # Perfect Paint Job: First paint application = +15
    if item.get("paint_level", 0) == 1:
        value += 15

    # COMBINATION MASTERY BONUSES

    # Nature-Art Fusion: Natural + Artificial materials = +25
    if item.get("has_natural", False) and item.get("has_artificial", False):
        value += 25

    # Texture Harmony: Soft + Hard materials = +20
    if item.get("has_soft", False) and item.get("has_hard", False):
        value += 20

    # ULTIMATE CREATION BONUS
    # Multi-process masterpiece: Cut + Painted + Decorated = +30
    if (
        item.get("cut_level", 0) >= 1
        and item.get("paint_level", 0) >= 1
        and item.get("decorated_level", 0) >= 1
    ):
        value += 30

    # HARSH PENALTIES FOR POOR UNDERSTANDING

    # Wrong tool penalties
    if item.get("material_type") == "natural" and item.get("decorated_level", 0) == 1:
        value -= 25  # Pen on natural is bad

    if (
        item.get("material_type") != "wood"
        and item.get("cut_level", 0) == 1
        and item.get("hardness") == "hard"
    ):
        value -= 25  # Wrong cutting tool

    # Overprocessing penalties
    if item.get("paint_level", 0) >= 2:
        value -= 30  # Over-painted is terrible

    # Material chaos - too many basic items
    basic_count = item.get("basic_item_count", 0)
    if basic_count > 2:
        value -= 20 * (basic_count - 2)  # Harsh penalty for clutter

    # No processing penalty (raw materials aren't valuable)
    if (
        item.get("cut_level", 0) == 0
        and item.get("paint_level", 0) == 0
        and item.get("decorated_level", 0) == 0
        and basic_count > 1
    ):
        value -= 15  # Multiple raw materials combined badly

    return max(value, 0)


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

    if tool["name"] == "pen":
        new_item["decorated_level"] = 1

    elif tool["name"] == "saw":
        new_item["cut_level"] = 1

    elif tool["name"] == "scissors":
        # Only cut soft items, not hard ones
        if item.get("hardness") == "soft":
            new_item["cut_level"] = 1
        else:
            new_item["cut_level"] = (
                1  # Still mark as cut but value function handles penalty
            )

    elif tool["name"] == "paint":
        new_item["paint_level"] = min(item.get("paint_level", 0) + 1, 2)

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

        # Track material types for combination bonuses
        new_item["has_natural"] = (
            item1.get("material_type") == "natural" or item1.get("has_natural", False)
        ) or (
            item2.get("material_type") == "natural" or item2.get("has_natural", False)
        )
        new_item["has_artificial"] = (
            item1.get("material_type") == "artificial"
            or item1.get("has_artificial", False)
        ) or (
            item2.get("material_type") == "artificial"
            or item2.get("has_artificial", False)
        )
        new_item["has_soft"] = (
            item1.get("hardness") == "soft" or item1.get("has_soft", False)
        ) or (item2.get("hardness") == "soft" or item2.get("has_soft", False))
        new_item["has_hard"] = (
            item1.get("hardness") == "hard" or item1.get("has_hard", False)
        ) or (item2.get("hardness") == "hard" or item2.get("has_hard", False))

        # Determine primary material type (prefer artificial if mixed)
        if (
            item1.get("material_type") == "artificial"
            or item2.get("material_type") == "artificial"
        ):
            new_item["material_type"] = "artificial"
        elif (
            item1.get("material_type") == "wood" or item2.get("material_type") == "wood"
        ):
            new_item["material_type"] = "wood"
        else:
            new_item["material_type"] = "natural"

        # Determine hardness (prefer hard if mixed)
        if item1.get("hardness") == "hard" or item2.get("hardness") == "hard":
            new_item["hardness"] = "hard"
        else:
            new_item["hardness"] = "soft"

        # Preserve highest levels
        new_item["paint_level"] = max(
            item1.get("paint_level", 0), item2.get("paint_level", 0)
        )
        new_item["cut_level"] = max(
            item1.get("cut_level", 0), item2.get("cut_level", 0)
        )
        new_item["decorated_level"] = max(
            item1.get("decorated_level", 0), item2.get("decorated_level", 0)
        )

        # Combine basic items
        new_item["basic_items"] = item1.get("basic_items", []) + item2.get(
            "basic_items", []
        )
        new_item["basic_item_count"] = item1.get("basic_item_count", 0) + item2.get(
            "basic_item_count", 0
        )

    # Calculate value
    new_item["tool"] = False
    new_item["value"] = decorations_value_function(new_item)

    return new_item


# GENETICS DOMAIN FUNCTIONS

genetics_feature_names = {
    "mutation_level": ["normal", "mutant", "super-mutant", "corrupted"],
    "metabolic_level": ["normal", "enhanced"],
}


def genetics_value_function(item):
    """Calculate the value of a genetic creation based on its features."""
    value = 3  # Base value for all animals

    # EVOLUTION MASTERY BONUSES (high rewards for understanding genetics)

    # Optimal Growth: Growth serum on small animals = +30
    if item.get("growth_applied", False) and item.get("original_size") == "small":
        value += 30

    # Perfect Mutation: Second-level mutation = +25
    if item.get("mutation_level", 0) == 2:
        value += 25

    # Metabolic Enhancement: Accelerator on carnivores/omnivores = +20
    if item.get("metabolic_level", 0) == 1 and item.get("diet_type") in [
        "carnivore",
        "omnivore",
    ]:
        value += 20

    # ULTIMATE EVOLUTION BONUSES

    # Amphibious Mastery: Gills + Lungs + Mutation + Reconfiguration = +40
    if (
        item.get("has_gills_animal", False)
        and item.get("has_lungs_animal", False)
        and item.get("reconfigured_respiratory", False)
        and item.get("mutation_level", 0) >= 1
    ):
        value += 40

    # Perfect Hybrid: Exactly 2 families from same habitat = +35
    if (
        item.get("families")
        and len(set(item["families"])) == 2
        and "habitats" in item
        and len(set(item["habitats"])) == 1
    ):
        value += 35

    # Size Perfection: Same-size breeding = +15
    if item.get("size_variance", 1) == 0:  # No size difference
        value += 15

    # MEGA EVOLUTION: Growth + Mutation + Metabolic + Perfect Hybrid = +50
    if (
        item.get("growth_applied", False)
        and item.get("mutation_level", 0) >= 2
        and item.get("metabolic_level", 0) >= 1
        and item.get("families")
        and len(set(item["families"])) == 2
    ):
        value += 50

    # HARSH PENALTIES FOR POOR BREEDING

    # Wrong growth application
    if item.get("growth_applied", False) and item.get("original_size") == "large":
        value -= 30  # Growth on large animals is terrible

    # Mutation disasters
    if item.get("mutation_level", 0) == 1:
        value -= 20  # First mutation is unstable
    if item.get("mutation_level", 0) >= 3:
        value -= 40  # Over-mutation is catastrophic

    # Metabolic mismatch
    if item.get("metabolic_level", 0) == 1 and item.get("diet_type") == "herbivore":
        value -= 25  # Metabolic boost on herbivores is bad

    # Size incompatibility disaster
    if item.get("size_variance", 0) >= 2:  # Large vs small
        value -= 35  # Terrible genetic mismatch

    # Habitat chaos
    if "habitats" in item and len(set(item["habitats"])) > 2:
        value -= 25 * (len(set(item["habitats"])) - 2)

    # Family chaos
    if item.get("families") and len(set(item["families"])) > 3:
        value -= 20 * (len(set(item["families"])) - 3)

    # Too many animals penalty
    if item.get("basic_animal_count", 0) > 2:
        value -= 30 * (item.get("basic_animal_count", 0) - 2)

    # Random mixing penalty
    if item.get("basic_animal_count", 0) > 1 and not any(
        [
            item.get("growth_applied", False),
            item.get("mutation_level", 0) > 0,
            item.get("metabolic_level", 0) > 0,
            item.get("reconfigured_respiratory", False),
        ]
    ):
        value -= 20  # Raw breeding without enhancement

    return max(value, 0)


def genetics_apply_tool(tool, item):
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

    if tool["name"] == "growth serum":
        new_item["growth_applied"] = True
        new_item["original_size"] = item.get("size", "medium")

    elif tool["name"] == "mutation catalyst":
        new_item["mutation_level"] = min(item.get("mutation_level", 0) + 1, 3)

    elif tool["name"] == "respiratory reconfigurer":
        # Toggle respiratory type
        if item.get("respiratory_type") == "gills":
            new_item["respiratory_type"] = "lungs"
        else:
            new_item["respiratory_type"] = "gills"
        new_item["reconfigured_respiratory"] = True
        # Track the original type for hybrid bonus
        if item.get("respiratory_type") == "gills":
            new_item["has_gills_animal"] = True
        else:
            new_item["has_lungs_animal"] = True

    elif tool["name"] == "metabolic accelerator":
        new_item["metabolic_level"] = 1

    return new_item


def genetics_combination_function(item1, item2):
    """The overall combination function for the genetics domain."""

    # If they're both tools, return None
    if item1["tool"] and item2["tool"]:
        return None

    # If one item is a tool, apply it to the other item
    if item1["tool"]:
        new_item = genetics_apply_tool(item1, item2)
    elif item2["tool"]:
        new_item = genetics_apply_tool(item2, item1)
    else:
        # Combine two animals
        new_item = {}

        # Track families for cross-family bonus
        families1 = (
            [item1.get("family")] if "family" in item1 else item1.get("families", [])
        )
        families2 = (
            [item2.get("family")] if "family" in item2 else item2.get("families", [])
        )
        new_item["families"] = families1 + families2

        # Track habitats
        habitats1 = (
            [item1.get("habitat")] if "habitat" in item1 else item1.get("habitats", [])
        )
        habitats2 = (
            [item2.get("habitat")] if "habitat" in item2 else item2.get("habitats", [])
        )
        new_item["habitats"] = habitats1 + habitats2

        # Calculate size variance
        size_map = {"small": 0, "medium": 1, "large": 2}
        size1 = size_map.get(item1.get("size", "medium"), 1)
        size2 = size_map.get(item2.get("size", "medium"), 1)
        new_item["size_variance"] = abs(size1 - size2)

        # Determine result size (average)
        avg_size = (size1 + size2) / 2
        if avg_size < 0.5:
            new_item["size"] = "small"
        elif avg_size < 1.5:
            new_item["size"] = "medium"
        else:
            new_item["size"] = "large"

        # Preserve highest levels
        new_item["mutation_level"] = max(
            item1.get("mutation_level", 0), item2.get("mutation_level", 0)
        )
        new_item["metabolic_level"] = max(
            item1.get("metabolic_level", 0), item2.get("metabolic_level", 0)
        )

        # Handle respiratory type
        if item1.get("reconfigured_respiratory") or item2.get(
            "reconfigured_respiratory"
        ):
            new_item["reconfigured_respiratory"] = True
            # Track for amphibious bonus
            new_item["has_gills_animal"] = (
                item1.get("respiratory_type") == "gills"
                or item1.get("has_gills_animal", False)
            ) or (
                item2.get("respiratory_type") == "gills"
                or item2.get("has_gills_animal", False)
            )
            new_item["has_lungs_animal"] = (
                item1.get("respiratory_type") == "lungs"
                or item1.get("has_lungs_animal", False)
            ) or (
                item2.get("respiratory_type") == "lungs"
                or item2.get("has_lungs_animal", False)
            )

        # Determine respiratory type (prefer gills for water animals)
        if "water" in new_item["habitats"]:
            new_item["respiratory_type"] = "gills"
        else:
            new_item["respiratory_type"] = "lungs"

        # Determine diet type (carnivore dominates, then omnivore, then herbivore)
        if (
            item1.get("diet_type") == "carnivore"
            or item2.get("diet_type") == "carnivore"
        ):
            new_item["diet_type"] = "carnivore"
        elif (
            item1.get("diet_type") == "omnivore" or item2.get("diet_type") == "omnivore"
        ):
            new_item["diet_type"] = "omnivore"
        else:
            new_item["diet_type"] = "herbivore"

        # Preserve growth applied status
        new_item["growth_applied"] = item1.get("growth_applied", False) or item2.get(
            "growth_applied", False
        )
        if new_item["growth_applied"]:
            # Use the original size of whichever had growth applied
            if item1.get("growth_applied", False):
                new_item["original_size"] = item1.get("original_size", "medium")
            else:
                new_item["original_size"] = item2.get("original_size", "medium")

        # Combine basic animals
        new_item["basic_animals"] = item1.get("basic_animals", []) + item2.get(
            "basic_animals", []
        )
        new_item["basic_animal_count"] = item1.get("basic_animal_count", 0) + item2.get(
            "basic_animal_count", 0
        )

        # Determine primary habitat (water dominates, then air, then land)
        if "water" in new_item["habitats"]:
            new_item["habitat"] = "water"
        elif "air" in new_item["habitats"]:
            new_item["habitat"] = "air"
        else:
            new_item["habitat"] = "land"

        # Set a reasonable family (first one in the list)
        if new_item["families"]:
            new_item["family"] = new_item["families"][0]

    # Calculate value
    new_item["tool"] = False
    new_item["value"] = genetics_value_function(new_item)

    return new_item


# POTIONS DOMAIN FUNCTIONS

potions_feature_names = {
    "enchantment_level": ["unenchanted", "flickering", "glowing", "corrupted"],
    "extraction_level": ["unextracted", "extracted"],
    "filtered": ["unfiltered", "filtered"],
}


def potions_value_function(item):
    """Calculate the potency of a potion based on its features."""
    value = 2  # Base value for all potions

    # ALCHEMICAL MASTERY BONUSES (high rewards for understanding alchemy)

    # Plant Extraction Mastery: Vial on plant ingredients = +25
    if item.get("extraction_level", 0) == 1 and item.get("ingredient_type") == "plant":
        value += 25

    # Mineral Grinding Mastery: Mortar on hard minerals = +25
    if (
        item.get("ground", False)
        and item.get("hardness") == "hard"
        and item.get("ingredient_type") == "mineral"
    ):
        value += 25

    # Perfect Enchantment: Second-level enchantment = +30
    if item.get("enchantment_level", 0) == 2:
        value += 30

    # Liquid Purification: Filter on liquid potions = +20
    if item.get("filtered", False) and item.get("state_of_matter") == "liquid":
        value += 20

    # ULTIMATE ALCHEMY BONUSES

    # State Transformation Mastery: 3+ different states combined = +35
    if "states_of_matter" in item and len(set(item["states_of_matter"])) >= 3:
        value += 35

    # Magical-Mundane Fusion: Both magical and mundane = +30
    if item.get("has_magical", False) and item.get("has_mundane", False):
        value += 30

    # Perfect Processing: Extracted + Ground + Enchanted + Filtered = +40
    if (
        item.get("extraction_level", 0) >= 1
        and item.get("ground", False)
        and item.get("enchantment_level", 0) >= 1
        and item.get("filtered", False)
    ):
        value += 40

    # GRAND ELIXIR: All mastery bonuses combined = +50
    if (
        item.get("extraction_level", 0) >= 1
        and item.get("ground", False)
        and item.get("enchantment_level", 0) == 2
        and item.get("filtered", False)
        and item.get("has_magical", False)
        and item.get("has_mundane", False)
    ):
        value += 50

    # HARSH PENALTIES FOR POOR ALCHEMY

    # Wrong extraction target
    if item.get("extraction_level", 0) == 1 and item.get("ingredient_type") != "plant":
        value -= 25  # Vial on non-plant is wasteful

    # Wrong grinding target
    if item.get("ground", False) and item.get("hardness") == "soft":
        value -= 25  # Mortar on soft materials is wrong

    # Enchantment disasters
    if item.get("enchantment_level", 0) == 1:
        value -= 15  # First enchantment is unstable
    if item.get("enchantment_level", 0) >= 3:
        value -= 35  # Over-enchantment is catastrophic

    # Wrong filtration
    if item.get("filtered", False) and item.get("state_of_matter") in ["solid", "gas"]:
        value -= 25  # Can't filter solids/gases properly

    # State monotony penalty
    if (
        "states_of_matter" in item
        and len(set(item["states_of_matter"])) == 1
        and len(item["states_of_matter"]) > 1
    ):
        value -= 20  # Boring same-state combinations

    # Magical monotony penalty
    if (
        "magical_levels" in item
        and len(set(item["magical_levels"])) == 1
        and len(item["magical_levels"]) > 1
    ):
        value -= 15  # All same magical level is bland

    # Too many ingredients chaos
    if item.get("basic_ingredient_count", 0) > 3:
        value -= 25 * (item.get("basic_ingredient_count", 0) - 3)

    # Raw ingredient mixing penalty
    if item.get("basic_ingredient_count", 0) > 1 and not any(
        [
            item.get("extraction_level", 0) > 0,
            item.get("ground", False),
            item.get("enchantment_level", 0) > 0,
            item.get("filtered", False),
        ]
    ):
        value -= 20  # Raw mixing is amateur alchemy

    return max(value, 0)


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

    if tool["name"] == "vial":
        new_item["extraction_level"] = 1

    elif tool["name"] == "mortar":
        new_item["ground"] = True
        # Change state to powder if solid and hard
        if item.get("state_of_matter") == "solid" and item.get("hardness") == "hard":
            new_item["state_of_matter"] = "powder"

    elif tool["name"] == "wand":
        new_item["enchantment_level"] = min(item.get("enchantment_level", 0) + 1, 3)

    elif tool["name"] == "filter":
        new_item["filtered"] = True

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

        # Track states of matter for combination bonus
        states1 = [item1.get("state_of_matter")] if "state_of_matter" in item1 else []
        states2 = [item2.get("state_of_matter")] if "state_of_matter" in item2 else []
        new_item["states_of_matter"] = states1 + states2

        # Track magical levels
        new_item["has_magical"] = (
            item1.get("magical_level") == "magical"
            or item2.get("magical_level") == "magical"
            or item1.get("has_magical", False)
            or item2.get("has_magical", False)
        )
        new_item["has_mundane"] = (
            item1.get("magical_level") == "mundane"
            or item2.get("magical_level") == "mundane"
            or item1.get("has_mundane", False)
            or item2.get("has_mundane", False)
        )

        magical_levels1 = (
            [item1.get("magical_level")] if "magical_level" in item1 else []
        )
        magical_levels2 = (
            [item2.get("magical_level")] if "magical_level" in item2 else []
        )
        new_item["magical_levels"] = magical_levels1 + magical_levels2

        # Determine resulting state (liquid dominates, then gas, then powder, then solid)
        if (
            item1.get("state_of_matter") == "liquid"
            or item2.get("state_of_matter") == "liquid"
        ):
            new_item["state_of_matter"] = "liquid"
        elif (
            item1.get("state_of_matter") == "gas"
            or item2.get("state_of_matter") == "gas"
        ):
            new_item["state_of_matter"] = "gas"
        elif (
            item1.get("state_of_matter") == "powder"
            or item2.get("state_of_matter") == "powder"
        ):
            new_item["state_of_matter"] = "powder"
        else:
            new_item["state_of_matter"] = "solid"

        # Determine hardness (soft dominates for mixtures)
        if item1.get("hardness") == "soft" or item2.get("hardness") == "soft":
            new_item["hardness"] = "soft"
        else:
            new_item["hardness"] = "hard"

        # Determine ingredient type (animal dominates, then mineral, then essence, then plant)
        types = [item1.get("ingredient_type"), item2.get("ingredient_type")]
        if "animal" in types:
            new_item["ingredient_type"] = "animal"
        elif "mineral" in types:
            new_item["ingredient_type"] = "mineral"
        elif "essence" in types:
            new_item["ingredient_type"] = "essence"
        else:
            new_item["ingredient_type"] = "plant"

        # Determine magical level (magical dominates)
        if (
            item1.get("magical_level") == "magical"
            or item2.get("magical_level") == "magical"
        ):
            new_item["magical_level"] = "magical"
        else:
            new_item["magical_level"] = "mundane"

        # Preserve highest levels
        new_item["enchantment_level"] = max(
            item1.get("enchantment_level", 0), item2.get("enchantment_level", 0)
        )
        new_item["extraction_level"] = max(
            item1.get("extraction_level", 0), item2.get("extraction_level", 0)
        )
        new_item["filtered"] = item1.get("filtered", False) or item2.get(
            "filtered", False
        )
        new_item["ground"] = item1.get("ground", False) or item2.get("ground", False)

        # Combine basic ingredients
        new_item["basic_ingredients"] = item1.get("basic_ingredients", []) + item2.get(
            "basic_ingredients", []
        )
        new_item["basic_ingredient_count"] = item1.get(
            "basic_ingredient_count", 0
        ) + item2.get("basic_ingredient_count", 0)

    # Calculate value
    new_item["tool"] = False
    new_item["value"] = potions_value_function(new_item)

    return new_item


COMBO_FUNCTIONS = {
    "cooking": cooking_combination_function,
    "decorations": decorations_combination_function,
    "genetics": genetics_combination_function,
    "potions": potions_combination_function,
}

FEATURE_NAMES = {
    "cooking": cooking_feature_names,
    "decorations": decorations_feature_names,
    "genetics": genetics_feature_names,
    "potions": potions_feature_names,
}
