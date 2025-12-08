import random

import pandas as pd
from tqdm import tqdm

from src.constants import Tool
from src.environment import CraftingGame


def run_random_agent(domain: str, n_runs: int = 10, n_steps: int = 10) -> pd.DataFrame:
    """
    Run the random agent for multiple episodes and return results.

    Args:
        domain: Crafting domain ('cooking', 'decorations', 'animals', 'potions')
        n_runs: Number of episodes to run
        n_steps: Maximum steps per episode

    Returns:
        DataFrame with step-by-step episode results with harmonized format
    """
    log = []
    env = CraftingGame("none", domain=domain, assign_names=False)

    for run_idx in tqdm(range(n_runs)):
        env.reset()
        inventory = env.inventory
        run_log = []  # Store logs for this run to add final_reward later

        for step in range(n_steps):
            # choose two items. They can't both be tools
            item1, item2 = random.sample(inventory, 2)
            while isinstance(item1, Tool) and isinstance(item2, Tool):
                item1, item2 = random.sample(inventory, 2)

            obs, score, done, info = env.step((item1.name, item2.name))
            new_item = obs["new_item"]
            inventory = obs["inventory"]
            ingredients = [item for item in inventory if not isinstance(item, Tool)]
            score = sum([item.value for item in ingredients]) / len(ingredients)

            step_log = {
                "run_idx": run_idx,
                "step": step,
                "action": (item1.name, item2.name),
                "new_item": new_item,
                "score": score,
                "inventory_size": len(inventory),
                "inventory": inventory,
            }
            run_log.append(step_log)

            if done:
                break

        # Get final reward for this run
        final_reward = env.get_reward()

        # Add final_reward to all steps in this run
        for step_log in run_log:
            step_log["final_reward"] = final_reward
            log.append(step_log)

    return pd.DataFrame(log)
