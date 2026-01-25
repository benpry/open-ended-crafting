import json
from dataclasses import replace

import gymnasium as gym
from google.genai import types

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
        # GameDescriptor already validates and instantiates Tool/Ingredient objects.
        # Keep compatibility if a raw mapping ever slips through.
        self.tools = [Tool(**x) if isinstance(x, dict) else x for x in descriptor.tools]
        self.ingredients = [
            Ingredient(**x) if isinstance(x, dict) else x
            for x in descriptor.ingredients
        ]
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


# Language model crafting game
SYSTEM_PROMPT = """You are playing a crafting game. Your goal is to craft valuable items. Each item has features that determine how it combines with other items and how valuable it is. Some items are tools and others are ingredients. Tools can be used only once, while ingredients can be used as many times as you want. Using tools will change an item's features, while combining ingredients will create a new combined item. Your overall score is the value of the most valuable item in your inventory at the time you submit, but it cannot drop below 0. The maximum possible value is 100. You will have to learn the rules for how items combine, what the tools do, and how values are determined in order to achieve high scores. You should respond in JSON and follow this format:
```json
{
    "reasoning": "a one or two sentence explanation of why you chose this action",
    "action": "either a list of the names of two items in the inventory or the string 'submit'"
}
```
The action should include only the item names, not the emoji.
"""


class LMCraftingGame(gym.Env):
    """
    A wrapper around the oecraft crafting game that allows for language model interaction.
    """

    def __init__(self, env: CraftingGame):
        self.env = env
        self.prompt_history = []

    def clear_history(self):
        self.prompt_history = []

    def _append_user_message(self, content: str):
        if self.prompt_history and self.prompt_history[-1].role == "user":
            # add the new content to the last message
            self.prompt_history = self.prompt_history[:-1] + [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=self.prompt_history[-1].parts[0].text
                            + "\n\n"
                            + content
                        )
                    ],
                )
            ]
        else:
            self.prompt_history.append(
                types.Content(role="user", parts=[types.Part.from_text(text=content)])
            )

    def reset(
        self,
        seed: int | None = None,
        options: dict | None = None,
    ):
        self.env.reset(seed=seed, options=options)
        if len(self.prompt_history) == 0:
            self.prompt_history = []
            self._append_user_message("Starting inventory:\n" + self.env.render())
        else:
            self._append_user_message(
                "You have begun a new round.\nStarting inventory:\n" + self.env.render()
            )

    def parse_action(self, action: str):
        # parse the action
        action_json = json.loads(action)
        if "reasoning" not in action_json:
            raise ValueError("Action must contain a 'reasoning' field")
        if "action" not in action_json:
            raise ValueError("Action must contain an 'action' field")

        # "action" should have either a pair of items or the string "submit"
        if action_json["action"] == "submit":
            return action_json
        elif (
            isinstance(action_json["action"], list) and len(action_json["action"]) == 2
        ):
            return action_json
        else:
            raise ValueError(
                "Action must contain a pair of items or the string 'submit'"
            )

    def format_obs(self, obs: dict):
        new_item = obs["new_item"]
        if new_item is not None:
            new_item_features = self.env.descriptor_fn(
                new_item, self.env.world_model.feature_names
            )
            inventory_formatted = f"""New item: {new_item.emoji} {new_item.name}, value: {new_item.value}, features: {new_item_features}
Current inventory:\n""" + self.env.render()
        else:
            inventory_formatted = "Current inventory:\n" + self.env.render()

        inventory_formatted += f"Current score: {self.env.get_reward()}"

        return inventory_formatted

    def inner_step(self, action: str):
        # parse the action
        action_json = self.parse_action(action)

        # format the action to be passed to the environment
        if action_json["action"] == "submit":
            env_action = None
        else:
            env_action = action_json["action"]

        # execute the action
        obs, reward, terminated, info = self.env.step(env_action)

        self._append_user_message(self.format_obs(obs))

        return obs, reward, terminated, info

    def step(self, action: str):
        self.prompt_history.append(
            types.Content(role="model", parts=[types.Part.from_text(text=action)])
        )

        try:
            obs, reward, terminated, info = self.inner_step(action)
        except ValueError as e:
            self._append_user_message(f"Error: {e}\nPlease try again.")
            obs = {
                "inventory": self.env.inventory,
                "new_item": None,
            }
            reward = 0
            terminated = False
            info = {}

        return obs, reward, terminated, info

    def get_prompt_history(self):
        return self.prompt_history[:]

    def add_message_to_history(self, message: str):
        self._append_user_message(
            f"You received the following message from a previous player trying to help you:\n{message}"
        )

    def get_reward(self):
        return self.env.get_reward()
