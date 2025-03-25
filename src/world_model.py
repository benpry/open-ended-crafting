"""
This file handles interfacing with the language model to get new crafting instructions.
"""

from litellm import completion
from src.prompts import get_combination_prompt
from pydantic import BaseModel


class Item(BaseModel):
    reasoning: str
    name: str
    emoji: str
    value: int
    consumable: bool


class Inventory(BaseModel):
    reasoning: str
    items: list[Item]


def combine_elements(e1, e2, ic_examples, model):
    messages = get_combination_prompt(e1, e2, ic_examples)
    response = completion(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Item",
                "schema": Item.model_json_schema(),
            },
        },
        max_tokens=1000,
        temperature=0.8,
    )

    # Parse the response into a Pydantic model
    content = response.choices[0].message.content
    return Item.model_validate_json(content)


class MemoizedWorldModel:

    def __init__(self, lm):
        self.lm = lm
        self.combinations = {}

    def combine(self, e1, e2):
        items = frozenset((e1["name"], e2["name"]))
        if items in self.combinations:
            return self.combinations[items]

        else:
            new_item = combine_elements(e1, e2, self.combinations, self.lm)
            new_item = dict(new_item)
            del new_item["reasoning"]
            self.combinations[items] = new_item

            return new_item


if __name__ == "__main__":
    model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
