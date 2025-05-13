"""
This file handles interfacing with the language model to get new crafting instructions.
"""

from litellm import completion
from src.prompts import get_combination_prompt
from pydantic import BaseModel
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
        self.world_type = world_type

    def combine_elements(self, e1, e2):
        messages = get_combination_prompt(e1, e2, self.world_type)
        response = completion(
            model=self.lm,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "Item",
                    "schema": Item.model_json_schema(),
                },
            },
            max_tokens=2048,
            temperature=0.6,
        )

        # Parse the response into a Pydantic model
        content = response.choices[0].message.content
        return Item.model_validate_json(content)

    def combine(self, e1, e2):
        items = frozenset((e1["name"], e2["name"]))
        if items in self.combinations:
            new_item = self.combinations[items][-1]
        else:
            ic_examples = list(self.combinations.values())
            new_item = self.combine_elements(e1, e2)
            new_item = dict(new_item.model_copy(update={"exclude": {"reasoning"}}))
            if len(new_item["emoji"]) > 3:
                new_item["emoji"] = new_item["emoji"][:3]
            self.combinations[items] = (e1, e2, new_item)

        return new_item

    def save(self, filepath: str):
        world_model_dict = {
            "lm": self.lm,
            "combinations": self.combinations,
        }
        with open(filepath, "w") as f:
            json.dump(world_model_dict, f)

    def load(self, filepath: str):
        with open(filepath, "r") as f:
            world_model_dict = json.load(f)
        self.lm = world_model_dict["lm"]
        self.combinations = world_model_dict["combinations"]


if __name__ == "__main__":
    model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
