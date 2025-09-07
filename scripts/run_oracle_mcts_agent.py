"""
Run the Oracle MCTS agent across all domains and save results.
"""

import os
from argparse import ArgumentParser

from pyprojroot import here

from src.agents.oracle_mcts_agent import run_oracle_mcts_agent

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--domain", type=str)
    parser.add_argument("--n_runs", type=int, default=30)
    parser.add_argument("--n_steps", type=int, default=8)
    parser.add_argument("--n_simulations", type=int, default=1000)
    parser.add_argument("--exploration_c", type=float, default=1.25)
    parser.add_argument("--discount_factor", type=float, default=0.98)
    args = parser.parse_args()

    df_domain = run_oracle_mcts_agent(
        args.domain,
        n_runs=args.n_runs,
        n_steps=args.n_steps,
        simulations_per_move=args.n_simulations,
        max_depth=args.n_steps,
        exploration_c=args.exploration_c,
        discount_factor=args.discount_factor,
    )
    df_domain["domain"] = args.domain

    os.makedirs(here("data/simulations"), exist_ok=True)
    df_domain.to_csv(
        here(f"data/simulations/oracle_mcts_results_{args.domain}.csv"), index=False
    )
