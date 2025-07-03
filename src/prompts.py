"""
This file contains prompts for the language model.
"""

import os

import instructor
from groq import Groq
from pydantic import BaseModel

from src.combo_functions import FEATURE_NAMES
from src.constants import SYSTEM_PROMPTS

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
client = instructor.from_groq(client, mode=instructor.Mode.JSON)


class ItemSemantics(BaseModel):
    emoji: str
    name: str


def apply_feature_names(item: dict, feature_names: dict) -> dict:
    updated_item = item.copy()
    print(item)
    for feature, value in item.items():
        if feature in feature_names:
            print(feature, value)
            updated_item[feature] = feature_names[feature][value]
    return updated_item


def get_combination_messages(e1, e2, o, domain, ic_examples):
    system_prompt = SYSTEM_PROMPTS[domain]
    feature_names = FEATURE_NAMES[domain]

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # the first and last 2 examples are used for the prompt
    if len(ic_examples) > 4:
        ic_examples = ic_examples[:2] + ic_examples[-2:]

    for example in ic_examples:
        item1, item2 = example["input"]
        outcome = example["outcome"]
        item1 = apply_feature_names(item1, feature_names)
        item2 = apply_feature_names(item2, feature_names)
        outcome = apply_feature_names(outcome, feature_names)
        semantics = example["semantics"]

        messages.append(
            {
                "role": "user",
                "content": f"Item 1: {item1}\nItem 2: {item2}\nOutcome: {outcome}",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": f"{semantics}",
            }
        )

    messages += [
        {"role": "user", "content": f"Item 1: {e1}\nItem 2: {e2}\nOutcome: {o}"},
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

    messages = get_combination_messages(
        inputs[0], inputs[1], outcome, domain, ic_examples
    )

    semantics = call_model(messages, lm_string)

    return semantics
