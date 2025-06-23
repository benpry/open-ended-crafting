import math


def cooking_value_function(item):
    # Base value: only edible things have value
    if not item["edible"]:
        return 0

    value = 0

    # Positive utility:
    if item["cook_level"] == 1:  # Cooked things are good
        value += 15

    if item["water_level"] == 1 and item["cook_level"] == 1:  # Soup is good
        value += 40

    if (
        item["water_level"] == 1 and item["chop_level"] >= 1
    ):  # Chopped and soaked things are good
        value += 20

    if (
        item["cook_level"] == 1 and item["chop_level"] == 1
    ):  # Cooked and chopped things are good
        value += 10

    if item["chop_level"] == 1:  # Chopped things are good
        value += 5

    if item["salt_level"] == 1:  # Salted things are good
        value += 20

    # cooked meats are extra good
    if "meat" in item["ingredient_types"] and item["cook_level"] == 1:
        value += 30

    # chopped and eviscerated aromatic things are extra good
    if "aromatic" in item["ingredient_types"] and item["chop_level"] >= 2:
        value += 15

    # combining up to 3 different ingredient types is good
    distinct_ingredient_types = min(len(set(item["ingredient_types"])), 3)
    if distinct_ingredient_types == 2:
        value += 10
    elif distinct_ingredient_types == 3:
        value += 20

    # Negative utility:
    if item["cook_level"] == 2:  # Overcooked things are bad
        value -= 40

    if item["salt_level"] == 2:  # Over-salted things are bad
        value -= 40

    if (
        item["water_level"] == 1 and item["cook_level"] == 0
    ):  # Uncooked soaked things are bad
        value -= 20

    # salting fruit is bad
    if set(item["ingredient_types"]) == {"fruit"}:
        value -= 15

    # more than one ingredient of the same type is bad
    for ingredient_type in item["ingredient_types"]:
        if item["ingredient_types"].count(ingredient_type) > 1:
            value -= 30

    return value


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
        value += 20

    # Cutting soft materials is good
    if item["hardness"] == "soft" and item["cut_level"] == 1:
        value += 20

    # Painting is good
    if item["paint_level"] == 1:
        value += 15

    # framing helps, provided we didn't mess with something after framing
    if item["framed"] and not item["post_frame_messed_with"]:
        value += 15

    # combining natural and artificial materials is good
    if "natural" in item["material_types"] and "artificial" in item["material_types"]:
        value += 35

    # NEGATIVE UTILITY

    # messing with things after framing is bad
    if item["post_frame_messed_with"]:
        value -= 50

    # over-painting is bad
    if item["paint_level"] == 2:
        value -= 20

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


# GENETICS DOMAIN FUNCTIONS

genetics_feature_names = {
    "mutation_level": ["normal", "mutant", "super-mutant", "corrupted"],
    "metabolic_level": ["normal", "enhanced"],
}


def genetics_value_function(item):
    """Calculate the value of a genetic creation based on its features."""
    value = 0  # No base value for animals

    # EVOLUTION MASTERY BONUSES (high rewards for understanding genetics)

    # Optimal Growth: Growth serum on small animals = +65
    if item.get("growth_applied", False) and item.get("original_size") == "small":
        value += 65

    # Perfect Mutation: Second-level mutation = +60
    if item.get("mutation_level", 0) == 2:
        value += 60

    # Metabolic Enhancement: Accelerator on carnivores/omnivores = +55
    if item.get("metabolic_level", 0) == 1 and item.get("diet_type") in [
        "carnivore",
        "omnivore",
    ]:
        value += 55

    # ULTIMATE EVOLUTION BONUSES

    # Amphibious Mastery: Gills + Lungs + Mutation + Reconfiguration = +90
    if (
        item.get("has_gills_animal", False)
        and item.get("has_lungs_animal", False)
        and item.get("reconfigured_respiratory", False)
        and item.get("mutation_level", 0) >= 1
    ):
        value += 90

    # Perfect Hybrid: Exactly 2 families from same habitat = +80
    if (
        item.get("families")
        and len(set(item["families"])) == 2
        and "habitats" in item
        and len(set(item["habitats"])) == 1
    ):
        value += 80

    # Size Perfection: Same-size breeding = +45
    if item.get("size_variance", 1) == 0:  # No size difference
        value += 45

    # MEGA EVOLUTION: Growth + Mutation + Metabolic + Perfect Hybrid = +120
    if (
        item.get("growth_applied", False)
        and item.get("mutation_level", 0) >= 2
        and item.get("metabolic_level", 0) >= 1
        and item.get("families")
        and len(set(item["families"])) == 2
    ):
        value += 120

    # Remove simple breeding bonus to reduce random scores

    # HARSH PENALTIES FOR POOR BREEDING

    # Penalty 0: Single unmodified animals = -120
    if (
        item.get("basic_animal_count", 0) == 1
        and not item.get("growth_applied", False)
        and item.get("mutation_level", 0) == 0
        and item.get("metabolic_level", 0) == 0
        and not item.get("reconfigured_respiratory", False)
    ):
        value -= 120

    # Any unmodified animal combination
    if item.get("basic_animal_count", 0) > 1 and not any(
        [
            item.get("growth_applied", False),
            item.get("mutation_level", 0) > 0,
            item.get("metabolic_level", 0) > 0,
            item.get("reconfigured_respiratory", False),
        ]
    ):
        value -= 120

    # Wrong growth application
    if item.get("growth_applied", False) and item.get("original_size") == "large":
        value -= 65  # Growth on large animals is terrible

    # Mutation disasters
    if item.get("mutation_level", 0) == 1:
        value -= 55  # First mutation is unstable
    if item.get("mutation_level", 0) >= 3:
        value -= 85  # Over-mutation is catastrophic

    # Metabolic mismatch
    if item.get("metabolic_level", 0) == 1 and item.get("diet_type") == "herbivore":
        value -= 60  # Metabolic boost on herbivores is bad

    # Size incompatibility disaster
    if item.get("size_variance", 0) >= 2:  # Large vs small
        value -= 75  # Terrible genetic mismatch

    # Habitat chaos
    if "habitats" in item and len(set(item["habitats"])) > 2:
        value -= 60 * (len(set(item["habitats"])) - 2)

    # Family chaos
    if item.get("families") and len(set(item["families"])) > 3:
        value -= 55 * (len(set(item["families"])) - 3)

    # Too many animals penalty
    if item.get("basic_animal_count", 0) > 2:
        value -= 150 * (item.get("basic_animal_count", 0) - 2)

    # Penalty 8: Any animal without proper enhancement = -200
    if (
        item.get("basic_animal_count", 0) >= 1
        and not item.get("growth_applied", False)
        and item.get("mutation_level", 0) == 0
    ):
        value -= 200

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
    value = 0  # No base value for potions

    # ALCHEMICAL MASTERY BONUSES (high rewards for understanding alchemy)

    # Plant Extraction Mastery: Vial on plant ingredients = +60
    if item.get("extraction_level", 0) == 1 and item.get("ingredient_type") == "plant":
        value += 60

    # Mineral Grinding Mastery: Mortar on hard minerals = +60
    if (
        item.get("ground", False)
        and item.get("hardness") == "hard"
        and item.get("ingredient_type") == "mineral"
    ):
        value += 60

    # Perfect Enchantment: Second-level enchantment = +65
    if item.get("enchantment_level", 0) == 2:
        value += 65

    # Liquid Purification: Filter on liquid potions = +55
    if item.get("filtered", False) and item.get("state_of_matter") == "liquid":
        value += 55

    # ULTIMATE ALCHEMY BONUSES

    # State Transformation Mastery: 3+ different states combined = +85
    if "states_of_matter" in item and len(set(item["states_of_matter"])) >= 3:
        value += 85

    # Magical-Mundane Fusion: Both magical and mundane = +80
    if item.get("has_magical", False) and item.get("has_mundane", False):
        value += 80

    # Perfect Processing: Extracted + Ground + Enchanted + Filtered = +100
    if (
        item.get("extraction_level", 0) >= 1
        and item.get("ground", False)
        and item.get("enchantment_level", 0) >= 1
        and item.get("filtered", False)
    ):
        value += 100

    # GRAND ELIXIR: All mastery bonuses combined = +120
    if (
        item.get("extraction_level", 0) >= 1
        and item.get("ground", False)
        and item.get("enchantment_level", 0) == 2
        and item.get("filtered", False)
        and item.get("has_magical", False)
        and item.get("has_mundane", False)
        and len(set(item.get("states_of_matter", []))) >= 3
    ):
        value += 120

    # Remove simple processing bonus to reduce random scores

    # HARSH PENALTIES FOR POOR ALCHEMY

    # Penalty 0: Single unprocessed ingredients = -120
    if (
        item.get("basic_ingredient_count", 0) == 1
        and item.get("extraction_level", 0) == 0
        and not item.get("ground", False)
        and item.get("enchantment_level", 0) == 0
        and not item.get("filtered", False)
    ):
        value -= 120

    # Any unprocessed ingredient combination
    if item.get("basic_ingredient_count", 0) > 1 and not any(
        [
            item.get("extraction_level", 0) > 0,
            item.get("ground", False),
            item.get("enchantment_level", 0) > 0,
            item.get("filtered", False),
        ]
    ):
        value -= 120

    # Wrong extraction target
    if item.get("extraction_level", 0) == 1 and item.get("ingredient_type") != "plant":
        value -= 60  # Vial on non-plant is wasteful

    # Wrong grinding target
    if item.get("ground", False) and item.get("hardness") == "soft":
        value -= 60  # Mortar on soft materials is wrong

    # Enchantment disasters
    if item.get("enchantment_level", 0) == 1:
        value -= 45  # First enchantment is unstable
    if item.get("enchantment_level", 0) >= 3:
        value -= 80  # Over-enchantment is catastrophic

    # Wrong filtration
    if item.get("filtered", False) and item.get("state_of_matter") in ["solid", "gas"]:
        value -= 60  # Can't filter solids/gases properly

    # State monotony penalty
    if (
        "states_of_matter" in item
        and len(set(item["states_of_matter"])) == 1
        and len(item["states_of_matter"]) > 1
    ):
        value -= 55  # Boring same-state combinations

    # Magical monotony penalty
    if (
        "magical_levels" in item
        and len(set(item["magical_levels"])) == 1
        and len(item["magical_levels"]) > 1
    ):
        value -= 45  # All same magical level is bland

    # Too many ingredients chaos
    if item.get("basic_ingredient_count", 0) > 3:
        value -= 150 * (item.get("basic_ingredient_count", 0) - 3)

    # Penalty 7: Multiple ingredients with no processing = -180
    if (
        item.get("basic_ingredient_count", 0) > 1
        and item.get("extraction_level", 0) == 0
        and not item.get("ground", False)
        and item.get("enchantment_level", 0) == 0
    ):
        value -= 180

    # Penalty 8: Any ingredient without proper processing = -150
    if (
        item.get("basic_ingredient_count", 0) >= 1
        and item.get("extraction_level", 0) == 0
        and not item.get("ground", False)
    ):
        value -= 150

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

VALUE_FUNCTIONS = {
    "cooking": cooking_value_function,
    "decorations": decorations_value_function,
    "genetics": genetics_value_function,
    "potions": potions_value_function,
}
