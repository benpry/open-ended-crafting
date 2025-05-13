"""
A fastapi server that runs the cooking game.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.environment import CraftingGame
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games = {}


class InitRequest(BaseModel):
    model: Optional[str] = Field(
        "gemini/gemini-2.0-flash", description="The model to use for the game"
    )


@app.get("/init")
def initialize(request: Optional[InitRequest] = None):
    """
    Get an initial inventory
    """
    # model = request.model if request else "gemini/gemini-2.0-flash"
    # model = request.model if request else "gemini/gemini-2.0-flash"
    # model = (
    #     request.model
    #     if request
    #     else "fireworks_ai/accounts/fireworks/models/qwen3-235b-a22b"
    # )
    # model = request.model if request else "gemini/gemini-2.5-flash-preview-04-17"
    # model = request.model if request else "openai/gpt-4o"
    model = (
        request.model
        if request
        else "fireworks_ai/accounts/fireworks/models/llama4-maverick-instruct-basic"
    )
    world_type = "craft_making"
    game = CraftingGame(model, world_type)
    game.reset()
    game_id = world_type
    games[game_id] = game
    return {
        "game_id": game_id,
        "inventory": game.inventory,
    }


class StepRequest(BaseModel):
    game_id: str
    action: tuple[str, str]


@app.post("/step")
def step(request: StepRequest):
    """
    Take an action in the game.
    """
    game = games[request.game_id]
    print(f"inventory: {game.inventory}")
    obs, _, _, _ = game.step(request.action)
    print(f"obs: {obs}")
    return obs
