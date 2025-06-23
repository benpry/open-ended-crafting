import random

import pandas as pd
from tqdm import tqdm

from src.environment import CraftingGame


def run_random_agent(domain: str, n_runs: int = 10, n_steps: int = 10) -> pd.DataFrame:
    """
    Run the random agent for multiple episodes and return results.

    Args:
        domain: Crafting domain ('cooking', 'decorations', 'genetics', 'potions')
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
            item1, item2 = random.sample(inventory, 2)
            obs, score, done, info = env.step((item1["name"], item2["name"]))
            new_item = obs["new_item"]
            inventory = obs["inventory"]
            score = sum([item["value"] for item in inventory]) / (len(inventory) - 4)

            step_log = {
                "run_idx": run_idx,
                "step": step,
                "action": (item1["name"], item2["name"]),
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
