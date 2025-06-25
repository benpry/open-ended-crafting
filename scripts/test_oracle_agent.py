#!/usr/bin/env python3
"""
Test script for the Oracle Agent.

This script demonstrates the oracle agent's performance across different domains
and compares it with the random baseline.
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.oracle_agent import OracleAgent, run_oracle_agent
from src.agents.random_agent import run_random_agent
from src.environment import CraftingGame


def test_single_domain(domain: str, n_runs: int = 5, max_steps: int = 10):
    """Test oracle agent on a single domain."""
    print(f"\n{'=' * 50}")
    print(f"Testing {domain.upper()} domain")
    print(f"{'=' * 50}")

    # Test oracle agent
    print("Oracle Agent Results:")
    oracle_df = run_oracle_agent(domain, n_runs=n_runs, max_steps=max_steps)
    oracle_rewards = oracle_df.groupby("run_idx")["final_reward"].first()

    print(f"  Average final reward: {oracle_rewards.mean():.2f}")
    print(f"  Max final reward: {oracle_rewards.max():.2f}")
    print(f"  Min final reward: {oracle_rewards.min():.2f}")
    print(f"  Std dev: {oracle_rewards.std():.2f}")

    # Test random agent for comparison
    print("\nRandom Agent Results (for comparison):")
    random_df = run_random_agent(domain, n_runs=n_runs, n_steps=max_steps)
    random_rewards = random_df.groupby("run_idx")["final_reward"].first()

    print(f"  Average final reward: {random_rewards.mean():.2f}")
    print(f"  Max final reward: {random_rewards.max():.2f}")
    print(f"  Min final reward: {random_rewards.min():.2f}")
    print(f"  Std dev: {random_rewards.std():.2f}")

    # Calculate improvement
    improvement = (
        (oracle_rewards.mean() - random_rewards.mean()) / random_rewards.mean()
    ) * 100
    print(f"\nImprovement: {improvement:.1f}% better than random")

    return oracle_rewards.mean(), random_rewards.mean()


def test_detailed_example(domain: str = "cooking"):
    """Show a detailed example of oracle agent planning."""
    print(f"\n{'=' * 50}")
    print(f"Detailed Example: {domain.upper()} domain")
    print(f"{'=' * 50}")

    agent = OracleAgent(domain)
    env = CraftingGame("none", domain=domain, assign_names=False)

    # Reset and show initial state
    env.reset()
    print("Initial inventory:")
    for item in env.inventory:
        print(
            f"  {item['emoji']} {item['name']} (value: {item['value']}, tool: {item.get('tool', False)})"
        )

    print(f"\nInitial max value: {max(item['value'] for item in env.inventory)}")

    # Plan and execute
    result = agent.plan_and_execute(env, max_steps=10)

    print("\nAction sequence:")
    for step_log in result["episode_log"]:
        action = step_log["action"]
        new_item = step_log["new_item"]
        print(
            f"  Step {step_log['step']}: {action[0]} + {action[1]} = {new_item['name'] if new_item else 'None'}"
        )
        if new_item:
            print(f"    New item value: {new_item['value']}")
        print(f"    Max inventory value: {step_log['max_value']}")

    print(f"\nFinal reward: {result['final_reward']}")
    print(f"Steps taken: {result['steps_taken']}")


def test_planning_methods():
    """Test different planning methods on various domains."""

    domains = ["cooking", "decorations", "animals", "potions"]

    for domain in domains:
        print(f"\n=== Testing domain: {domain} ===")

        # Create environment and get initial inventory
        env = CraftingGame("none", domain=domain, assign_names=False)
        env.reset()
        initial_inventory = env.inventory.copy()

        print(f"Initial inventory size: {len(initial_inventory)}")
        print(
            f"Initial max value: {max(item['value'] for item in initial_inventory) if initial_inventory else 0}"
        )

        # Test different planning methods
        methods = [
            ("beam_search", 5, "Beam Search (width=5)"),
            ("beam_search", 3, "Beam Search (width=3)"),
            ("greedy", None, "Greedy"),
        ]

        # Only test BFS on small inventories
        if len(initial_inventory) <= 4:
            methods.append(("bfs", None, "BFS (exhaustive)"))

        for method, beam_width, description in methods:
            try:
                print(f"\nTesting {description}...")

                # Create agent with specific method
                agent = OracleAgent(
                    domain=domain,
                    max_depth=8,
                    beam_width=beam_width or 5,
                    planning_method=method,
                )

                # Time the planning
                start_time = time.time()
                sequence, final_value = agent.plan_sequence(initial_inventory)
                planning_time = time.time() - start_time

                print(f"  Planning time: {planning_time:.3f}s")
                print(f"  Planned steps: {len(sequence)}")
                print(f"  Expected final value: {final_value}")

                if sequence:
                    print(f"  First few actions: {sequence[:3]}")

            except Exception as e:
                print(f"  Error with {description}: {e}")

        # Compare all methods at once if inventory is small enough
        if len(initial_inventory) <= 4:
            print("\nComparing all methods...")
            try:
                agent = OracleAgent(domain=domain)
                comparison = agent.compare_planning_methods(initial_inventory)

                for method_name, results in comparison.items():
                    if "note" not in results:
                        print(
                            f"  {method_name}: {results['steps']} steps, value {results['final_value']}"
                        )
                    else:
                        print(f"  {method_name}: {results['note']}")
            except Exception as e:
                print(f"  Error in comparison: {e}")


def test_full_episode():
    """Test a full episode with beam search."""
    print("\n=== Testing full episode with beam search ===")

    domain = "decorations"  # This was the problematic domain
    agent = OracleAgent(domain=domain, beam_width=3, planning_method="beam_search")
    env = CraftingGame("none", domain=domain, assign_names=False)

    start_time = time.time()
    result = agent.plan_and_execute(env, max_steps=8)
    execution_time = time.time() - start_time

    print(f"Domain: {domain}")
    print(f"Planning method: {result['planning_method']}")
    print(f"Total time: {execution_time:.3f}s")
    print(f"Steps taken: {result['steps_taken']}")
    print(f"Final reward: {result['final_reward']}")
    print(
        f"Predicted vs actual value: {result['predicted_final_value']} vs {result['actual_final_value']}"
    )


def main():
    """Main test function."""
    print("Oracle Agent Test Suite")
    print("=" * 50)

    domains = ["cooking", "decorations", "animals", "potions"]
    results = {}

    # Test each domain
    for domain in domains:
        oracle_avg, random_avg = test_single_domain(domain, n_runs=10, max_steps=10)
        results[domain] = {"oracle": oracle_avg, "random": random_avg}

    # Summary
    print(f"\n{'=' * 50}")
    print("SUMMARY")
    print(f"{'=' * 50}")
    print(f"{'Domain':<12} {'Oracle':<8} {'Random':<8} {'Improvement':<12}")
    print("-" * 50)

    total_oracle = 0
    total_random = 0

    for domain in domains:
        oracle_avg = results[domain]["oracle"]
        random_avg = results[domain]["random"]
        improvement = ((oracle_avg - random_avg) / random_avg) * 100
        print(
            f"{domain:<12} {oracle_avg:<8.1f} {random_avg:<8.1f} {improvement:<12.1f}%"
        )
        total_oracle += oracle_avg
        total_random += random_avg

    overall_improvement = ((total_oracle - total_random) / total_random) * 100
    print("-" * 50)
    print(
        f"{'Overall':<12} {total_oracle / len(domains):<8.1f} {total_random / len(domains):<8.1f} {overall_improvement:<12.1f}%"
    )

    # Show detailed example
    test_detailed_example("cooking")

    # Test planning methods and full episode
    test_planning_methods()
    test_full_episode()


if __name__ == "__main__":
    main()
