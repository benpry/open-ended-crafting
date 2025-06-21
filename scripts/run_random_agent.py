"""
Run the random baseline agent
"""

import pandas as pd
from pyprojroot import here

from src.agents.random_agent import run_random_agent

if __name__ == "__main__":
    df_all = pd.DataFrame()
    for domain in ["cooking", "decorations", "genetics", "potions"]:
        df_domain = run_random_agent(domain, n_runs=1000, n_steps=30)
        df_domain["domain"] = domain
        df_all = pd.concat([df_all, df_domain])

    df_all.to_csv(here("data/simulations/random_baseline_results.csv"), index=False)
