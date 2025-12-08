from dataclasses import replace
from typing import Optional

import gymnasium as gym
from unicards import unicard

from src.constants import CombinedItem, Ingredient, Item, NonTool, Tool

suit_order = ["clubs", "diamonds", "spades", "hearts"]
number_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, "jack", "queen", "king", "ace"]


def get_item_descriptor(item: NonTool) -> str:
    if isinstance(item, CombinedItem):
        ingredient_descriptors = [
            f"{x.emoji} {x.name}: {get_item_descriptor(x)}" for x in item.ingredients
        ]
        return "\n".join(ingredient_descriptors)

    descriptors = []

    descriptors.append(str(number_order[item.features["number"]]))
    descriptors.append(suit_order[item.features["suit"]])

    return ", ".join(descriptors)


def get_card_emoji(number, suit):
    suit = suit_order[suit]
    suit = suit[0]
    number = number_order[number]
    number = "T" if number == 10 else str(number)[0].upper()
    card_string = f"{number}{suit}"
    card_emoji = unicard(card_string)

    return card_emoji


def value_fn(item: NonTool) -> int:
    if isinstance(item, CombinedItem):
        ingredient_values = [value_fn(x) for x in item.ingredients]
        n_ingredients = len(item.ingredients)
        n_distinct_suits = len(set([x.features["suit"] for x in item.ingredients]))

        if n_ingredients > 1 and n_distinct_suits == 1:
            bonus = 20
        else:
            bonus = -45

        return sum(ingredient_values) + bonus

    if item.features["number"] <= 10:
        number_value = item.features["number"] * 4
    else:
        number_value = -20

    return number_value


def apply_tool(tool: Tool, item: NonTool) -> NonTool:
    if isinstance(item, CombinedItem):
        return CombinedItem(
            ingredients=[apply_tool(tool, x) for x in item.ingredients],
        )

    new_features = item.features.copy()

    if tool.name == "number increaser":
        new_features["number"] = min(item.features["number"] + 1, len(number_order) - 1)

    new_name = (
        f"{number_order[new_features['number']]} of {suit_order[new_features['suit']]}"
    )
    new_emoji = get_card_emoji(new_features["number"], new_features["suit"])
    return Ingredient(features=new_features, name=new_name, emoji=new_emoji)


def get_item_name(item: Item) -> str:
    if isinstance(item, CombinedItem):
        ingredient_names = [get_item_name(x) for x in item.ingredients]
        return f"{', '.join(ingredient_names)}"
    else:
        return f"{number_order[item.features['number']]} of {suit_order[item.features['suit']]}"


def get_item_emoji(item: Item) -> str:
    if isinstance(item, CombinedItem):
        ingredient_emojis = [get_item_emoji(x) for x in item.ingredients]
        return "".join(ingredient_emojis)
    else:
        return get_card_emoji(item.features["number"], item.features["suit"])


def combo_fn(item1: Item, item2: Item) -> NonTool:
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

    new_item = replace(
        new_item,
        name=get_item_name(new_item),
        emoji=get_item_emoji(new_item),
        value=value_fn(new_item),
    )

    return new_item


tools = [
    Tool(name="number increaser", emoji="➕"),
]

ingredients = [
    Ingredient(
        name="2 of clubs",
        emoji=unicard("2c"),
        features={"number": 2, "suit": 0},
        value=value_fn(Ingredient(features={"number": 2, "suit": 0})),
    ),
    Ingredient(
        name="5 of hearts",
        emoji=unicard("5h"),
        features={"number": 5, "suit": 3},
        value=value_fn(Ingredient(features={"number": 5, "suit": 3})),
    ),
    Ingredient(
        name="4 of clubs",
        emoji=unicard("4c"),
        features={"number": 4, "suit": 0},
        value=value_fn(Ingredient(features={"number": 4, "suit": 0})),
    ),
]


class PracticeCraftingGame(gym.Env):
    """
    A simple practice crafting.
    """

    def __init__(self):
        super().__init__()
        self.inventory = []

    def reset(self, seed=None, options=None):
        self.inventory = tools + ingredients
        return self.inventory

    def render(self):
        print("Inventory:")
        for item in self.inventory:
            if item["tool"]:
                print(f"{item['emoji']} {item['name']}")
            else:
                print(f"{item['emoji']} {item['name']}, value: {item['value']}")

    def step(self, action: Optional[tuple[str, str]]):
        if action is None:
            reward = self.get_reward()
            obs = {
                "inventory": self.inventory,
                "new_item": None,
            }
            return obs, reward, True, {}
        else:
            name1, name2 = action

        item1 = next(item for item in self.inventory if item.name == name1)
        item2 = next(item for item in self.inventory if item.name == name2)

        new_item = combo_fn(item1, item2)

        if new_item is None:
            obs = {
                "inventory": self.inventory,
                "new_item": new_item,
            }
            return obs, 0, False, {}

        if not isinstance(item1, Tool):
            self.inventory.remove(item1)
        if not isinstance(item2, Tool):
            self.inventory.remove(item2)

        self.inventory.append(new_item)

        obs = {
            "inventory": self.inventory,
            "new_item": new_item,
        }

        return obs, 0, False, {}

    def get_reward(self):
        """
        Get the reward
        """
        ingredients = [item for item in self.inventory if not item["tool"]]
        reward = sum(item["value"] for item in ingredients) / len(ingredients)

        # overall reward can't go below 0
        return max(reward, 0)
