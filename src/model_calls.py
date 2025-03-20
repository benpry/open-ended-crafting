"""
This file handles interfacing with the language model to get new crafting instructions.
"""

from litellm import completion
from src.prompts import get_initialization_prompt, get_combination_prompt
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


def get_initial_inventory(model):
    messages = get_initialization_prompt()
    response = completion(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Inventory",
                "schema": Inventory.model_json_schema(),
            },
        },
        temperature=0.8,
    )

    content = response.choices[0].message.content
    inventory = Inventory.model_validate_json(content)
    return inventory


def combine_elements(e1, e2, model):
    messages = get_combination_prompt(e1, e2)
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


if __name__ == "__main__":
    # model = "openai/gpt-4o"
    # model = "fireworks_ai/accounts/fireworks/models/mistral-small-24b-instruct-2501"
    # model = "fireworks_ai/accounts/fireworks/models/deepseek-v3"
    model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
    # model = "anthropic/claude-3-7-sonnet-20250219"

    inventory = get_initial_inventory(model)
    print(inventory)

    print(f"combining {inventory.items[0]} and {inventory.items[1]}")
    new_item = combine_elements(inventory.items[0], inventory.items[1], model)
    print(new_item)
