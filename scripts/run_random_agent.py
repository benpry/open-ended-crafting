"""
Run the random baseline agent
"""

import pandas as pd

from oecraft.agents.random_agent import run_random_agent
from oecraft.game_descriptors import GAME_DESCRIPTORS

if __name__ == "__main__":
    df_all = pd.DataFrame()
    for domain, game_descriptor in GAME_DESCRIPTORS.items():
        print(f"Running random agent for {domain}")
        df = run_random_agent(game_descriptor=game_descriptor, n_runs=10, n_steps=10)
        print(df.head())
