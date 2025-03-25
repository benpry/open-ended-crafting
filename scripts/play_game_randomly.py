from src.environment import CookingGame
import random

model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
# model = "openai/gpt-4o"
# model = "anthropic/claude-3-7-sonnet-20250219"
game = CookingGame(model)
game.reset()


def get_action(inv):
    item1, item2 = random.sample(inv, 2)
    return item1, item2


for i in range(10):
    print(f"Step {i}")
    game.render()
    action = get_action(game.inventory)
    print(f"combining {action[0]['name']} and {action[1]['name']}")
    game.step(action)
