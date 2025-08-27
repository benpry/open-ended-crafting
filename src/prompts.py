"""
This file contains prompts for the language model.
"""

import os
from dataclasses import asdict

import instructor
from groq import Groq
from pydantic import BaseModel

from src.combo_functions import FEATURE_NAMES
from src.constants import IC_EXAMPLES, SYSTEM_PROMPTS, Item

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
client = instructor.from_groq(client, mode=instructor.Mode.JSON)


class ItemSemantics(BaseModel):
    emoji: str
    name: str


def item_to_dict(item: Item, feature_names: dict) -> Item:
    item_dict = asdict(item)
    for feature, value in item_dict.items():
        if feature in feature_names:
            item_dict[feature] = feature_names[feature][value]
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
    dict_outcome = item_to_dict(outcome, feature_names)

    messages += [
        {
            "role": "user",
            "content": f"Item 1: {dict_item1}\nItem 2: {dict_item2}\nOutcome: {dict_outcome}",
        },
    ]

    return messages


def call_model(messages: list, lm_string: str) -> dict:
    semantics = client.completions.create(
        model=lm_string, messages=messages, response_model=ItemSemantics, max_retries=5
    )

    semantics = semantics.model_dump()

    if len(semantics["emoji"]) > 3:
        semantics["emoji"] = semantics["emoji"][:3]

    return semantics


def get_item_semantics_from_lm(
    inputs: list, outcome: dict, domain: str, lm_string: str, ic_examples: list
) -> dict:
    # compile a list of messages to send to the LM

    all_ic_examples = IC_EXAMPLES[domain] + ic_examples

    messages = get_combination_messages(
        inputs[0], inputs[1], outcome, domain, all_ic_examples
    )

    semantics = call_model(messages, lm_string)

    return semantics
