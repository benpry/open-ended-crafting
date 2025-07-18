import random

from pyprojroot import here

from src.environment import CraftingGame

# model = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
# model = "fireworks_ai/accounts/fireworks/models/llama4-maverick-instruct-basic"
# model = "gemini/gemini-2.5-flash-preview-04-17"
model = "meta-llama/llama-4-maverick-17b-128e-instruct"
# model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
# model = "Qwen/Qwen3-235B-A22B-fp8-tput"
# model = "groq/llama-4-scout"
# model = "openai/gpt-4.1-mini"
# model = "anthropic/claude-3-7-sonnet-20250219"

DOMAIN = "animals"
game = CraftingGame(model, DOMAIN, assign_names=True)
game.reset()


def get_action(inv):
    item1, item2 = random.sample(inv, 2)
    return item1["name"], item2["name"]


rewards = []
for run in range(3):
    game.reset()
    for i in range(10):
        print(f"Step {i}")
        game.render()
        action = get_action(game.inventory)
        game.step(action)

    print(f"Game {run} finished")
    reward = game.get_reward()
    print(f"Reward: {reward}")
    rewards.append(reward)

print(f"Rewards: {rewards}")

print(f"Average reward: {sum(rewards) / len(rewards)}")
short_model_name = model.split("/")[-1].replace(".", "-")
game.world_model.save(
    str(here(f"data/world-models/{DOMAIN}_{short_model_name}_random.json"))
)
