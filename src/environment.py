import random
from typing import Optional
import gymnasium as gym
from src.world_model import MemoizedWorldModel

all_ingredients = [
    {"name": "apple", "emoji": "🍎", "value": 2, "durable": False},
    {"name": "banana", "emoji": "🍌", "value": 2, "durable": False},
    {"name": "carrot", "emoji": "🥕", "value": 2, "durable": False},
    {"name": "egg", "emoji": "🥚", "value": 0, "durable": False},
    {"name": "raw fish", "emoji": "🐟", "value": 2, "durable": False},
    {"name": "raw meat", "emoji": "🥩", "value": 0, "durable": False},
    {"name": "raw rice", "emoji": "🌾", "value": 0, "durable": False},
    {"name": "wheat", "emoji": "🌾", "value": 0, "durable": False},
    {"name": "milk", "emoji": "🥛", "value": 2, "durable": False},
    {"name": "cheese", "emoji": "🧀", "value": 2, "durable": False},
    {"name": "lettuce", "emoji": "🥬", "value": 2, "durable": False},
    {"name": "tomato", "emoji": "🍅", "value": 2, "durable": False},
    {"name": "onion", "emoji": "🧅", "value": 1, "durable": False},
    {"name": "garlic", "emoji": "🧄", "value": 0, "durable": False},
    {"name": "ginger", "emoji": "🫚", "value": 0, "durable": False},
    {"name": "mushroom", "emoji": "🍄", "value": 2, "durable": False},
    {"name": "pepper", "emoji": "🌶️", "value": 2, "durable": False},
    {"name": "potato", "emoji": "🥔", "value": 2, "durable": False},
    {"name": "coconut", "emoji": "🥥", "value": 2, "durable": False},
    {"name": "pineapple", "emoji": "🍍", "value": 2, "durable": False},
]


tools = [
    {"name": "water", "emoji": "💧", "value": 0, "durable": True},
    {"name": "knife", "emoji": "🔪", "value": 0, "durable": True},
    {"name": "stove", "emoji": "🔥", "value": 0, "durable": True},
    {"name": "salt", "emoji": "🧂", "value": 0, "durable": True},
]


class CookingGame(gym.Env):
    """
    An open-ended LM-driven cooking game.
    """

    def __init__(self, model: str):
        super().__init__()
        self.model = model
        self.world_model = MemoizedWorldModel(lm=model)
        self.inventory = []

    def reset(self, seed=None, options=None):
        """
        Get an initial state consisting of basic ingredients.
        """
        # get the item names and delete the reasoning
        ingredients = random.sample(all_ingredients, 5)
        self.inventory = tools + ingredients

        return self.inventory

    def reset_world_model(self):
        """
        Reset the world model.
        """
        self.world_model = MemoizedWorldModel(lm=self.model)

    def load_world_model(self, filepath: str):
        """
        Load the world model from a file.
        """
        self.world_model = MemoizedWorldModel(lm=self.model)
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

        # remove consumable items
        if item1["consumable"]:
            self.inventory.remove(item1)
        if item2["consumable"]:
            self.inventory.remove(item2)

        # combine the items
        new_item = self.world_model.combine(item1, item2)

        # if the new item is already in the inventory, don't add it
        if new_item["name"] in inv_names:
            return self.inventory, 0, False, {}

        # update the inventory
        self.inventory.append(new_item)

        return self.inventory, 0, False, {}

    def render(self):
        """
        Render the environment.
        """
        print("Inventory:")
        for item in self.inventory:
            print(f"{item['emoji']} {item['name']}, tastiness: {item['value']}")
