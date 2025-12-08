"""
Oracle BFS Agent for the Open-Ended Crafting Game.

This agent performs a brute-force breadth-first search over action sequences
using perfect knowledge of the environment's world model to plan crafting
actions. It mirrors the public interface of the MCTS agent.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Callable, Dict, List, Optional, Tuple

from tqdm import tqdm

from oecraft.constants import Item, Tool
from oecraft.environment import CraftingGame

Inventory = Tuple[Item, ...]


def compute_reward_from_inventory(inventory: Inventory) -> int:
    """
    Mirror CraftingGame.get_reward but for an arbitrary inventory snapshot.
    Reward is the max value among non-tools, floored at 0.
    """
    ingredients = [item for item in inventory if not isinstance(item, Tool)]
    if not ingredients:
        return 0
    reward = max(item.value for item in ingredients)
    return max(reward, 0)


def legal_actions_from_inventory(
    inventory: Inventory,
) -> List[Optional[Tuple[int, int]]]:
    """
    Return indices (i, j) of legal actions from the given inventory.

    Includes None to represent the terminal action (stop now).
    """
    actions: List[Optional[Tuple[int, int]]] = [None]
    n = len(inventory)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = inventory[i], inventory[j]
            if isinstance(a, Tool) and isinstance(b, Tool):
                continue
            actions.append((i, j))
    return actions


def apply_action_to_inventory(
    inventory: Inventory,
    action: Optional[tuple[int, int]],
    combine_fn: Callable[[Item, Item], Item],
) -> Inventory:
    """
    Apply the environment's combination dynamics to a copy of the inventory.
    Replicates CraftingGame.step consumption rules:
    - If both are tools: no-op (but we never call this because we filter those actions)
    - Non-tools are consumed; tools remain
    - The resulting new item is appended
    """
    next_inventory: List[Item] = list(inventory)

    if action is None:
        return tuple(next_inventory)

    i, j = action
    if i > j:
        i, j = j, i

    item1 = next_inventory[i]
    item2 = next_inventory[j]

    if not isinstance(item2, Tool):
        del next_inventory[j]
    if not isinstance(item1, Tool):
        del next_inventory[i]

    new_item = combine_fn(item1, item2)
    next_inventory.append(new_item)

    return tuple(next_inventory)


def item_feature_signature(item: Item):
    """
    Hashable, canonical representation of an item that ignores name/emoji/value
    and keeps only semantics-relevant structure and features.
    - Tool: identified by its name
    - Ingredient: sorted feature items
    - CombinedItem: (combined_features, sorted(ingredient_signatures))
    """
    if isinstance(item, Tool):
        return ("T", item.name)

    # Avoid importing dataclass classes directly to keep coupling low
    # Detect CombinedItem by attribute presence
    if hasattr(item, "ingredients"):

        def _norm(v):
            if v is None:
                return "<NONE>"
            if isinstance(v, (int, float, bool, str)):
                return v
            return str(v)

        combined_features = tuple(
            sorted((k, _norm(v)) for k, v in getattr(item, "features", {}).items())
        )
        ingredient_sigs = tuple(
            sorted(
                item_feature_signature(ing) for ing in getattr(item, "ingredients", [])
            )
        )
        return ("C", combined_features, ingredient_sigs)

    # Base non-tool (Ingredient)
    def _norm(v):
        if v is None:
            return "<NONE>"
        if isinstance(v, (int, float, bool, str)):
            return v
        return str(v)

    features = tuple(
        sorted((k, _norm(v)) for k, v in getattr(item, "features", {}).items())
    )
    return ("N", features)


def inventory_signature(inventory: Inventory):
    return tuple(sorted(item_feature_signature(x) for x in inventory))


class OracleBFSAgent:
    def __init__(
        self,
        env: CraftingGame,
        max_depth: int = 8,
    ) -> None:
        self.env = env
        self.max_depth = max_depth
        self._combine_fn = self.env.world_model.combine

    def plan_action(self, inventory: Inventory) -> Optional[Tuple[int, int]]:
        """
        Run BFS from the given inventory and return the action (index pair) from
        the root that leads to the best terminal reward within max_depth.
        Returns None if the best choice is to stop immediately or no actions.
        """
        root_inventory = tuple(inventory)
        legal = legal_actions_from_inventory(root_inventory)
        if not legal:
            return None

        # Track best result per first action: (reward, -terminal_depth)
        best_by_first: Dict[Optional[Tuple[int, int]], Tuple[int, int]] = {}

        # Initialize per-first-action visited sets to avoid cycles while being fair
        visited_by_first: Dict[Optional[Tuple[int, int]], set[tuple]] = {}

        queue: deque[Tuple[Inventory, int, Optional[Tuple[int, int]]]] = deque()

        # Deduplicate root expansions that lead to identical next states
        seen_root_next: set[tuple] = set()
        for action in legal:
            if action is None:
                # Evaluate stopping immediately
                reward_now = compute_reward_from_inventory(root_inventory)
                best_by_first[None] = max(
                    best_by_first.get(None, (float("-inf"), 0)),
                    (reward_now, 0),
                )
                continue

            next_inv = apply_action_to_inventory(
                root_inventory, action, self._combine_fn
            )
            sig = inventory_signature(next_inv)
            if sig in seen_root_next:
                continue
            seen_root_next.add(sig)
            queue.append((next_inv, 1, action))
            visited_by_first.setdefault(action, set()).add(sig)

        while queue:
            current_inventory, depth, first_action = queue.popleft()

            # Evaluate current state as a potential stopping point
            reward_here = compute_reward_from_inventory(current_inventory)
            best_by_first[first_action] = max(
                best_by_first.get(first_action, (float("-inf"), 0)),
                (reward_here, -depth),
            )

            if depth >= self.max_depth:
                continue

            # Deduplicate child expansions by resulting state signature
            seen_child_next: set[tuple] = set()
            for action in legal_actions_from_inventory(current_inventory):
                if action is None:
                    # Stopping at this depth
                    best_by_first[first_action] = max(
                        best_by_first.get(first_action, (float("-inf"), 0)),
                        (reward_here, -depth),
                    )
                    continue

                next_inv = apply_action_to_inventory(
                    current_inventory, action, self._combine_fn
                )
                visited = visited_by_first.setdefault(first_action, set())
                sig = inventory_signature(next_inv)
                if sig in visited or sig in seen_child_next:
                    continue
                seen_child_next.add(sig)
                visited.add(sig)
                queue.append((next_inv, depth + 1, first_action))

        if not best_by_first:
            return None

        # Choose the first action with highest reward, breaking ties toward shallower depth
        # Note: None indicates stopping immediately
        best_action = max(best_by_first.items(), key=lambda kv: (kv[1][0], kv[1][1]))[0]
        return best_action


def run_oracle_bfs_agent(
    domain: str,
    n_runs: int = 10,
    n_steps: int = 10,
) -> Any:
    """
    Run the Oracle BFS agent for multiple episodes and return results.
    Matches the logging format used by the random and MCTS agents for analysis.
    """
    import pandas as pd  # Local import to avoid hard dependency at module import

    logs = []
    env = CraftingGame("none", domain=domain, assign_names=False)
    agent = OracleBFSAgent(env, max_depth=n_steps)

    for run_idx in tqdm(range(n_runs)):
        env.reset()
        inventory = env.inventory
        run_log = []

        for step in range(n_steps):
            action = agent.plan_action(inventory)

            if isinstance(action, tuple):
                i, j = action
                item1, item2 = inventory[i], inventory[j]
                action = (item1.name, item2.name)

            obs, score, done, info = env.step(action)
            new_item = obs["new_item"]
            inventory = obs["inventory"]

            # Compute mean ingredient value like baseline analysis expects
            ingredients = [item for item in inventory if not isinstance(item, Tool)]
            score = max([item.value for item in ingredients])

            step_log = {
                "run_idx": run_idx,
                "step": step,
                "action": action,
                "new_item": (new_item.name, new_item.value) if new_item else None,
                "score": score,
                "inventory_size": len(inventory),
                "ingredients": [
                    (item.name, item.value)
                    for item in inventory
                    if not isinstance(item, Tool)
                ],
            }
            run_log.append(step_log)

            if done:
                break

        final_reward = env.get_reward()
        print(f"final_reward: {final_reward}")
        for step_log in run_log:
            step_log["final_reward"] = final_reward
            logs.append(step_log)

    return pd.DataFrame(logs)
