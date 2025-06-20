"""
Run the random and oracle agents on all domains and compare their performance.
"""

import pandas as pd
from pyprojroot import here

from src.agents.oracle_agent import run_oracle_agent
from src.agents.random_agent import run_random_agent

if __name__ == "__main__":
    domains = ["cooking", "decorations", "genetics", "potions"]
    df = pd.DataFrame()

    for domain in domains:
        print(f"Running domain: {domain}")

        # Run random agent
        df_random = run_random_agent(domain, n_runs=100, n_steps=5).assign(
            agent="random", domain=domain
        )

        # Run oracle agent with beam search (faster for large search spaces)
        # Use smaller beam width for decorations to ensure speed
        df_oracle = run_oracle_agent(
            domain,
            n_runs=100,
            max_steps=10,
            beam_width=100,
            planning_method="beam_search",
        ).assign(agent="oracle", domain=domain)

        df_random_trials = df_random[["run_idx", "final_reward"]].drop_duplicates()
        df_oracle_trials = df_oracle[["run_idx", "final_reward"]].drop_duplicates()
        print(f"Random agent score: {df_random_trials['final_reward'].mean():.2f}")
        print(f"Oracle agent score: {df_oracle_trials['final_reward'].mean():.2f}")
        df = pd.concat([df, df_random, df_oracle])

    df.to_csv(here("data/simulations/agent_comparison.csv"), index=False)
