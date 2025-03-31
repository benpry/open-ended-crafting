import random
import gymnasium as gym
from src.world_model import MemoizedWorldModel

all_ingredients = [
    {"name": "apple", "emoji": "🍎", "value": 2, "consumable": True},
    {"name": "banana", "emoji": "🍌", "value": 2, "consumable": True},
    {"name": "carrot", "emoji": "🥕", "value": 2, "consumable": True},
    {"name": "egg", "emoji": "🥚", "value": 0, "consumable": True},
    {"name": "raw fish", "emoji": "🐟", "value": 6, "consumable": True},
    {"name": "raw meat", "emoji": "🥩", "value": 0, "consumable": True},
    {"name": "raw rice", "emoji": "🌾", "value": 0, "consumable": True},
    {"name": "wheat", "emoji": "🌾", "value": 0, "consumable": True},
    {"name": "milk", "emoji": "🥛", "value": 8, "consumable": True},
    {"name": "cheese", "emoji": "🧀", "value": 10, "consumable": True},
    {"name": "lettuce", "emoji": "🥬", "value": 2, "consumable": True},
    {"name": "tomato", "emoji": "🍅", "value": 2, "consumable": True},
    {"name": "onion", "emoji": "🧅", "value": 1, "consumable": True},
    {"name": "garlic", "emoji": "🧄", "value": 0, "consumable": True},
    {"name": "ginger", "emoji": "🫚", "value": 0, "consumable": True},
    {"name": "mushroom", "emoji": "🍄", "value": 2, "consumable": True},
    {"name": "pepper", "emoji": "🌶️", "value": 2, "consumable": True},
    {"name": "potato", "emoji": "🥔", "value": 2, "consumable": True},
    {"name": "coconut", "emoji": "🥥", "value": 2, "consumable": True},
    {"name": "pineapple", "emoji": "🍍", "value": 2, "consumable": True},
]


all_tools = [
    {"name": "oven", "emoji": "🔥", "value": 0, "consumable": False},
    {"name": "knife", "emoji": "🔪", "value": 0, "consumable": False},
    {"name": "salt", "emoji": "🧂", "value": 0, "consumable": False},
    {"name": "bowl", "emoji": "🥣", "value": 0, "consumable": False},
    {"name": "pot", "emoji": "🥘", "value": 0, "consumable": False},
    {"name": "stove", "emoji": "🔥", "value": 0, "consumable": False},
]

universal_items = [
    {"name": "water", "emoji": "💧", "value": 0, "consumable": False},
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
        self.best_value = 0

    def reset(self, seed=None, options=None):
        """
        Get an initial state consisting of basic ingredients.
        """
        # get the item names and delete the reasoning
        ingredients = random.sample(all_ingredients, 5)
        tools = random.sample(all_tools, 2)
        self.inventory = universal_items + tools + ingredients
        self.best_value = max(item["value"] for item in self.inventory)

        return self.inventory

    def reset_world_model(self):
        """
        Reset the world model.
        """
        self.world_model = MemoizedWorldModel(lm=self.model)

    def step(self, action: tuple[str, str]):
        """
        Take an action in the environment.
        """
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

        # reward is the difference between the new item and the best value
        reward = max(new_item["value"] - self.best_value, 0)
        self.best_value = max(self.best_value, new_item["value"])

        # update the inventory
        self.inventory.append(new_item)

        return self.inventory, reward, False, {}

    def render(self):
        """
        Render the environment.
        """
        print("Inventory:")
        for item in self.inventory:
            print(f"{item['emoji']} {item['name']}, tastiness: {item['value']}")
