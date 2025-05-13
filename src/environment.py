import random
from typing import Optional
import gymnasium as gym
from src.world_model import MemoizedWorldModel
from src.constants import TOOLS, INGREDIENTS


class CraftingGame(gym.Env):
    """
    An open-ended LM-driven crafting game.
    """

    def __init__(self, model: str, setting: str):
        super().__init__()
        self.model = model
        self.setting = setting
        self.world_model = MemoizedWorldModel(lm=model, world_type=self.setting)
        self.inventory = []

    def reset(self, seed=None, options=None):
        """
        Get an initial state consisting of basic ingredients.
        """
        # get the item names and delete the reasoning
        tools = random.sample(TOOLS[self.setting], 4)
        ingredients = random.sample(INGREDIENTS[self.setting], 6)
        self.inventory = tools + ingredients

        return self.inventory

    def render(self):
        """
        Render the environment.
        """
        print("Inventory:")
        for item in self.inventory:
            print(f"{item['emoji']} {item['name']}, tastiness: {item['value']}")

    def reset_world_model(self):
        """
        Reset the world model.
        """
        self.world_model = MemoizedWorldModel(lm=self.model, world_type=self.setting)

    def load_world_model(self, filepath: str):
        """
        Load the world model from a file.
        """
        self.world_model = MemoizedWorldModel(lm=self.model, world_type=self.setting)
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
            best_value = max(item["value"] for item in self.inventory)
            return self.inventory, best_value, True, {}
        else:
            name1, name2 = action

        inv_names = [item["name"] for item in self.inventory]

        # check if the items are in the inventory
        if name1 not in inv_names or name2 not in inv_names:
            raise ValueError(f"Item {name1} or {name2} not in inventory")

        # get the items
        item1 = next(item for item in self.inventory if item["name"] == name1)
        item2 = next(item for item in self.inventory if item["name"] == name2)

        # remove non-durable items
        if not item1["durable"]:
            self.inventory.remove(item1)
        if not item2["durable"]:
            self.inventory.remove(item2)

        # combine the items
        new_item = self.world_model.combine(item1, item2)

        # if the new item is already in the inventory, don't add it
        if new_item["name"] in inv_names:
            return self.inventory, 0, False, {}

        # update the inventory
        self.inventory.append(new_item)

        obs = {
            "inventory": self.inventory,
            "new_item": new_item,
        }

        return obs, 0, False, {}
