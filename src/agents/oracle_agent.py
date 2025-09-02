"""
Oracle MCTS Agent for the Open-Ended Crafting Game.

This agent uses Monte Carlo Tree Search with perfect knowledge of
the combination and value functions (via the environment's world model)
to plan crafting actions.
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

from tqdm import tqdm

from src.constants import Item, Tool
from src.environment import CraftingGame

Inventory = List[Item]
Action = Tuple[str, str]


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


def legal_actions_from_inventory(inventory: Inventory) -> List[Tuple[int, int]]:
    """
    Return indices (i, j) of legal actions from the given inventory.
    Legal actions exclude tool-tool pairs. Order is irrelevant; we enforce i < j.
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
    # Copy first to avoid mutating caller's state
    next_inventory: Inventory = list(inventory)

    if action is None:
        return next_inventory

    i, j = action

    # Ensure i < j for stable indexing removal
    if i > j:
        i, j = j, i

    item1 = next_inventory[i]
    item2 = next_inventory[j]

    # Remove non-tools (higher index first to preserve indices)
    if not isinstance(item2, Tool):
        del next_inventory[j]
    if not isinstance(item1, Tool):
        del next_inventory[i]

    # Combine
    new_item = combine_fn(item1, item2)
    next_inventory.append(new_item)

    return next_inventory


class MCTSNode:
    def __init__(
        self,
        inventory: Inventory,
        parent: Optional[MCTSNode] = None,
        incoming_action: Optional[Tuple[int, int]] = None,
        is_end_state: bool = False,
    ) -> None:
        self.inventory: Inventory = inventory
        self.is_end_state: bool = is_end_state
        self.parent: Optional[MCTSNode] = parent
        self.incoming_action: Optional[Tuple[int, int]] = incoming_action
        self.children: Dict[Tuple[int, int], MCTSNode] = {}
        self.visits: int = 0
        self.total_value: float = 0.0
        self._unexpanded_actions: Optional[List[Tuple[int, int]]] = None

    @property
    def q_value(self) -> float:
        if self.visits == 0:
            return 0.0
        return self.total_value / self.visits

    def is_fully_expanded(self, legal_actions: List[Tuple[int, int]]) -> bool:
        return len(self.children) >= len(legal_actions)

    def select_child_ucb(self, c: float) -> Tuple[Tuple[int, int], "MCTSNode"]:
        assert self.children, "No children to select from"
        log_parent = math.log(self.visits + 1.0)
        best_score = -float("inf")
        best_pair: Tuple[Tuple[int, int], MCTSNode] | None = None
        for action, child in self.children.items():
            exploration = c * math.sqrt(log_parent / (child.visits + 1e-9))
            score = child.q_value + exploration
            if score > best_score:
                best_score = score
                best_pair = (action, child)
        assert best_pair is not None
        return best_pair


class OracleMCTSAgent:
    def __init__(
        self,
        env: CraftingGame,
        simulations_per_move: int = 200,
        max_depth: int = 8,
        exploration_c: float = 1.25,
        discount_factor: float = 0.98,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.env = env
        self.simulations_per_move = simulations_per_move
        self.max_depth = max_depth
        self.exploration_c = exploration_c
        self.discount_factor = discount_factor
        self.rng = rng or random.Random()

        # Use the environment's world model for perfect knowledge
        self._combine_fn = self.env.world_model.combine

    def plan_action(self, inventory: Inventory) -> Optional[Tuple[int, int]]:
        """
        Run MCTS from the given inventory and return the best action as index pair.
        Returns None if no legal actions are available (i.e., only tool-tool pairs).
        """
        legal = legal_actions_from_inventory(inventory)
        if not legal:
            return None

        root = MCTSNode(inventory=list(inventory))

        for _ in range(self.simulations_per_move):
            node = root
            depth = 0

            # SELECTION & EXPANSION
            while True:
                legal_here = legal_actions_from_inventory(node.inventory)
                # Expand if there's an untried action
                untried = [a for a in legal_here if a not in node.children]
                if untried:
                    action = self.rng.choice(untried)
                    next_inv = apply_action_to_inventory(
                        node.inventory, action, self._combine_fn
                    )
                    child = MCTSNode(
                        next_inv,
                        parent=node,
                        incoming_action=action,
                        is_end_state=action is None,
                    )
                    node.children[action] = child
                    node = child
                    depth += 1
                    break
                if node.children:
                    action, node = node.select_child_ucb(self.exploration_c)
                    depth += 1
                    if depth >= self.max_depth:
                        break
                else:
                    # No legal actions
                    break

            # SIMULATION
            if node.is_end_state:
                rollout_value = compute_reward_from_inventory(node.inventory)
            else:
                rollout_value = self._rollout(
                    node.inventory, remaining_depth=self.max_depth - depth
                )

            # BACKPROPAGATION
            self._backpropagate(node, rollout_value)

        # Choose the action leading to the highest mean value
        if not root.children:
            return None
        best_action = max(root.children.items(), key=lambda kv: kv[1].q_value)[0]
        return best_action

    def _rollout(self, inventory: Inventory, remaining_depth: int) -> float:
        if remaining_depth <= 0:
            return float(compute_reward_from_inventory(inventory))

        current_inventory = list(inventory)
        depth = 0
        inventory_values = [compute_reward_from_inventory(current_inventory)]
        while depth < remaining_depth:
            legal = legal_actions_from_inventory(current_inventory)
            if not legal:
                break

            action = self.rng.choice(legal)

            current_inventory = apply_action_to_inventory(
                current_inventory, action, self._combine_fn
            )
            inventory_values.append(
                compute_reward_from_inventory(current_inventory)
                * self.discount_factor ** (depth + 1)
            )
            depth += 1

        return max(inventory_values)

    def _backpropagate(self, node: MCTSNode, value: float) -> None:
        cursor: Optional[MCTSNode] = node
        total_discount = 1.0
        while cursor is not None:
            cursor.visits += 1
            cursor.total_value += value * total_discount
            cursor = cursor.parent
            total_discount *= self.discount_factor


def run_oracle_mcts_agent(
    domain: str,
    n_runs: int = 10,
    n_steps: int = 10,
    simulations_per_move: int = 200,
    max_depth: int = 8,
    exploration_c: float = 1.25,
    discount_factor: float = 0.98,
) -> Any:
    """
    Run the Oracle MCTS agent for multiple episodes and return results.
    Matches the logging format used by the random agent for downstream analysis.
    """
    import pandas as pd  # Local import to avoid hard dependency at module import

    log = []
    env = CraftingGame("none", domain=domain, assign_names=False)
    agent = OracleMCTSAgent(
        env,
        simulations_per_move=simulations_per_move,
        max_depth=max_depth,
        exploration_c=exploration_c,
        discount_factor=discount_factor,
    )

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

            # For compatibility with baseline, compute mean ingredient value
            ingredients = [item for item in inventory if not isinstance(item, Tool)]
            score = max([item.value for item in ingredients])

            step_log = {
                "run_idx": run_idx,
                "step": step,
                "action": action,
                "new_item": new_item,
                "score": score,
                "inventory_size": len(inventory),
                "inventory": inventory,
            }
            run_log.append(step_log)

            if done:
                break

        # Final reward for this run
        final_reward = env.get_reward()
        for step_log in run_log:
            step_log["final_reward"] = final_reward
            log.append(step_log)

    return pd.DataFrame(log)
