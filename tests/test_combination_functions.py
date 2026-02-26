import random

from oecraft.types import CombinedItem, Ingredient, Tool
from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.utils import load_function_from_string


def test_combination_functions():
    for domain_name, descriptor in GAME_DESCRIPTORS.items():
        print(f"Testing domain: {domain_name}")

        # reconstruct objects from dicts
        ingredients = [
            Ingredient(**d) if isinstance(d, dict) else d
            for d in descriptor.ingredients
        ]
        tools = [Tool(**d) if isinstance(d, dict) else d for d in descriptor.tools]
        inventory = ingredients + tools

        combination_fn = load_function_from_string(
            descriptor.combination_fn, "combination_fn"
        )

        for _ in range(50):
            item1 = random.choice(inventory)
            item2 = random.choice(inventory)

            result = combination_fn(item1, item2)

            # check that the result is valid (None or has features)
            assert result is None or hasattr(result, "features")


def test_potions_framed_as_cooking_loads():
    """Verify the descriptor exists and all functions load."""
    assert "potions_framed_as_cooking" in GAME_DESCRIPTORS
    desc = GAME_DESCRIPTORS["potions_framed_as_cooking"]

    assert len(desc.ingredients) == 20
    assert len(desc.tools) == 2

    # All four functions should load without error
    load_function_from_string(desc.combination_fn, "combination_fn")
    load_function_from_string(desc.value_fn, "value_fn")
    load_function_from_string(desc.get_inventory_fn, "get_inventory_fn")
    load_function_from_string(desc.descriptor_fn, "descriptor_fn")


def test_potions_framed_as_cooking_ingredient_distribution():
    """Verify ingredient distribution matches potions exactly."""
    desc = GAME_DESCRIPTORS["potions_framed_as_cooking"]
    ingredients = [
        Ingredient(**d) if isinstance(d, dict) else d for d in desc.ingredients
    ]

    # Count by form (= state_of_matter in potions)
    whole = [i for i in ingredients if i.features["form"] == "whole"]
    ground = [i for i in ingredients if i.features["form"] == "ground"]
    liquid = [i for i in ingredients if i.features["form"] == "liquid"]
    assert len(whole) == 11
    assert len(ground) == 4
    assert len(liquid) == 5

    # Count seasoned/plain within each form (= magical/mundane in potions)
    assert sum(1 for i in whole if i.features["seasoned"] == 0) == 7
    assert sum(1 for i in whole if i.features["seasoned"] == 1) == 4
    assert sum(1 for i in ground if i.features["seasoned"] == 0) == 1
    assert sum(1 for i in ground if i.features["seasoned"] == 1) == 3
    assert sum(1 for i in liquid if i.features["seasoned"] == 0) == 3
    assert sum(1 for i in liquid if i.features["seasoned"] == 1) == 2


def _load_fns(descriptor):
    """Helper to load all functions from a descriptor."""
    return (
        load_function_from_string(descriptor.combination_fn, "combination_fn"),
        load_function_from_string(descriptor.value_fn, "value_fn"),
        load_function_from_string(descriptor.get_inventory_fn, "get_inventory_fn"),
        load_function_from_string(descriptor.descriptor_fn, "descriptor_fn"),
    )


def test_potions_framed_as_cooking_isomorphism():
    """Core test: cooking-framed values must match potions for corresponding features."""
    p_comb, p_val, _, _ = _load_fns(GAME_DESCRIPTORS["potions"])
    c_comb, c_val, _, _ = _load_fns(GAME_DESCRIPTORS["potions_framed_as_cooking"])

    def p_item(**kw):
        defaults = {
            "state_of_matter": "solid",
            "magical": 0,
            "filtering": None,
            "extraction": None,
        }
        defaults.update(kw)
        return Ingredient(features=defaults)

    def c_item(**kw):
        defaults = {
            "form": "whole",
            "seasoned": 0,
            "straining": None,
            "juicing": None,
        }
        defaults.update(kw)
        return Ingredient(features=defaults)

    vial = Tool(name="vial", emoji="x")
    filt = Tool(name="filter", emoji="x")
    juicer = Tool(name="juicer", emoji="x")
    strainer = Tool(name="strainer", emoji="x")

    # 1. Correct tool on correct item: vial+solid = juicer+whole → 30
    assert p_val(p_comb(vial, p_item())) == c_val(c_comb(juicer, c_item())) == 30

    # 2. Wrong tool → botched: filter+solid = strainer+whole → -20
    assert p_val(p_comb(filt, p_item())) == c_val(c_comb(strainer, c_item())) == -20

    # 3. Filter on liquid = strainer on liquid → filtered/strained → 30
    p_liq = p_item(state_of_matter="liquid")
    c_liq = c_item(form="liquid")
    assert p_val(p_comb(filt, p_liq)) == c_val(c_comb(strainer, c_liq)) == 30

    # 4. Vial on liquid → botched extraction/juicing → -20
    assert p_val(p_comb(vial, p_liq)) == c_val(c_comb(juicer, c_liq)) == -20

    # 5. Filter on gas = strainer on ground → filtered/strained → 30
    p_gas = p_item(state_of_matter="gas", magical=1)
    c_gnd = c_item(form="ground", seasoned=1)
    assert p_val(p_comb(filt, p_gas)) == c_val(c_comb(strainer, c_gnd)) == 30

    # 6. Two liquids mixed magical/mundane = mixed seasoned/plain → +40
    p_liq_mag = p_item(state_of_matter="liquid", magical=1)
    p_liq_mun = p_item(state_of_matter="liquid", magical=0)
    c_liq_sea = c_item(form="liquid", seasoned=1)
    c_liq_pln = c_item(form="liquid", seasoned=0)
    assert p_val(p_comb(p_liq_mag, p_liq_mun)) == c_val(
        c_comb(c_liq_sea, c_liq_pln)
    ) == 40

    # 7. Two liquids same magical/seasoned → no bonus, just 0
    assert p_val(p_comb(p_liq_mun, p_liq_mun)) == c_val(
        c_comb(c_liq_pln, c_liq_pln)
    ) == 0

    # 8. Best combo: extracted+filtered magical liquid + mundane liquid → 100
    p_best = p_item(
        state_of_matter="liquid",
        magical=1,
        extraction="extracted",
        filtering="filtered",
    )
    c_best = c_item(
        form="liquid", seasoned=1, juicing="juiced", straining="strained"
    )
    assert p_val(p_comb(p_best, p_liq_mun)) == c_val(
        c_comb(c_best, c_liq_pln)
    ) == 100

    # 9. 3-ingredient penalty: three liquids (mixed) → -100 + 40 = -60
    p_trio = p_comb(p_comb(p_liq_mag, p_liq_mun), p_liq_mun)
    c_trio = c_comb(c_comb(c_liq_sea, c_liq_pln), c_liq_pln)
    assert p_val(p_trio) == c_val(c_trio) == -60

    # 10. Non-liquid in combo (mixed): solid+liquid → -100 + 40 = -60
    p_mixed = p_comb(p_item(magical=1), p_liq_mun)
    c_mixed = c_comb(c_item(seasoned=1), c_liq_pln)
    assert p_val(p_mixed) == c_val(c_mixed) == -60

    # 11. Double-botched item → -40
    p_double = p_item(extraction="botched", filtering="botched")
    c_double = c_item(juicing="botched", straining="botched")
    assert p_val(p_double) == c_val(c_double) == -40


def test_potions_framed_as_cooking_combination_fn_smoke():
    """Random combinations should not crash."""
    desc = GAME_DESCRIPTORS["potions_framed_as_cooking"]
    comb_fn = load_function_from_string(desc.combination_fn, "combination_fn")
    val_fn = load_function_from_string(desc.value_fn, "value_fn")

    ingredients = [
        Ingredient(**d) if isinstance(d, dict) else d for d in desc.ingredients
    ]
    tools = [Tool(**d) if isinstance(d, dict) else d for d in desc.tools]
    inventory = ingredients + tools

    for _ in range(100):
        item1 = random.choice(inventory)
        item2 = random.choice(inventory)
        result = comb_fn(item1, item2)

        if result is not None:
            # value_fn should not crash on the result
            val_fn(result)


def test_potions_framed_as_cooking_inventory():
    """Inventory selection should always include seasoned and plain items."""
    desc = GAME_DESCRIPTORS["potions_framed_as_cooking"]
    get_inv = load_function_from_string(desc.get_inventory_fn, "get_inventory_fn")
    ingredients = [
        Ingredient(**d) if isinstance(d, dict) else d for d in desc.ingredients
    ]

    for _ in range(50):
        inv = get_inv(4, ingredients)
        assert len(inv) == 4
        seasonings = {i.features["seasoned"] for i in inv}
        assert 0 in seasonings, "Inventory missing plain ingredient"
        assert 1 in seasonings, "Inventory missing seasoned ingredient"


def test_potions_framed_as_cooking_descriptor_fn():
    """Descriptor function should produce correct human-readable strings."""
    desc = GAME_DESCRIPTORS["potions_framed_as_cooking"]
    desc_fn = load_function_from_string(desc.descriptor_fn, "descriptor_fn")
    feature_names = desc.feature_names

    # Basic whole plain item
    item = Ingredient(
        features={"form": "whole", "seasoned": 0, "straining": None, "juicing": None}
    )
    result = desc_fn(item, feature_names)
    assert "whole" in result
    assert "plain" in result

    # Juiced seasoned item
    item = Ingredient(
        features={
            "form": "liquid",
            "seasoned": 1,
            "straining": None,
            "juicing": "juiced",
        }
    )
    result = desc_fn(item, feature_names)
    assert "liquid" in result
    assert "juiced" in result
    assert "seasoned" in result

    # Botched straining
    item = Ingredient(
        features={
            "form": "whole",
            "seasoned": 0,
            "straining": "botched",
            "juicing": None,
        }
    )
    result = desc_fn(item, feature_names)
    assert "botched straining" in result
    assert "plain" in result

    # Strained item
    item = Ingredient(
        features={
            "form": "liquid",
            "seasoned": 1,
            "straining": "strained",
            "juicing": None,
        }
    )
    result = desc_fn(item, feature_names)
    assert "strained" in result
    assert "seasoned" in result

    # Combined item descriptor
    comb_fn = load_function_from_string(desc.combination_fn, "combination_fn")
    item1 = Ingredient(
        name="apple",
        emoji="🍎",
        features={
            "form": "liquid",
            "seasoned": 0,
            "straining": None,
            "juicing": "juiced",
        },
    )
    item2 = Ingredient(
        name="ginger",
        emoji="🫚",
        features={
            "form": "whole",
            "seasoned": 1,
            "straining": None,
            "juicing": None,
        },
    )
    combined = comb_fn(item1, item2)
    result = desc_fn(combined, feature_names)
    assert "apple" in result
    assert "ginger" in result
