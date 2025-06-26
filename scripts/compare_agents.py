"""
Run the random and oracle agents on all domains and compare their performance.
"""

import pandas as pd
from pyprojroot import here

from src.agents.oracle_agent import run_oracle_agent
from src.agents.random_agent import run_random_agent

if __name__ == "__main__":
    domains = ["cooking", "decorations", "animals", "potions"]
    df = pd.DataFrame()

    for domain in domains:
        print(f"Running domain: {domain}")

        # Run random agent
        df_random = run_random_agent(domain, n_runs=100, n_steps=5).assign(
            agent_type="random", domain=domain
        )

        # Run oracle agent with beam search (faster for large search spaces)
        # Use smaller beam width for decorations to ensure speed
        df_oracle = run_oracle_agent(
            domain,
            n_runs=100,
            max_depth=10,
        ).assign(agent_type="oracle", domain=domain)

        # Get the final scores for each run
        # Both agents should have 'final_reward' column
        df_random_final = (
            df_random.groupby("run_idx")["final_reward"].last().reset_index()
        )
        df_oracle_final = (
            df_oracle.groupby("run_idx")["final_reward"].last().reset_index()
        )

        print(f"Random agent scores: {df_random_final['final_reward'].describe()}")
        print(f"Oracle agent scores: {df_oracle_final['final_reward'].describe()}")

        oracle_episode_lengths = (
            df_oracle.groupby(["domain", "run_idx"])["step"]
            .max()
            .reset_index()
            .rename(columns={"step": "episode_length"})["episode_length"]
        )
        print(f"Median oracle episode length: {oracle_episode_lengths.median()}")
        print(f"Mean oracle episode length: {oracle_episode_lengths.mean()}")

        example_oracle_episode = df_oracle[df_oracle["run_idx"] == 0]
        print(example_oracle_episode["action"])

        df = pd.concat([df, df_random, df_oracle])

    df.to_csv(here("data/simulations/agent_comparison.csv"), index=False)
