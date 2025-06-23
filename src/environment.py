import random
from typing import Optional

import gymnasium as gym

from src.combo_functions import VALUE_FUNCTIONS
from src.constants import INGREDIENTS, TOOLS
from src.world_model import MemoizedWorldModel


class CraftingGame(gym.Env):
    """
    An open-ended LM-driven crafting game.
    """

    def __init__(self, model: str, domain: str, assign_names: bool = False):
        super().__init__()
        self.model = model
        self.domain = domain
        self.world_model = MemoizedWorldModel(
            lm=model, domain=self.domain, assign_names=assign_names
        )
        self.inventory = []

    def reset(self, seed=None, options=None):
        """
        Get an initial state consisting of basic ingredients.
        """
        # get the item names and delete the reasoning
        tools = TOOLS[self.domain]
        ingredients = random.sample(INGREDIENTS[self.domain], 3)
        for ingredient in ingredients:
            ingredient["value"] = VALUE_FUNCTIONS[self.domain](ingredient)
        # tools = cooking_tools
        # ingredients = random.sample(cooking_ingredients, 5)
        self.inventory = tools + ingredients

        return self.inventory

    def render(self):
        """
        Render the environment.
        """
        print("Inventory:")
        for item in self.inventory:
            print(f"{item['emoji']} {item['name']}, value: {item['value']}")

    def reset_world_model(self):
        """
        Reset the world model.
        """
        self.world_model = MemoizedWorldModel(lm=self.model, domain=self.domain)

    def load_world_model(self, filepath: str):
        """
        Load the world model from a file.
        """
        self.world_model = MemoizedWorldModel(lm=self.model, domain=self.domain)
        self.world_model.load(filepath)

    def save_world_model(self, filepath: str):
        """
        Save the world model to a file.
        """
        self.world_model.save(filepath)

    def step(self, action: Optional[tuple[str, str]]):
        """
        Take an action in the environment.
        """
        if action is None:
            reward = self.get_reward()
            obs = {
                "inventory": self.inventory,
                "new_item": None,
            }
            return obs, reward, True, {}
        else:
            name1, name2 = action

        inv_names = [item["name"] for item in self.inventory]

        # check if the items are in the inventory
        if name1 not in inv_names or name2 not in inv_names:
            raise ValueError(f"Item {name1} or {name2} not in inventory")

        # get the items
        item1 = next(item for item in self.inventory if item["name"] == name1)
        item2 = next(item for item in self.inventory if item["name"] == name2)

        # remove non-tool items (ingredients get consumed)
        # Tools are durable and stay in inventory, ingredients are consumed
        if not item1.get("tool", False):
            self.inventory.remove(item1)
        if not item2.get("tool", False):
            self.inventory.remove(item2)

        # combine the items
        new_item = self.world_model.combine(item1, item2)

        obs = {
            "inventory": self.inventory,
            "new_item": new_item,
        }

        # if the new item is already in the inventory, don't add it
        if new_item is None or new_item["name"] in inv_names:
            return obs, 0, False, {}

        # update the inventory
        self.inventory.append(new_item)

        return obs, 0, False, {}

    def get_reward(self):
        """
        Get the reward at the end of an epoch.
        """
        reward = sum(
            item["value"] if item["tool"] not in item else 0 for item in self.inventory
        ) / (len(self.inventory) - len(TOOLS[self.domain]))

        # overall reward can't go below 0
        return max(reward, 0)
