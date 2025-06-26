"""
This file handles interfacing with the language model to get new crafting instructions.
"""

import json
from ast import literal_eval

import networkx as nx

from src.combo_functions import COMBO_FUNCTIONS
from src.prompts import get_item_semantics_from_lm


def check_if_same_item(e1, e2):
    for feature, value in e1.items():
        if e2[feature] != value:
            return False
    return True


class MemoizedWorldModel:
    def __init__(self, lm, domain, assign_names=False):
        self.lm = lm
        self.ic_examples = []
        self.domain = domain
        self.combinations = {}
        self.combo_function = COMBO_FUNCTIONS[self.domain]
        self.assign_names = assign_names

    def combine_elements(self, e1, e2):
        new_item = self.combo_function(e1, e2)
        if new_item is None:
            return None

        # If one of the items is a tool and the output features are the same as the input features,
        # then the output is the same as the input
        if e1["tool"] and check_if_same_item(new_item, e2):
            return e2.copy()
        elif e2["tool"] and check_if_same_item(new_item, e1):
            return e1.copy()

        if self.assign_names:
            semantics = get_item_semantics_from_lm(
                [e1, e2], new_item, self.domain, self.lm, self.ic_examples
            )
            self.ic_examples.append(
                {
                    "input": [e1, e2],
                    "outcome": new_item.copy(),
                    "semantics": semantics,
                }
            )

            new_item["name"] = semantics["name"]
            new_item["emoji"] = semantics["emoji"]

        else:
            new_item["name"] = f"[{e1['name']}]-[{e2['name']}]"
            new_item["emoji"] = "❓"

        return new_item

    def combine(self, e1, e2):
        items = frozenset((e1["name"], e2["name"]))

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
            inps = tuple(combo)
            combinations_lsts[str(inps)] = result

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
            self.combinations[frozenset(literal_eval(combo))] = literal_eval(result)

    def loads(self, data: str):
        world_model_dict = json.loads(data)
        self.lm = world_model_dict["lm"]
        self.assign_names = world_model_dict["assign_names"]
        self.ic_examples = world_model_dict["ic_examples"]
        self.combinations = {}
        for combo, result in world_model_dict["combinations"].items():
            self.combinations[frozenset(literal_eval(combo))] = literal_eval(result)

    def dumps(self):
        combinations_lsts = {}
        for combo, result in self.combinations.items():
            inps = tuple(combo)
            combinations_lsts[str(inps)] = result

        world_model_dict = {
            "lm": self.lm,
            "combinations": combinations_lsts,
            "ic_examples": self.ic_examples,
            "assign_names": self.assign_names,
        }

        return json.dumps(world_model_dict)

    def make_graph(self):
        G = nx.DiGraph()
        for inputs, output in self.combinations.items():
            G.add_node(output)
            for inp in inputs:
                G.add_node(inp)
                G.add_edge(inp, output)

        return G


if __name__ == "__main__":
    model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
