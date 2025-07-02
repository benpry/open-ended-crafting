import math
from typing import Optional

import gymnasium as gym

suit_order = ["clubs", "diamonds", "spades", "hearts"]
suit_emojis = ["♣", "♢", "♠", "♡"]
number_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, "jack", "queen", "king", "ace"]
number_emojis = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def value_fn(item):
    if item["number"] < 12:
        number_value = math.floor(item["number"] / 3)
    elif item["number"] == 12:
        number_value = 10
    else:
        number_value = 0

    suit_value = 10 if item["suit"] == 1 or item["suit"] == 3 else 1

    return number_value + suit_value


def tool_fn(tool, item):
    new_item = item.copy()

    if tool["name"] == "suit swapper":
        new_item["suit"] = (item["suit"] + 1) % len(suit_order)

    elif tool["name"] == "number increaser":
        new_item["number"] = min(item["number"] + 1, len(number_order) - 1)

    return new_item


def combo_fn(item1, item2):
    if item1["tool"] and item2["tool"]:
        return None

    if item1["tool"]:
        new_item = tool_fn(item1, item2)
    elif item2["tool"]:
        new_item = tool_fn(item2, item1)
    else:
        new_item = {}

        new_item["number"] = max(item1["number"], item2["number"])
        new_item["suit"] = max(item1["suit"], item2["suit"])

    new_item["name"] = (
        f"{number_order[new_item['number']]} of {suit_order[new_item['suit']]}"
    )
    new_item["emoji"] = (
        f"{number_emojis[new_item['number']]}{suit_emojis[new_item['suit']]}"
    )
    new_item["tool"] = False
    new_item["value"] = value_fn(new_item)

    return new_item


tools = [
    {
        "name": "suit swapper",
        "emoji": "🃏",
        "tool": True,
    },
    {
        "name": "number increaser",
        "emoji": "➕",
        "tool": True,
    },
]

ingredients = [
    {
        "name": "7 of clubs",
        "emoji": "7♣",
        "tool": False,
        "number": 7,
        "suit": 0,
    },
    {
        "name": "jack of hearts",
        "emoji": "J♡",
        "tool": False,
        "number": 11,
        "suit": 2,
    },
]

for ingredient in ingredients:
    ingredient["value"] = value_fn(ingredient)


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

        item1 = next(item for item in self.inventory if item["name"] == name1)
        item2 = next(item for item in self.inventory if item["name"] == name2)

        new_item = combo_fn(item1, item2)

        if new_item is None:
            obs = {
                "inventory": self.inventory,
                "new_item": new_item,
            }
            return obs, 0, False, {}

        if not item1["tool"]:
            self.inventory.remove(item1)
        if not item2["tool"]:
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
