"""
This file contains prompts for the language model.
"""

import json
import os
from dataclasses import asdict, replace
from typing import Optional

import requests
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from oecraft.constants import IC_EXAMPLES, SYSTEM_PROMPTS, CombinedItem, Item, Tool
from oecraft.functions import FEATURE_NAMES


@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=2, max=60))
def get_completion(
    model: str,
    messages: list,
    response_model: BaseModel,
    max_retries: int = 5,
    groq_api_key: Optional[str] = None,
    reasoning_effort: str = "medium",
) -> dict:
    last_error = None

    if groq_api_key is None:
        groq_api_key = os.getenv("GROQ_API_KEY")

    for attempt in range(max_retries):
        try:
            # Get the schema and prepare it for Groq
            schema = response_model.model_json_schema()

            # Remove 'title' field if present and add required fields for structured outputs
            if "title" in schema:
                schema = {k: v for k, v in schema.items() if k != "title"}

            # Add additionalProperties: false for strict mode
            if "additionalProperties" not in schema:
                schema["additionalProperties"] = False

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "ItemSemantics",
                            "strict": True,
                            "schema": schema,
                        },
                    },
                    "reasoning_effort": reasoning_effort,
                },
            )

            # Check if the response is successful
            response.raise_for_status()

            # Try to parse the JSON response
            result = response.json()

            # Check if the response contains an error
            if "error" in result:
                last_error = result["error"]
                continue

            semantics = json.loads(result["choices"][0]["message"]["content"])

            # If we got a valid response, return it
            return semantics

        except (requests.RequestException, ValueError) as e:
            last_error = str(e)
            if attempt == max_retries - 1:
                # This was the last attempt, raise the error
                raise RuntimeError(
                    f"Failed to get valid completion after {max_retries} attempts. Last error: {last_error}"
                )

    # If we exhausted all retries due to API errors (not exceptions)
    raise RuntimeError(
        f"Failed to get valid completion after {max_retries} attempts. Last error: {last_error}"
    )


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


def call_model(
    messages: list,
    lm_string: str,
    reasoning_effort: str = "medium",
    groq_api_key: Optional[str] = None,
) -> dict:
    semantics = get_completion(
        model=lm_string,
        messages=messages,
        response_model=ItemSemantics,
        max_retries=5,
        reasoning_effort=reasoning_effort,
        groq_api_key=groq_api_key,
    )

    if len(semantics["emoji"]) > 3:
        semantics["emoji"] = semantics["emoji"][:3]

    return semantics


def get_item_semantics_from_lm(
    inputs: list,
    outcome: dict,
    domain: str,
    lm_string: str,
    ic_examples: list,
    reasoning_effort: str = "medium",
    groq_api_key: Optional[str] = None,
) -> dict:
    all_ic_examples = IC_EXAMPLES[domain] + ic_examples
    messages = get_combination_messages(
        inputs[0],
        inputs[1],
        outcome,
        domain,
        all_ic_examples,
    )
    semantics = call_model(messages, lm_string, reasoning_effort, groq_api_key)

    return semantics
