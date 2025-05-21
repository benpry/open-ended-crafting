"""
This file contains prompts for the language model.
"""

import json
from src.constants import SYSTEM_PROMPTS
from litellm import completion
from ast import literal_eval
import backoff
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    emoji: str
    value: int
    durable: bool


def get_combination_messages(e1, e2, game_type, ic_examples):
    system_prompt = SYSTEM_PROMPTS[game_type]

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Only use the last 10 examples for the prompt
    if len(ic_examples) > 20:
        ic_examples = ic_examples[:5] + ic_examples[-15:]

    for example in ic_examples:

        item1, item2 = example["input"]
        reasoning = example["reasoning"]
        outcome = example["output"]

        messages.append(
            {
                "role": "user",
                "content": f"Item 1: {item1}\nItem 2: {item2}",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": f"<reasoning>\n{reasoning}\n</reasoning>\n<output>\n{outcome}\n</output>",
            }
        )

    messages += [
        {"role": "user", "content": f"Item 1: {e1}\nItem 2: {e2}"},
    ]

    return messages


@backoff.on_exception(backoff.expo, Exception, max_tries=10)
def call_model(messages: list, lm_string: str) -> str:
    response = completion(
        model=lm_string,
        messages=messages,
        max_tokens=2048,
        temperature=0.6,
    )

    return response.choices[0].message.content


@backoff.on_exception(backoff.expo, Exception, max_tries=10)
def get_json_response(messages: list, partial_content: str, lm_string: str) -> dict:

    rephrase_messages = messages[:-1]
    last_message = messages[-1]
    last_message_content = last_message["content"]
    last_message["content"] = (
        f"You, but you did not produce valid JSON. Please provide a valid JSON object based on the reasoning you have provided.\n{last_message_content}\nreasoning:\n {partial_content}"
    )
    rephrase_messages.append(last_message)

    response = completion(
        model=lm_string,
        messages=rephrase_messages,
        response_format=Item,
        max_tokens=2048,
        temperature=0.6,
    )

    return response.choices[0].message.content


def get_item_from_lm(messages: list, lm_string: str) -> dict:
    content = call_model(messages, lm_string)

    print("response:")
    print(content)

    reasoning = None
    outcome = None
    item = None

    # get only the stuff between the <reasoning> and </reasoning> tags
    try:
        reasoning = content.split("<reasoning>")[1].split("</reasoning>")[0]
        outcome = content.split("<output>")[1].split("</output>")[0]
        item = literal_eval(outcome)
        if item is None:
            raise ValueError("Item is None")
    except (IndexError, SyntaxError, ValueError):
        print("Got index error")
        # the reasoning got cut off,
        if reasoning is None:
            reasoning = content
        outcome = get_json_response(messages, reasoning, lm_string)
        print(f"outcome:\n{outcome}")
        print(type(outcome))
        item = json.loads(outcome)

    print("item:")
    print(item)

    return item, reasoning
