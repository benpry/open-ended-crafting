"""
Basic implementation for a language model agent that plays the crafting game.
"""

import json
import os
from typing import Optional

import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from oecraft.environment import SYSTEM_PROMPT as GAME_SYSTEM_PROMPT
from oecraft.environment import LMCraftingGame

MESSAGE_PROMPT = """You have finished playing the crafting game. Now, please write a message to help a future player play the same game. The message can contain anything you want and should help the next player succeed.
Please respond in JSON and follow this format:
```json
{
    "message": "a message that will be passed to the next player"
}
```
"""


class ActionResponse(BaseModel):
    reasoning: str = Field(
        description="A one or two sentence explanation of why you chose this action"
    )
    action: list[str] | str = Field(
        description="A list of the names of two items in the inventory or the string 'submit'"
    )


class MessageResponse(BaseModel):
    message: str = Field(description="A message that will be passed to the next player")


@retry(stop=stop_after_attempt(15), wait=wait_exponential())
async def get_completion(
    client: genai.Client,
    model: str,
    messages: list[dict],
    generate_kwargs: dict,
    response_schema: Optional[BaseModel] = None,
    max_tokens: int = 2048,
):
    response = await client.aio.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=GAME_SYSTEM_PROMPT,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_schema=response_schema,
            **generate_kwargs,
        ),
    )

    return response


class CraftingAgent:
    """
    A basic implementation for a language model agent that plays the crafting game.
    """

    def __init__(
        self,
        env: LMCraftingGame,
        model: str,
        generate_kwargs: dict,
        verbose: bool = False,
    ):
        self.env = env
        self.model = model
        self.generate_kwargs = generate_kwargs or {}
        api_key = os.environ.get("COCOLAB_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("COCOLAB_GEMINI_API_KEY must be set.")
        self.client = genai.Client(api_key=api_key)
        self.log = []
        self.verbose = verbose

    async def _generate_text(
        self,
        messages: list[dict],
        response_schema: Optional[BaseModel] = None,
        max_tokens: int = 2048,
    ) -> str:
        response = await get_completion(
            self.client,
            self.model,
            messages,
            self.generate_kwargs,
            response_schema,
            max_tokens=max_tokens,
        )
        content = response.text
        if "</think>" in content:  # remove think content
            content = content.split("</think>")[1].strip()
        return content

    async def act(self):
        prompt = self.env.get_prompt_history()
        return await self._generate_text(
            prompt, response_schema=ActionResponse, max_tokens=8192
        )

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
        prompt_history.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=MESSAGE_PROMPT)]
            )
        )

        try:
            raw_message = await self._generate_text(
                prompt_history, response_schema=MessageResponse
            )
            message_json = json.loads(raw_message) if raw_message else {}
            message = message_json.get("message", "")
        except Exception as e:
            if self.verbose:
                print(f"Error with message: {e}")
            message = f"Error in generating message: {e}"

        self.log.append(
            {
                "round_num": self.round_num,
                "message": message,
            }
        )
        return message
