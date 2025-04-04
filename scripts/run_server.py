"""
A fastapi server that runs the cooking game.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.environment import CookingGame
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
    model = request.model if request else "gemini/gemini-2.0-flash"
    # model = request.model if request else "anthropic/claude-3-7-sonnet-20250219"
    game = CookingGame(model)
    game.reset()
    game_id = str(uuid4())
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
