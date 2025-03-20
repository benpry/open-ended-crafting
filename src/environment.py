import gymnasium as gym
from src.model_calls import get_initial_inventory, combine_elements


class CookingGame(gym.Env):
    """
    An open-ended LM-driven cooking game.
    """

    def __init__(self, model: str):
        super().__init__()
        self.model = model
        self.inventory = []
        self.best_value = 0

    def reset(self, seed=None, options=None):
        """
        Get an initial state consisting of basic ingredients.
        """
        inv_response = get_initial_inventory(self.model)

        # get the item names and delete the reasoning
        self.inventory = [dict(x) for x in inv_response.items]
        for item in self.inventory:
            del item["reasoning"]

        self.best_value = max(item["value"] for item in self.inventory)

        return self.inventory

    def step(self, action: dict):
        """
        Take an action in the environment.
        """
        item1, item2 = action["item1"], action["item2"]

        # check if the items are in the inventory
        if item1 not in self.inventory or item2 not in self.inventory:
            raise ValueError(f"Item {item1} or {item2} not in inventory")

        # remove consumable items
        if item1["consumable"]:
            self.inventory.remove(item1)
        if item2["consumable"]:
            self.inventory.remove(item2)

        # combine the items
        new_item = combine_elements(item1, item2, self.model)
        new_item = dict(new_item)
        del new_item["reasoning"]

        # reward is the difference between the new item and the best value
        reward = max(new_item["value"] - self.best_value, 0)
        self.best_value = max(self.best_value, new_item["value"])

        # update the inventory
        self.inventory.append(new_item)

        return self.inventory, reward, False, {}

    def render(self, mode="human"):
        """
        Render the environment.
        """
        print("Inventory:")
        for item in self.inventory:
            print(f"{item['emoji']} {item['name']}, tastiness: {item['value']}")
