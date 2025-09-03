"""
Run the Oracle MCTS agent across all domains and save results.
"""

import pandas as pd
from pyprojroot import here

from src.agents.oracle_agent import run_oracle_mcts_agent

if __name__ == "__main__":
    df_all = pd.DataFrame()
    for domain in ["cooking", "decorations", "animals", "potions"]:
        df_domain = run_oracle_mcts_agent(
            domain,
            n_runs=30,
            n_steps=15,
            simulations_per_move=5000,
            max_depth=15,
            exploration_c=1.25,
            discount_factor=0.98,
        )
        df_domain["domain"] = domain
        df_all = pd.concat([df_all, df_domain])

    df_all.to_csv(here("data/simulations/oracle_mcts_results.csv"), index=False)
