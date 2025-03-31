"""
A fastapi server that runs the cooking game.
"""

from fastapi import FastAPI
from src.environment import CookingGame
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI()

games = {}


class InitRequest(BaseModel):
    model: str


@app.get("/init")
def initialize(request: InitRequest):
    """
    Get an initial inventory
    """
    game = CookingGame(model=request.model)
    game.reset()
    game_id = str(uuid4())
    games[game_id] = game
    return {
        "id": game_id,
        "inventory": game.inventory,
    }


class StepRequest(BaseModel):
    action: tuple[str, str]


@app.get("/{game_id}/step")
def step(game_id: str, request: StepRequest):
    """
    Take an action in the game.
    """
    game = games[game_id]
    game.step(request.action)
    return game.inventory
