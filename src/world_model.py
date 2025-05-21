"""
This file handles interfacing with the language model to get new crafting instructions.
"""

from litellm import completion
from src.prompts import get_combination_messages, get_item_from_lm
from src.constants import IC_EXAMPLES
from pydantic import BaseModel
from ast import literal_eval
import networkx as nx
import random
import json


class Item(BaseModel):
    reasoning: str
    name: str
    emoji: str
    value: int
    durable: bool


class Inventory(BaseModel):
    reasoning: str
    items: list[Item]


class MemoizedWorldModel:

    def __init__(self, lm, world_type):
        self.lm = lm
        self.combinations = {}
        self.base_ic_examples = IC_EXAMPLES[world_type]
        self.generated_ic_examples = []
        self.world_type = world_type

    def combine_elements(self, e1, e2):

        # take at most 5 self-generated examples
        if len(self.generated_ic_examples) < 5:
            ic_examples = self.base_ic_examples + self.generated_ic_examples
        else:
            ic_examples = self.base_ic_examples + random.sample(
                self.generated_ic_examples, 5
            )

        # get the resulting item and reasoning for it
        messages = get_combination_messages(e1, e2, self.world_type, ic_examples)
        item, reasoning = get_item_from_lm(messages, self.lm)

        # make sure we respect the invariants
        item["durable"] = e1["durable"] and e2["durable"]
        if item["durable"]:
            item["value"] = 0
        if len(item["emoji"]) > 3:
            item["emoji"] = item["emoji"][:3]

        # update the in-context examples with the new item
        self.generated_ic_examples.append(
            {"input": [e1, e2], "reasoning": reasoning, "output": item}
        )

        return item

    def combine(self, e1, e2):
        items = frozenset((e1["name"], e2["name"]))
        if items in self.combinations:
            new_item = self.combinations[items][-1]
        else:
            new_item = self.combine_elements(e1, e2)
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
            "ic_examples": self.generated_ic_examples,
        }

        with open(filepath, "w") as f:
            json.dump(world_model_dict, f)

    def load(self, filepath: str):
        with open(filepath, "r") as f:
            world_model_dict = json.load(f)
        self.lm = world_model_dict["lm"]
        self.generated_ic_examples = world_model_dict["ic_examples"]
        self.combinations = {}
        for combo, result in world_model_dict["combinations"].items():
            self.combinations[frozenset(literal_eval(combo))] = literal_eval(result)

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
