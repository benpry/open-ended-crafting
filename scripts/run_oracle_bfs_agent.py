"""
Run the Oracle BFS agent across all domains and save results.
"""

import os
from argparse import ArgumentParser

from pyprojroot import here

from oecraft.agents.oracle_bfs_agent import run_oracle_bfs_agent

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--domain", type=str)
    parser.add_argument("--n_runs", type=int, default=30)
    parser.add_argument("--n_steps", type=int, default=8)
    args = parser.parse_args()

    df_domain = run_oracle_bfs_agent(
        args.domain,
        n_runs=args.n_runs,
        n_steps=args.n_steps,
    )
    df_domain["domain"] = args.domain

    os.makedirs(here("data/simulations"), exist_ok=True)
    df_domain.to_csv(
        here(f"data/simulations/oracle_bfs_results_{args.domain}.csv"), index=False
    )
