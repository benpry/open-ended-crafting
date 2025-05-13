from src.environment import CraftingGame
import random

# model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
model = "gemini/gemini-2.0-flash"
# model = "openai/gpt-4o"
# model = "anthropic/claude-3-7-sonnet-20250219"
game = CraftingGame(model, "cooking")
game.reset()


def get_action(inv):
    item1, item2 = random.sample(inv, 2)
    return item1["name"], item2["name"]


for i in range(10):
    print(f"Step {i}")
    game.render()
    action = get_action(game.inventory)
    print(f"combining {action[0]} and {action[1]}")
    game.step(action)
