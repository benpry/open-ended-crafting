"""
Code for tagging messages automatically using a language model.
"""

import os
import warnings
from argparse import ArgumentParser

import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
from pyprojroot import here
from tenacity import retry, stop_after_attempt, wait_exponential


class TaggingResult(BaseModel):
    abstractions: bool
    concrete_recipes: bool
    positive_valence: bool
    negative_valence: bool
    policy: bool
    dynamics: bool
    avoidance: bool


system_prompt = """
You will be shown a series of messages that human participants wrote to each other while playing a crafting game. The highest possible score in this game is 100. Your job is to tag each of the messages along the following dimensions:
1. abstractions: Does the message have abstractions? An abstraction is any information about the game and how it works that is more general than a specific recipe.
2. concrete_recipes: Does the message have concrete recipes? A concrete recipe is a description of specific items to combine and what they make or how valuable the result is. This must include specific item names (e.g. "elephant + whale" and not item features like "land animal + ocean animal"). Stating what tools to use on specific item names also counts as a concrete recipe.
3. positive_valence: Does the message talk about positively-valenced ideas and mention winning or achieving high scores? Just telling someone what to do to does not count. The message must talk about winning, success, using words like "good," "best," or "favorable," or achieving a high score (a score of 100 is the maximum).
4. negative_valence: Does the message talk about negatively-valenced ideas and mention losing or not being able to achieve a score above a certain threshold? Talking about not doing well or being confused counts as negative valence. Mentioning that something leads to negative value alone is not enough for the message ito include negative valence.
5. policy: Does the message talk about policy, meaning what people should do or not do?
6. dynamics: Does the message talk about the dynamics of the game environment and how it works? This includes discussion how tools influence the features and what increases or decreases the score of an item. For a message to include dynamics, it can't just tell the reader what to do. It has to discuss what happens when the player makes different combinations.
7. avoidance: Does the message talk about what to avoid or what leads to failure? This includes discussion of what not to do or what leads to a low score. Just mentioning that something creates negative value is not enough for avoidance. The message must either say not to do something or make it very clear that doing something will lead to a low score.

For each message, you should respond with a JSON object containing a single boolean value for each of the six dimensions. You will need to respond in JSON and follow this format:
```json
{
    "abstractions": bool,
    "concrete_recipes": bool,
    "positive_valence": bool,
    "negative_valence": bool,
    "policy": bool,
    "dynamics": bool,
    "avoidance": bool,
}
```
"""


def get_ic_examples(filepath: str):
    messages = []
    df_ic = pd.read_csv(here(filepath))
    for index, row in df_ic.iterrows():
        messages.append(
            {
                "role": "user",
                "content": row["message"],
            }
        )
        result = TaggingResult(
            abstractions=bool(row["abstractions"]),
            concrete_recipes=bool(row["concrete_recipes"]),
            positive_valence=bool(row["positive_valence"]),
            negative_valence=bool(row["negative_valence"]),
            policy=bool(row["policy"]),
            dynamics=bool(row["dynamics"]),
            avoidance=bool(row["avoidance"]),
        )
        messages.append(
            {
                "role": "assistant",
                "content": result.model_dump_json(),
            }
        )

    return messages


@retry(stop=stop_after_attempt(10), wait=wait_exponential())
def get_completion(
    messages: list[dict], client: OpenAI, model_name: str
) -> tuple[TaggingResult, dict[str, float | None]]:
    response = client.chat.completions.parse(
        model=model_name,
        messages=messages,
        response_format=TaggingResult,
    )
    parsed = response.choices[0].message.parsed
    return parsed


def tag_message(
    message: str, base_messages: list[dict], client: OpenAI, model_name: str
) -> tuple[TaggingResult, dict[str, float | None]]:
    messages = [
        *base_messages,
        {"role": "user", "content": message},
    ]
    return get_completion(messages, client, model_name)


def main(args):
    if "fireworks" in args.tagging_model:
        client = OpenAI(
            api_key=os.getenv("FIREWORKS_AI_API_KEY"),
            base_url="https://api.fireworks.ai/inference/v1/",
        )
    elif "gpt" in args.tagging_model:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif "gemini" in args.tagging_model:
        client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        )
    else:
        raise ValueError(f"Invalid model name: {args.tagging_model}")

    base_messages = [
        {"role": "system", "content": system_prompt},
    ]
    base_messages += get_ic_examples(args.ic_filepath)

    df_to_tag = pd.read_csv(here(args.eval_filepath))
    for index, row in df_to_tag.iterrows():
        tagging_result = tag_message(
            row["message"], base_messages, client, args.tagging_model
        )
        if tagging_result is None:
            warnings.warn(f"Received None when tagging message {index}")
            continue
        df_to_tag.at[index, "abstractions_lm"] = tagging_result.abstractions
        df_to_tag.at[index, "concrete_recipes_lm"] = tagging_result.concrete_recipes
        df_to_tag.at[index, "positive_valence_lm"] = tagging_result.positive_valence
        df_to_tag.at[index, "negative_valence_lm"] = tagging_result.negative_valence
        df_to_tag.at[index, "policy_lm"] = tagging_result.policy
        df_to_tag.at[index, "dynamics_lm"] = tagging_result.dynamics
        df_to_tag.at[index, "avoidance_lm"] = tagging_result.avoidance

    df_to_tag.to_csv(
        here(args.eval_filepath.replace(".csv", "_lm_tags.csv")), index=False
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--ic_filepath",
        type=str,
        default="data/human-data/experiment-1/processed/message-tags-ic.csv",
    )
    parser.add_argument(
        "--tagging_model",
        type=str,
        default="fireworks/deepseek-v3p2",
    )
    parser.add_argument(
        "--eval_filepath",
        type=str,
        default="data/human-data/experiment-1/processed/messages.csv",
    )
    args = parser.parse_args()
    main(args)
