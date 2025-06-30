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

        # Assign values to all ingredients
        for ingredient in ingredients:
            ingredient["value"] = VALUE_FUNCTIONS[self.domain](ingredient)

        self.inventory = tools + ingredients

        return self.inventory

    def render(self):
        """
        Render the environment.
        """
        print("Inventory:")
        for item in self.inventory:
            if item["tool"]:
                print(f"{item['emoji']} {item['name']}")
            else:
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

        # if the user tries to combine two tools, do nothing
        if item1["tool"] and item2["tool"]:
            obs = {
                "inventory": self.inventory,
                "new_item": None,
            }
            return obs, 0, False, {}

        # remove non-tool items (ingredients get consumed)
        # Tools are durable and stay in inventory, ingredients are consumed
        if not item1["tool"]:
            self.inventory.remove(item1)
        if not item2["tool"]:
            self.inventory.remove(item2)

        # combine the items
        new_item = self.world_model.combine(item1, item2)

        # update the inventory
        self.inventory.append(new_item)

        obs = {
            "inventory": self.inventory,
            "new_item": new_item,
        }

        return obs, 0, False, {}

    def get_reward(self):
        """
        Get the reward at the end of an epoch.
        """
        ingredients = [item for item in self.inventory if not item["tool"]]
        reward = sum(item["value"] for item in ingredients) / len(ingredients)

        # overall reward can't go below 0
        return max(reward, 0)
