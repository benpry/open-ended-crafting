"""
This file contains prompts for the language model.
"""

import backoff
from litellm import completion
from pydantic import BaseModel

from src.combo_functions import FEATURE_NAMES
from src.constants import SYSTEM_PROMPTS


class ItemSemantics(BaseModel):
    emoji: str
    name: str


def apply_feature_names(item: dict, feature_names: dict) -> dict:
    updated_item = item.copy()
    for feature, value in item.items():
        if feature in feature_names:
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


@backoff.on_exception(backoff.expo, Exception, max_tries=8)
def call_model(messages: list, lm_string: str) -> str:
    try:
        response = completion(
            model=lm_string,
            messages=messages,
            response_format=ItemSemantics,
            max_completion_tokens=4096,
            temperature=0.2,
        )
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Full error: {repr(e)}")
        raise e

    print("response:")
    print(response)

    content = response.choices[0].message.content
    if content is None:
        print("No content")
        print(messages)
        print(lm_string)
        raise Exception("No content")

    semantics = ItemSemantics.model_validate_json(content).model_dump()
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
