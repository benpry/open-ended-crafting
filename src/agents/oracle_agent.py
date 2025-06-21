"""
An oracle agent that has access to the ground-truth value and combination functions.
"""

import copy
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from tqdm import tqdm

from src.environment import CraftingGame


def get_possible_actions(
    inventory: List[Dict[str, Any]],
) -> List[Optional[Tuple[str, str]]]:
    """
    Get all possible actions (pairs of items) from the current inventory.

    Args:
        inventory: Current inventory items

    Returns:
        List of possible action tuples (item1_name, item2_name) or None for submit
    """
    actions = []
    for i, item1 in enumerate(inventory):
        for j, item2 in enumerate(inventory):
            if i < j:  # Avoid duplicate pairs and self-pairing
                actions.append((item1["name"], item2["name"]))

    # None action corresponds to pressing submit
    actions.append(None)
    return actions


class OracleAgent:
    """
    An oracle agent that uses ground-truth combination functions to plan optimal sequences.

    This agent has perfect knowledge of the combination functions and uses the CraftingGame
    environment to simulate actions and plan optimal sequences. It implements both exhaustive
    planning using breadth-first search and efficient beam search for large search spaces.

    The agent leverages the existing CraftingGame environment for simulation instead of
    reimplementing the game logic, making it more maintainable and consistent with the
    actual game mechanics. It provides optimal planning (BFS), beam search planning,
    and greedy planning methods for comparison.

    Attributes:
        domain: The crafting domain ('cooking', 'decorations', 'genetics', 'potions')
        max_depth: Maximum planning depth for action sequences
        beam_width: Width of the beam for beam search (number of best states to keep)
        planning_method: Method to use for planning ('beam_search', 'bfs', or 'greedy')
        _sim_env: Internal environment used for simulation
    """

    def __init__(
        self,
        domain: str,
        max_depth: int = 10,
        beam_width: int = 5,
        planning_method: str = "beam_search",
    ):
        """
        Initialize the oracle agent.

        Args:
            domain: The crafting domain ('cooking', 'decorations', 'genetics', 'potions')
            max_depth: Maximum search depth for planning sequences
            beam_width: Width of the beam for beam search (number of best states to keep)
            planning_method: Planning method to use ('beam_search', 'bfs', or 'greedy')
        """
        self.domain = domain
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.planning_method = planning_method
        # Create a simulation environment with ground-truth combination functions
        self._sim_env = CraftingGame("none", domain=domain, assign_names=False)

    def _simulate_action(
        self, inventory: List[Dict[str, Any]], action: Optional[Tuple[str, str]]
    ) -> Optional[Tuple[List[Dict[str, Any]], int]]:
        """
        Simulate an action on a given inventory state.

        Uses the CraftingGame environment to simulate the action and return the
        resulting inventory and value change.

        Args:
            inventory: Current inventory state
            action: Action tuple (item1_name, item2_name) or None for submit

        Returns:
            Tuple of (new_inventory, value_gain) or None if action is invalid
        """
        # Create a copy of the environment and set its inventory
        self._sim_env.inventory = [copy.deepcopy(item) for item in inventory]
        current_max_value = max(item["value"] for item in inventory) if inventory else 0

        try:
            # Simulate the action
            obs, reward, done, info = self._sim_env.step(action)
            new_inventory = obs["inventory"]
            new_max_value = (
                max(item["value"] for item in new_inventory) if new_inventory else 0
            )
            value_gain = new_max_value - current_max_value

            return new_inventory, value_gain
        except (ValueError, KeyError):
            # Action is invalid (e.g., items not in inventory)
            return None

    def _get_inventory_hash(self, inventory: List[Dict[str, Any]]) -> str:
        """
        Create a hash of the inventory state for deduplication.

        Args:
            inventory: Current inventory state

        Returns:
            String hash representing the inventory state
        """
        # Sort items by name and value to create consistent hash
        items = [(item["name"], item["value"]) for item in inventory]
        items.sort()
        return str(items)

    def plan_beam_search(
        self, inventory: List[Dict[str, Any]]
    ) -> Tuple[List[Tuple[str, str]], int]:
        """
        Plan using beam search to balance optimality and efficiency.

        Beam search keeps only the top beam_width states at each level, making it much
        more efficient than exhaustive BFS while still exploring promising paths.
        This is ideal for domains with large search spaces like decorations.

        Args:
            inventory: Current inventory

        Returns:
            Tuple of (best_action_sequence, final_max_value)
        """
        if not inventory:
            return [], 0

        # State: (inventory, action_sequence, current_max_value, heuristic_score)
        initial_max_value = max(item["value"] for item in inventory)

        # Initialize beam with starting state
        # Heuristic: use current max value as simple heuristic
        beam = [(inventory, [], initial_max_value, initial_max_value)]

        best_sequence = []
        best_final_value = initial_max_value

        for depth in range(self.max_depth):
            next_beam = []

            # Expand each state in current beam
            for current_inventory, action_sequence, current_max_value, _ in beam:
                possible_actions = get_possible_actions(current_inventory)

                for action in possible_actions:
                    if action is None:  # Submit action
                        continue

                    # Simulate the action
                    result = self._simulate_action(current_inventory, action)
                    if result is None:
                        continue

                    new_inventory, value_gain = result
                    new_max_value = current_max_value + value_gain

                    # Only keep states that improve value
                    if value_gain > 0:
                        new_sequence = action_sequence + [action]

                        # Simple heuristic: current max value + potential based on inventory size
                        inventory_diversity = len(
                            set(item["name"] for item in new_inventory)
                        )
                        heuristic_score = new_max_value + 0.1 * inventory_diversity

                        next_beam.append(
                            (
                                new_inventory,
                                new_sequence,
                                new_max_value,
                                heuristic_score,
                            )
                        )

                        # Update best if this is better
                        if new_max_value > best_final_value:
                            best_sequence = new_sequence
                            best_final_value = new_max_value

            # If no beneficial actions found, stop
            if not next_beam:
                break

            # Keep only top beam_width states based on heuristic score
            next_beam.sort(key=lambda x: x[3], reverse=True)  # Sort by heuristic score
            beam = next_beam[: self.beam_width]

        return best_sequence, best_final_value

    def plan_optimal_sequence(
        self, inventory: List[Dict[str, Any]]
    ) -> Tuple[List[Tuple[str, str]], int]:
        """
        Plan the optimal sequence of actions using breadth-first search.

        This method implements exhaustive planning by exploring all possible action sequences
        up to max_depth and finding the one that leads to the maximum final value.
        Uses BFS with state deduplication to handle the search space efficiently.

        Note: This can be very slow for domains with large search spaces. Consider using
        beam search for better performance.

        Args:
            inventory: Current inventory

        Returns:
            Tuple of (optimal_action_sequence, final_max_value)
        """
        if not inventory:
            return [], 0

        from collections import deque

        # State: (inventory, action_sequence, current_max_value)
        initial_max_value = max(item["value"] for item in inventory)
        queue = deque([(inventory, [], initial_max_value)])

        # Track visited states to avoid cycles
        visited = set()
        visited.add(self._get_inventory_hash(inventory))

        best_sequence = []
        best_final_value = initial_max_value

        while queue:
            current_inventory, action_sequence, current_max_value = queue.popleft()

            # Skip if we've reached max depth
            if len(action_sequence) >= self.max_depth:
                continue

            # Get possible actions from current state
            possible_actions = get_possible_actions(current_inventory)

            # Track if any beneficial action is found at this level
            found_beneficial_action = False

            for action in possible_actions:
                if action is None:  # Submit action
                    continue

                # Simulate the action
                result = self._simulate_action(current_inventory, action)
                if result is None:
                    continue

                new_inventory, value_gain = result
                new_max_value = current_max_value + value_gain

                # Only continue if this action provides some benefit
                if value_gain > 0:
                    found_beneficial_action = True

                    # Create new action sequence
                    new_sequence = action_sequence + [action]

                    # Check if this is better than our current best
                    if new_max_value > best_final_value:
                        best_sequence = new_sequence
                        best_final_value = new_max_value

                    # Add to queue for further exploration if not visited
                    inventory_hash = self._get_inventory_hash(new_inventory)
                    if inventory_hash not in visited:
                        visited.add(inventory_hash)
                        queue.append((new_inventory, new_sequence, new_max_value))

            # If no beneficial actions found at this level and we have a sequence,
            # this is a potential terminal state
            if not found_beneficial_action and action_sequence:
                if current_max_value > best_final_value:
                    best_sequence = action_sequence
                    best_final_value = current_max_value

        return best_sequence, best_final_value

    def plan_sequence(
        self, inventory: List[Dict[str, Any]]
    ) -> Tuple[List[Tuple[str, str]], int]:
        """
        Plan a sequence of actions using the configured planning method.

        This is the main planning interface that delegates to the appropriate
        planning algorithm based on self.planning_method.

        Args:
            inventory: Current inventory

        Returns:
            Tuple of (action_sequence, final_max_value)
        """
        if self.planning_method == "beam_search":
            return self.plan_beam_search(inventory)
        elif self.planning_method == "bfs":
            return self.plan_optimal_sequence(inventory)
        elif self.planning_method == "greedy":
            greedy_sequence = self.get_greedy_sequence(inventory)
            # Calculate final value for greedy sequence
            if not greedy_sequence:
                return [], max(item["value"] for item in inventory) if inventory else 0

            current_inventory = [copy.deepcopy(item) for item in inventory]
            current_max_value = (
                max(item["value"] for item in current_inventory)
                if current_inventory
                else 0
            )

            for action in greedy_sequence:
                result = self._simulate_action(current_inventory, action)
                if result is not None:
                    current_inventory, value_gain = result
                    current_max_value += value_gain
                else:
                    break

            return greedy_sequence, current_max_value
        else:
            raise ValueError(f"Unknown planning method: {self.planning_method}")

    def get_greedy_sequence(
        self, inventory: List[Dict[str, Any]]
    ) -> List[Tuple[str, str]]:
        """
        Get a greedy sequence of actions that maximizes immediate value gains.

        This method implements a greedy search that at each step chooses the action
        that provides the maximum immediate value gain. Uses the CraftingGame
        environment for accurate simulation of game mechanics.

        Args:
            inventory: Current inventory

        Returns:
            List of actions to take in sequence
        """
        if inventory is None:
            return []

        current_inventory = [copy.deepcopy(item) for item in inventory]
        actions = []

        for _ in range(self.max_depth):
            best_action = None
            best_value_gain = 0
            best_new_inventory = None

            possible_actions = get_possible_actions(current_inventory)
            if not possible_actions:
                break

            # Try each possible action
            for action in possible_actions:
                if action is None:
                    # Submit action - end the sequence
                    continue

                result = self._simulate_action(current_inventory, action)
                if result is not None:
                    new_inventory, value_gain = result
                    if value_gain > best_value_gain:
                        best_value_gain = value_gain
                        best_action = action
                        best_new_inventory = new_inventory

            # If no beneficial action found, stop planning
            if best_action is None or best_value_gain <= 0:
                break

            actions.append(best_action)
            current_inventory = best_new_inventory

        return actions

    def act(self, inventory: List[Dict[str, Any]]) -> Optional[Tuple[str, str]]:
        """
        Choose the best action given the current inventory using the configured planning method.

        This method can be used for interactive play or step-by-step execution.

        Args:
            inventory: Current inventory items

        Returns:
            Best action tuple (item1_name, item2_name) or None to stop
        """
        # Get sequence using configured planning method and return first action
        sequence, _ = self.plan_sequence(inventory)
        return sequence[0] if sequence else None

    def compare_planning_methods(
        self, inventory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare different planning methods for the given inventory.

        This method is useful for analysis and understanding the trade-offs between
        different planning approaches.

        Args:
            inventory: Current inventory items

        Returns:
            Dictionary comparing all planning methods' results
        """
        results = {}

        # Test beam search
        beam_sequence, beam_value = self.plan_beam_search(inventory)
        results["beam_search"] = {
            "sequence": beam_sequence,
            "final_value": beam_value,
            "steps": len(beam_sequence),
        }

        # Test greedy
        greedy_sequence = self.get_greedy_sequence(inventory)
        greedy_final_value = 0
        if greedy_sequence:
            current_inventory = [copy.deepcopy(item) for item in inventory]
            current_max_value = (
                max(item["value"] for item in current_inventory)
                if current_inventory
                else 0
            )

            for action in greedy_sequence:
                result = self._simulate_action(current_inventory, action)
                if result is not None:
                    current_inventory, value_gain = result
                    current_max_value += value_gain
                else:
                    break

            greedy_final_value = current_max_value
        else:
            greedy_final_value = (
                max(item["value"] for item in inventory) if inventory else 0
            )

        results["greedy"] = {
            "sequence": greedy_sequence,
            "final_value": greedy_final_value,
            "steps": len(greedy_sequence),
        }

        # Only run BFS for small search spaces to avoid hanging
        if len(inventory) <= 4:  # Limit BFS to small inventories
            optimal_sequence, optimal_value = self.plan_optimal_sequence(inventory)
            results["bfs"] = {
                "sequence": optimal_sequence,
                "final_value": optimal_value,
                "steps": len(optimal_sequence),
            }
        else:
            results["bfs"] = {
                "sequence": [],
                "final_value": 0,
                "steps": 0,
                "note": "Skipped BFS due to large search space",
            }

        return results

    def plan_and_execute(
        self, env: CraftingGame, max_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Plan and execute a full game episode using the configured planning method.

        This method resets the environment, plans the sequence of actions
        using the configured planning method, and executes them while logging the results.

        Args:
            env: The crafting game environment
            max_steps: Maximum number of steps to take

        Returns:
            Dictionary with episode results including logs and final reward
        """
        env.reset()
        initial_inventory = env.inventory.copy()

        # Plan the sequence using the configured method
        planned_actions, predicted_final_value = self.plan_sequence(initial_inventory)

        episode_log = []
        current_inventory = env.inventory

        # Execute the planned sequence
        for step in range(min(max_steps, len(planned_actions))):
            action = planned_actions[step]

            # Verify action is still valid (should be since we planned optimally)
            possible_actions = get_possible_actions(current_inventory)
            if action not in possible_actions:
                # This shouldn't happen with good planning, but handle gracefully
                # Replan from current state if needed
                remaining_actions, _ = self.plan_sequence(current_inventory)
                if not remaining_actions:
                    break
                action = remaining_actions[0]

            # Execute action
            obs, reward, done, info = env.step(action)
            current_inventory = obs["inventory"]
            new_item = obs["new_item"]

            episode_log.append(
                {
                    "step": step,
                    "action": action,
                    "new_item": new_item,
                    "inventory_size": len(current_inventory),
                    "max_value": max(item["value"] for item in current_inventory)
                    if current_inventory
                    else 0,
                    "inventory": current_inventory.copy(),
                }
            )

            if done:
                break

        # Get final reward
        final_reward = env.get_reward()

        return {
            "initial_inventory": initial_inventory,
            "final_inventory": current_inventory,
            "episode_log": episode_log,
            "final_reward": final_reward,
            "steps_taken": len(episode_log),
            "planned_sequence": planned_actions,
            "predicted_final_value": predicted_final_value,
            "actual_final_value": max(item["value"] for item in current_inventory)
            if current_inventory
            else 0,
            "planning_method": self.planning_method,
        }


def run_oracle_agent(
    domain: str,
    n_runs: int = 10,
    max_steps: int = 10,
    beam_width: int = 5,
    planning_method: str = "beam_search",
) -> pd.DataFrame:
    """
    Run the oracle agent for multiple episodes and return results.

    This function provides an easy way to evaluate the oracle agent's performance
    and generate datasets for analysis.

    Args:
        domain: Crafting domain ('cooking', 'decorations', 'genetics', 'potions')
        n_runs: Number of episodes to run
        max_steps: Maximum steps per episode
        beam_width: Width of the beam for beam search
        planning_method: Planning method to use ('beam_search', 'bfs', or 'greedy')

    Returns:
        DataFrame with step-by-step episode results

    Example:
        >>> df = run_oracle_agent('cooking', n_runs=5, max_steps=10)
        >>> print(f"Average final reward: {df['final_reward'].mean():.2f}")
        >>> print(f"Success rate: {(df['final_reward'] > 0).mean()*100:.1f}%")

        >>> # For large search spaces like decorations, use beam search:
        >>> df = run_oracle_agent('decorations', n_runs=10, beam_width=3, planning_method='beam_search')
    """
    agent = OracleAgent(
        domain,
        max_depth=max_steps,
        beam_width=beam_width,
        planning_method=planning_method,
    )
    env = CraftingGame("none", domain=domain, assign_names=False)

    all_logs = []

    for run_idx in tqdm(range(n_runs)):
        result = agent.plan_and_execute(env, max_steps)

        # Add run information to each step log
        for step_log in result["episode_log"]:
            step_log["run_idx"] = run_idx
            step_log["final_reward"] = result["final_reward"]
            all_logs.append(step_log)

    return pd.DataFrame(all_logs)
