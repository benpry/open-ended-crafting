from src.environment import CookingGame
import random

# model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
model = "openai/gpt-4o"
game = CookingGame(model)
game.reset()


def get_action(inv):
    item1, item2 = random.sample(inv, 2)

    return {"item1": item1, "item2": item2}


for i in range(10):
    print(f"Step {i}")
    game.render()
    action = get_action(game.inventory)
    game.step(action)
