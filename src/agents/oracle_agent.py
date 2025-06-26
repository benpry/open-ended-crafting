"""
Oracle Agent for the Open-Ended Crafting Game.

This agent has perfect knowledge of the combination functions and uses BFS
to find optimal crafting strategies with efficient state representation.
"""

from collections import deque
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

import pandas as pd
from tqdm import tqdm

from src.combo_functions import COMBO_FUNCTIONS, VALUE_FUNCTIONS
from src.environment import CraftingGame
from src.world_model import MemoizedWorldModel


def _extract_essential_features(item: Dict[str, Any]) -> FrozenSet[Tuple[str, Any]]:
    """
    Extract only the essential features from an item that matter for
    combinations and value computation. Names, emojis, and other metadata are ignored.
    """
    essential_keys = {
        # Core identification
        "tool",
        "edible",
        "value",
        # Cooking domain features
        "water_level",
        "chop_level",
        "salt_level",
        "cook_level",
        "ingredient_types",
        "all_ingredients",
        # Decorations domain features
        "paint_level",
        "cut_level",
        "drawn_level",
        "material_types",
        "hardness",
        "framed",
        "post_frame_messed_with",
        # Animals domain features
        "habitat",
        "diet",
        "size",
        "domesticated",
        "aggressive",
        "age",
        "animal_types",
        # Potions domain features
        "color",
        "consistency",
        "temperature",
        "magical",
        "ingredients",
        "effect",
    }

    features = []
    for key, value in item.items():
        if key in essential_keys:
            if isinstance(value, list):
                # Convert lists to tuples for hashability
                features.append((key, tuple(value)))
            else:
                features.append((key, value))

    return frozenset(features)


def _features_to_item(features: FrozenSet[Tuple[str, Any]]) -> Dict[str, Any]:
    """Convert feature set back to item dictionary for use with world model."""
    item = {}
    for key, value in features:
        if isinstance(value, tuple) and key in [
            "ingredient_types",
            "all_ingredients",
            "material_types",
            "animal_types",
        ]:
            # Convert tuples back to lists for these specific fields
            item[key] = list(value)
        else:
            item[key] = value

    # Ensure name field exists for world model compatibility
    if "name" not in item:
        # Generate a deterministic name based on features for consistency
        item["name"] = f"item_{hash(features) % 100000}"

    # Ensure emoji field exists
    if "emoji" not in item:
        item["emoji"] = "❓"

    return item


class OracleAgent:
    """
    An oracle agent that knows the true combination functions and uses BFS
    to find optimal solutions with efficient state representation.
    """

    def __init__(
        self, domain: str, max_depth: int = 5, world_model: MemoizedWorldModel = None
    ):
        """
        Initialize the oracle agent.

        Args:
            domain: The crafting domain ('cooking', 'decorations', 'animals', 'potions')
            max_depth: Maximum depth for BFS search
            world_model: The world model to use for combinations
        """
        self.domain = domain
        self.max_depth = max_depth
        self.combo_function = COMBO_FUNCTIONS[domain]
        self.value_function = VALUE_FUNCTIONS[domain]
        self.world_model = world_model

        # Cache for combination results using feature representations
        self._combination_cache: Dict[
            Tuple[FrozenSet, FrozenSet], Optional[FrozenSet]
        ] = {}

    def _compute_reward(self, consumable_items: FrozenSet[FrozenSet]) -> float:
        """
        Compute the value of a given set of consumable items.
        Tools are stored separately and don't contribute to value.
        """
        if not consumable_items:
            return 0.0

        total_value = 0.0
        for item_features in consumable_items:
            # Convert features back to item dict for value computation
            item_dict = _features_to_item(item_features)
            value = self.value_function(item_dict)
            total_value += value

        return max(total_value / len(consumable_items), 0.0)

    def _prepare_initial_state(
        self, initial_inventory: List[Dict[str, Any]]
    ) -> Tuple[FrozenSet[FrozenSet], FrozenSet[FrozenSet]]:
        """
        Convert initial inventory to efficient representation.
        Returns (consumable_items, tools).
        """
        consumable_items = set()
        tools = set()

        for item in initial_inventory:
            features = _extract_essential_features(item)
            if item.get("tool", False):
                tools.add(features)
            else:
                consumable_items.add(features)

        return frozenset(consumable_items), frozenset(tools)

    def find_optimal_sequence(
        self,
        initial_inventory: List[Dict[str, Any]],
        max_states: int = None,  # Limit to prevent memory explosion
    ) -> Tuple[List[Tuple[str, str]], float]:
        """
        Use BFS to find the optimal sequence of combinations.
        Returns:
            Tuple of (action_sequence, best_reward)
        """
        # We'll do a simpler approach: use the efficient state representation for
        # visited state tracking, but maintain the actual inventory for action naming

        # Initialize BFS queue with (inventory, action_sequence, depth)
        queue = deque([(initial_inventory, [], 0)])
        visited: Set[FrozenSet[FrozenSet]] = set()

        best_reward = self._compute_reward_from_inventory(initial_inventory)
        best_sequence = []
        states_explored = 0

        while queue and (max_states is None or states_explored < max_states):
            current_inventory, action_sequence, depth = queue.popleft()
            states_explored += 1
            # Create efficient state representation for visited check
            consumable_items, tools = self._prepare_initial_state(current_inventory)
            state_key = consumable_items  # Tools don't change, so just use consumables

            # Check if we've seen this state before
            if state_key in visited:
                continue
            visited.add(state_key)

            # Compute reward for current state
            current_reward = self._compute_reward_from_inventory(current_inventory)
            if current_reward > best_reward:
                best_reward = current_reward
                best_sequence = action_sequence.copy()

            # Stop if we've reached max depth
            if depth >= self.max_depth:
                continue

            # Generate all possible combinations from current inventory
            possible_actions = self._get_possible_actions(current_inventory)

            for action in possible_actions:
                new_inventory = self._apply_action_to_inventory(
                    current_inventory, action
                )
                if new_inventory is None:
                    continue

                # Check if this new state has been visited
                new_consumable, _ = self._prepare_initial_state(new_inventory)
                if new_consumable not in visited:
                    new_action_sequence = action_sequence + [action]
                    queue.append((new_inventory, new_action_sequence, depth + 1))

        # add a None action for submitting
        best_sequence.append(None)

        return best_sequence, best_reward

    def _compute_reward_from_inventory(self, inventory: List[Dict[str, Any]]) -> float:
        """Compute reward from actual inventory (for compatibility)."""
        ingredients = [item for item in inventory if not item.get("tool", False)]
        if not ingredients:
            return 0.0

        total_value = 0.0
        for item in ingredients:
            value = self.value_function(item)
            total_value += value

        return max(total_value / len(ingredients), 0.0)

    def _get_possible_actions(
        self, inventory: List[Dict[str, Any]]
    ) -> List[Tuple[str, str]]:
        """Get possible actions from actual inventory."""
        actions = []
        item_names = [item["name"] for item in inventory]

        # Get unique combinations to avoid duplicates
        for i, name1 in enumerate(item_names[:-1]):
            for j, name2 in enumerate(item_names[i + 1 :]):
                # Skip if both items are tools
                item1 = inventory[i]
                item2 = inventory[i + 1 + j]
                if item1["tool"] and item2["tool"]:
                    continue

                actions.append((name1, name2))

        return actions

    def _apply_action_to_inventory(
        self, inventory: List[Dict[str, Any]], action: Tuple[str, str]
    ) -> Optional[List[Dict[str, Any]]]:
        """Apply action to actual inventory."""
        item1_name, item2_name = action

        # Find items
        item1 = None
        item2 = None
        for item in inventory:
            if item["name"] == item1_name:
                item1 = item
            elif item["name"] == item2_name:
                item2 = item
            if item1 is not None and item2 is not None:
                break

        if item1 is None or item2 is None:
            return None

        # Get the combination result
        new_item = self.world_model.combine(item1, item2)
        if new_item is None:
            return None

        # Create new inventory
        new_inventory = []
        for item in inventory:
            if item["name"] == item1_name or item["name"] == item2_name:
                # Check if this item should be preserved (tools are durable)
                if item.get("tool", False):
                    new_inventory.append(item.copy())
                # Skip consumed items (non-tools)
            else:
                new_inventory.append(item.copy())

        # Add the new item
        new_inventory.append(new_item.copy())

        return new_inventory


def run_oracle_agent(
    domain: str,
    n_runs: int = 10,
    max_depth: int = 3,
) -> pd.DataFrame:
    """
    Run the oracle agent for multiple episodes and return results.

    Args:
        domain: Crafting domain ('cooking', 'decorations', 'animals', 'potions')
        n_runs: Number of episodes to run
        n_steps: Maximum steps per episode
        max_depth: Maximum search depth for BFS
        beam_width: Beam width for beam search

    Returns:
        DataFrame with step-by-step episode results
    """
    log = []
    env = CraftingGame("none", domain=domain, assign_names=False)
    oracle = OracleAgent(domain, max_depth=max_depth, world_model=env.world_model)

    for run_idx in tqdm(range(n_runs), desc=f"Running oracle agent on {domain}"):
        env.reset()
        inventory = env.inventory
        run_log = []  # Store logs for this run

        optimal_sequence, _ = oracle.find_optimal_sequence(inventory)

        for i, action in enumerate(optimal_sequence):
            if action is None:
                # No beneficial action found, stop this episode
                break

            # Execute the action
            obs, score, done, info = env.step(action)
            new_item = obs["new_item"]
            inventory = obs["inventory"]

            # Calculate current score
            ingredients = [item for item in inventory if not item.get("tool", False)]
            if ingredients:
                score = sum(item.get("value", 0) for item in ingredients) / len(
                    ingredients
                )
            else:
                score = 0.0

            step_log = {
                "run_idx": run_idx,
                "step": i,
                "action": action,
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


if __name__ == "__main__":
    # Test the oracle agent on all domains
    domains = ["cooking", "decorations", "animals", "potions"]

    for domain in domains:
        print(f"\nTesting Oracle Agent on {domain} domain:")
        results = run_oracle_agent(domain, n_runs=5, max_depth=10)

        print("mean final reward: ", results["final_reward"].mean())

        # print an example optimal action sequence
        example_actions = results[results["run_idx"] == 0]["action"]
        print(example_actions)
