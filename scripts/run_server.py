"""
A fastapi server that runs the cooking game.
"""

from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from oecraft.environment import CraftingGame

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
        "gemini/gemini-2.5-flash-preview-04-17",
        description="The model to use for the game",
    )


@app.get("/init")
def initialize(request: Optional[InitRequest] = None):
    """
    Get an initial inventory
    """
    # model = request.model if request else "gemini/gemini-2.5-flash-preview-04-17"
    model = "openai/gpt-4.1-mini"

    world_type = "potions"
    game = CraftingGame(model, world_type)
    game.reset()
    game_id = world_type
    if game_id not in games:
        games[game_id] = game
    else:
        game = games[game_id]
        game.reset()
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
