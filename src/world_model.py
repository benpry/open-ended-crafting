"""
This file handles interfacing with the language model to get new crafting instructions.
"""

import json
from ast import literal_eval
from dataclasses import asdict, replace

from frozendict import frozendict

from src.constants import CombinedItem, Item, NonTool, Tool
from src.functions import COMBO_FUNCTIONS
from src.prompts import get_item_semantics_from_lm
from src.utils import dict_to_dataclass


def freeze_item(item: Item) -> Item:
    if isinstance(item, Tool):
        return item

    if isinstance(item, CombinedItem):
        return replace(
            item,
            ingredients=tuple([freeze_item(ing) for ing in item.ingredients]),
            features=frozendict(item.features),
        )
    else:
        return replace(item, features=frozendict(item.features))


def thaw_item(item: Item) -> Item:
    if isinstance(item, Tool):
        return item

    if isinstance(item, CombinedItem):
        return CombinedItem(
            **asdict(item),
            ingredients=[thaw_item(ing) for ing in item.ingredients],
            features=dict(item.features),
        )
    else:
        return replace(item, features=dict(item.features))


def check_if_same_item(e1: NonTool, e2: NonTool) -> bool:
    if type(e1) is not type(e2):
        return False
    elif isinstance(e1, CombinedItem):
        return e1.ingredients == e2.ingredients and e1.features == e2.features
    else:
        return e1.features == e2.features


class MemoizedWorldModel:
    def __init__(self, lm, domain, assign_names=False):
        self.lm = lm
        self.ic_examples = []
        self.domain = domain
        self.combinations = {}
        self.combo_function = COMBO_FUNCTIONS[self.domain]
        self.assign_names = assign_names

    def combine_elements(self, e1: Item, e2: Item):
        new_item = self.combo_function(e1, e2)
        if new_item is None:
            return None

        # If one of the items is a tool and the output features are the same as the input features,
        # then the output is the same as the input
        if e1.tool and check_if_same_item(new_item, e2):
            return e2
        elif e2.tool and check_if_same_item(new_item, e1):
            return e1

        if self.assign_names:
            # if we applied a tool to a combined item, we need to assign names to the updated ingredients
            if (
                isinstance(e1, CombinedItem)
                and isinstance(e2, Tool)
                and e2.name != "frame"
            ):
                for i in range(len(new_item.ingredients)):
                    named_ingredient = self.combine(e1.ingredients[i], e2)
                    new_item.ingredients[i] = replace(
                        new_item.ingredients[i],
                        name=named_ingredient.name,
                        emoji=named_ingredient.emoji,
                    )
            elif (
                isinstance(e2, CombinedItem)
                and isinstance(e1, Tool)
                and e1.name != "frame"
            ):
                for i in range(len(new_item.ingredients)):
                    named_ingredient = self.combine(e1, e2.ingredients[i])
                    new_item.ingredients[i] = replace(
                        new_item.ingredients[i],
                        name=named_ingredient.name,
                        emoji=named_ingredient.emoji,
                    )

            semantics = get_item_semantics_from_lm(
                [e1, e2], new_item, self.domain, self.lm, self.ic_examples
            )
            self.ic_examples.append(
                {
                    "input": [e1, e2],
                    "outcome": new_item,
                    "semantics": semantics,
                }
            )

            new_item = replace(
                new_item, name=semantics["name"], emoji=semantics["emoji"]
            )

        else:
            if isinstance(e1, CombinedItem) and isinstance(e2, Tool):
                for i in range(len(new_item.ingredients)):
                    new_item.ingredients[i] = replace(
                        new_item.ingredients[i],
                        name=f"[{e1.ingredients[i].name}-{e2.name}]",
                        emoji="❓",
                    )
            elif isinstance(e2, CombinedItem) and isinstance(e1, Tool):
                for i in range(len(new_item.ingredients)):
                    new_item.ingredients[i] = replace(
                        new_item.ingredients[i],
                        name=f"[{e1.name}-{e2.ingredients[i].name}]",
                        emoji="❓",
                    )

            new_item = replace(new_item, name=f"[{e1.name}]-[{e2.name}]", emoji="❓")

        return new_item

    def combine(self, e1, e2):
        items = frozenset((freeze_item(e1), freeze_item(e2)))

        # check if we've already combined these items
        if items in self.combinations:
            new_item = self.combinations[items][-1]
        else:
            # otherwise, actually combine the items
            new_item = self.combine_elements(e1, e2)
            if new_item is not None:
                self.combinations[items] = (e1, e2, new_item)

        return new_item

    def save(self, filepath: str):
        combinations_lsts = {}
        for combo, result in self.combinations.items():
            inps = tuple(thaw_item(x) for x in combo)
            combinations_lsts[inps] = tuple(asdict(x) for x in result)

        world_model_dict = {
            "lm": self.lm,
            "combinations": combinations_lsts,
            "ic_examples": self.ic_examples,
            "assign_names": self.assign_names,
        }

        with open(filepath, "w") as f:
            json.dump(world_model_dict, f)

    def load(self, filepath: str):
        with open(filepath, "r") as f:
            world_model_dict = json.load(f)
        self.lm = world_model_dict["lm"]
        self.assign_names = world_model_dict["assign_names"]
        self.ic_examples = world_model_dict["ic_examples"]
        self.combinations = {}
        for combo, result in world_model_dict["combinations"].items():
            combo = frozenset(
                freeze_item(dict_to_dataclass(x)) for x in literal_eval(combo)
            )
            self.combinations[combo] = dict_to_dataclass(literal_eval(result))

    def loads(self, data: str):
        world_model_dict = json.loads(data)
        self.lm = world_model_dict["lm"]
        self.assign_names = world_model_dict["assign_names"]
        ic_examples = world_model_dict["ic_examples"]
        self.ic_examples = []
        for example in ic_examples:
            self.ic_examples.append(
                {
                    "input": [dict_to_dataclass(x) for x in example["input"]],
                    "outcome": dict_to_dataclass(example["outcome"]),
                    "semantics": example["semantics"],
                }
            )

        self.combinations = {}
        for combo, result in world_model_dict["combinations"].items():
            combo = frozenset(
                freeze_item(dict_to_dataclass(x)) for x in literal_eval(combo)
            )
            self.combinations[combo] = [dict_to_dataclass(x) for x in result]

    def dumps(self):
        combinations_lsts = {}
        for combo, result in self.combinations.items():
            inps = tuple(asdict(thaw_item(x)) for x in combo)
            combinations_lsts[str(inps)] = tuple(asdict(x) for x in result)

        ic_examples = []
        for example in self.ic_examples:
            ic_examples.append(
                {
                    "input": [asdict(x) for x in example["input"]],
                    "outcome": asdict(example["outcome"]),
                    "semantics": example["semantics"],
                }
            )

        world_model_dict = {
            "lm": self.lm,
            "combinations": combinations_lsts,
            "ic_examples": ic_examples,
            "assign_names": self.assign_names,
        }

        return json.dumps(world_model_dict)
