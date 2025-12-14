from dataclasses import replace

import gymnasium as gym

from oecraft.types import CombinedItem, GameDescriptor, Ingredient, Tool
from oecraft.utils import load_function_from_string
from oecraft.world_model import MemoizedWorldModel


class CraftingGame(gym.Env):
    def __init__(
        self,
        descriptor: GameDescriptor,
        model: str,
        n_starting_ingredients: int = 4,
        assign_names: bool = False,
    ):
        self.value_fn = load_function_from_string(descriptor.value_fn, "value_fn")
        self.get_inventory_fn = load_function_from_string(
            descriptor.get_inventory_fn, "get_inventory_fn"
        )
        self.descriptor_fn = load_function_from_string(
            descriptor.descriptor_fn, "descriptor_fn"
        )
        self.tools = [Tool(**x) for x in descriptor.tools]
        self.ingredients = [Ingredient(**x) for x in descriptor.ingredients]
        self.model = model
        self.n_starting_ingredients = n_starting_ingredients

        self.world_model = MemoizedWorldModel(
            lm=self.model,
            combo_function_str=descriptor.combination_fn,
            assign_names=assign_names,
            naming_system_prompt=descriptor.naming_system_prompt,
            naming_ic_examples=descriptor.naming_ic_examples,
            feature_names=descriptor.feature_names,
        )

        self.inventory = []

    def reset(self, seed: int | None = None, options: dict | None = None):
        ingredients = self.get_inventory_fn(
            self.n_starting_ingredients, self.ingredients
        )

        # assign values to the ingredients
        for ingredient in ingredients:
            ingredient = replace(ingredient, value=self.value_fn(ingredient))

        # get features for the ingredients
        ingredients = [
            replace(
                ingredient,
                description=self.descriptor_fn(
                    ingredient, self.world_model.feature_names
                ),
            )
            for ingredient in ingredients
        ]

        self.inventory = self.tools + ingredients

        print(f"starting inventory: {self.inventory}")

        return self.inventory

    def render(self):
        """
        Render the environment.
        """
        ret = ""
        for item in self.inventory:
            if isinstance(item, Tool):
                ret += f"Tool: {item.emoji} {item.name}\n"
            elif isinstance(item, Ingredient):
                features = self.descriptor_fn(item, self.world_model.feature_names)
                ret += f"Ingredient: {item.emoji} {item.name}, value: {item.value}, features: {features}\n"
            elif isinstance(item, CombinedItem):
                print(f"feature names: {self.world_model.feature_names}")
                features = self.descriptor_fn(
                    item, feature_names=self.world_model.feature_names
                )
                component_features = "; ".join(
                    [
                        f"{ing.emoji} {ing.name}: {self.descriptor_fn(ing, feature_names=self.world_model.feature_names)}"
                        for ing in item.ingredients
                    ]
                )
                ret += f"Combined item: {item.emoji} {item.name}, value: {item.value}, features: {features}, components: {component_features}\n"

        return ret

    def reset_world_model(self):
        """
        Reset the world model.
        """
        self.world_model = MemoizedWorldModel(lm=self.model)

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

    def step(self, action: tuple[str, str] | None):
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

        inv_names = [item.name for item in self.inventory]

        # check if the items are in the inventory
        if name1 not in inv_names:
            raise ValueError(
                f"Item {name1} not in inventory. Inventory contains the following items: {', '.join(inv_names)}"
            )
        if name2 not in inv_names:
            raise ValueError(
                f"Item {name2} not in inventory. Inventory contains the following items: {', '.join(inv_names)}"
            )

        # get the items
        item1 = next(item for item in self.inventory if item.name == name1)
        item2 = next(item for item in self.inventory if item.name == name2)

        # if the user tries to combine two tools, do nothing
        if isinstance(item1, Tool) and isinstance(item2, Tool):
            obs = {
                "inventory": self.inventory,
                "new_item": None,
            }
            return obs, 0, False, {}

        # remove non-tool items (ingredients get consumed)
        # Tools are durable and stay in inventory, ingredients are consumed
        if not isinstance(item1, Tool):
            self.inventory.remove(item1)
        if not isinstance(item2, Tool):
            self.inventory.remove(item2)

        # combine the items
        new_item = self.world_model.combine(item1, item2)

        # compute the value of the new item
        new_item = replace(new_item, value=self.value_fn(new_item))

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
        ingredients = [item for item in self.inventory if not isinstance(item, Tool)]
        # the reward is the value of the most valuable ingredient
        reward = max(item.value for item in ingredients)

        return max(reward, 0)
