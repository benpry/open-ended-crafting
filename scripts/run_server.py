"""
A fastapi server that runs the cooking game.
"""

from fastapi import FastAPI
from src.environment import CookingGame
from pydantic import BaseModel

app = FastAPI()


@app.get("/initialize")
def initialize():
    """
    Get an initial inventory
    """
    game = CookingGame()
    game.reset()
    return game.inventory


class StepRequest(BaseModel):
    inventory: list
    action: dict


@app.get("/step")
def step(request: StepRequest):
    """
    Take an action in the game.
    """
    game = CookingGame()
    game.inventory = request.inventory
    game.step(request.action)
    return game.inventory
