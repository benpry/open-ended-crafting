"""
This file contains prompts for the language model.
"""

import os
from dataclasses import asdict, replace

import httpx
import instructor
from groq import Groq
from pydantic import BaseModel

from src.constants import IC_EXAMPLES, SYSTEM_PROMPTS, CombinedItem, Item, Tool
from src.functions import FEATURE_NAMES

http_client = httpx.Client()

client = Groq(
    http_client=http_client,
    api_key=os.getenv("GROQ_API_KEY"),
)
client = instructor.from_groq(client, mode=instructor.Mode.JSON)


class ItemSemantics(BaseModel):
    emoji: str
    name: str


def item_to_dict(item: Item, feature_names: dict) -> Item:
    item_dict = asdict(item)

    # if the item is a tool, we don't need to do anything else
    if isinstance(item, Tool):
        return item_dict

    # convert the item's features to strings
    for feature, value in item_dict["features"].items():
        if feature in feature_names:
            item_dict["features"][feature] = feature_names[feature][value]
    if isinstance(item, CombinedItem):
        item_dict["ingredients"] = [
            item_to_dict(x, feature_names) for x in item.ingredients
        ]
    return item_dict


def get_combination_messages(
    item1: Item, item2: Item, outcome: Item, domain: str, ic_examples: list
) -> list:
    system_prompt = SYSTEM_PROMPTS[domain]
    feature_names = FEATURE_NAMES[domain]

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # the first and last 2 examples are used for the prompt
    if len(ic_examples) > 4:
        ic_examples = ic_examples[:2] + ic_examples[-2:]

    for example in ic_examples:
        example_item1, example_item2 = example["input"]
        example_outcome = example["outcome"]
        dict_item1 = item_to_dict(example_item1, feature_names)
        dict_item2 = item_to_dict(example_item2, feature_names)
        dict_outcome = item_to_dict(example_outcome, feature_names)
        semantics = example["semantics"]

        messages.append(
            {
                "role": "user",
                "content": f"Item 1: {dict_item1}\nItem 2: {dict_item2}\nOutcome: {dict_outcome}",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": f"{semantics}",
            }
        )

    dict_item1 = item_to_dict(item1, feature_names)
    dict_item2 = item_to_dict(item2, feature_names)
    # make sure the outcome doesn't have a name or emoji
    outcome = replace(outcome, name="", emoji="")
    dict_outcome = item_to_dict(outcome, feature_names)

    messages += [
        {
            "role": "user",
            "content": f"Item 1: {dict_item1}\nItem 2: {dict_item2}\nOutcome: {dict_outcome}",
        },
    ]

    return messages


def call_model(messages: list, lm_string: str) -> dict:
    semantics, completion = client.completions.create_with_completion(
        model=lm_string,
        messages=messages,
        response_model=ItemSemantics,
        max_retries=5,
        reasoning_effort="medium",
    )

    semantics = semantics.model_dump()

    if len(semantics["emoji"]) > 3:
        semantics["emoji"] = semantics["emoji"][:3]

    return semantics


def get_item_semantics_from_lm(
    inputs: list, outcome: dict, domain: str, lm_string: str, ic_examples: list
) -> dict:
    all_ic_examples = IC_EXAMPLES[domain] + ic_examples
    messages = get_combination_messages(
        inputs[0], inputs[1], outcome, domain, all_ic_examples
    )
    semantics = call_model(messages, lm_string)

    return semantics
