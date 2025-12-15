"""
Basic implementation for a language model agent that plays the crafting game.
"""

import json
import os
from types import SimpleNamespace

import pandas as pd
from openai import AsyncOpenAI, BadRequestError
from tenacity import retry, stop_after_attempt, wait_exponential

from oecraft.environment import LMCraftingGame

MESSAGE_PROMPT = """You have finished playing the crafting game. Now, please write a message to help a future player play the same game. The message can contain anything you want and should help the next player succeed.
Please respond in JSON and follow this format:
```json
{
    "message": "a message that will be passed to the next player"
}
```
"""


def return_failed_json_on_validation_error(retry_state):
    e = retry_state.outcome.exception()
    if isinstance(e, BadRequestError):
        if (
            isinstance(e.body, dict)
            and e.body.get("error", {}).get("code") == "json_validate_failed"
        ):
            failed_generation = e.body.get("error", {}).get("failed_generation", "")
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content=failed_generation))
                ]
            )
    raise e


@retry(
    stop=stop_after_attempt(15),
    wait=wait_exponential(),
    retry_error_callback=return_failed_json_on_validation_error,
)
async def get_completion(
    client: AsyncOpenAI,
    model: str,
    messages: list[dict],
    generate_kwargs: dict,
    max_tokens: int = 2048,
):
    return await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        **generate_kwargs,
        response_format={"type": "json_object"},
    )


class CraftingAgent:
    """
    A basic implementation for a language model agent that plays the crafting game.
    """

    def __init__(
        self, env: LMCraftingGame, model: str, api_base_url: str, generate_kwargs: dict
    ):
        self.env = env
        self.model = model
        self.generate_kwargs = generate_kwargs
        self.client = AsyncOpenAI(base_url=api_base_url)
        if "fireworks" in api_base_url:
            self.client.api_key = os.environ.get("FIREWORKS_API_KEY")
        elif "groq" in api_base_url:
            self.client.api_key = os.environ.get("GROQ_API_KEY")
        elif "googleapis" in api_base_url:
            self.client.api_key = os.environ.get("GEMINI_API_KEY")
        self.log = []

    async def act(self):
        prompt = self.env.get_prompt_history()
        response = await get_completion(
            self.client,
            self.model,
            prompt,
            self.generate_kwargs,
            max_tokens=8192,
        )
        content = response.choices[0].message.content
        if "</think>" in content:  # remove think content
            content = content.split("</think>")[1].strip()
        return content

    async def play_game(self, verbose: bool = False):
        obs = {"inventory": self.env.env.inventory, "new_item": None}
        terminated = False
        i = 0
        while not terminated:
            action = await self.act()
            if verbose:
                print(f"State: {self.env.format_obs(obs)}")
                print(f"Action: {action}")
            self.log.append(
                {
                    "timestep": i,
                    "round_num": self.round_num,
                    "state": self.env.env.inventory,
                    "action": action,
                    "score": self.env.get_reward(),
                }
            )
            obs, reward, terminated, info = self.env.step(action)
            i += 1

    async def play_games(
        self,
        num_rounds: int,
        incoming_message: str | None = None,
        verbose: bool = False,
    ):
        self.env.clear_history()
        self.round_num = 0
        self.log = []
        for round_num in range(num_rounds):
            self.env.reset()
            if round_num == 0 and incoming_message:
                self.env.add_message_to_history(incoming_message)
            await self.play_game(verbose=verbose)
            self.round_num += 1

        # write a message after the last round
        message = await self.write_message()
        return message, pd.DataFrame(self.log)

    async def write_message(self):
        prompt_history = self.env.get_prompt_history()
        prompt_history.append({"role": "user", "content": MESSAGE_PROMPT})

        try:
            response = await get_completion(
                self.client, self.model, prompt_history, self.generate_kwargs
            )
            raw_message = response.choices[0].message.content
            if raw_message is None:
                message = ""
            else:
                message_json = json.loads(raw_message)
                message = message_json["message"]
        except Exception as e:
            print(f"Error generating message: {e}")
            message = ""

        self.log.append(
            {
                "round_num": self.round_num,
                "message": message,
            }
        )
        return message
