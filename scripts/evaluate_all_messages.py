"""
Evaluate all the messages that people wrote in the experiment.
"""

import asyncio
from argparse import ArgumentParser

import pandas as pd

from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.optimization.simulation import run_simulations


def main(args):
    df_messages = pd.read_csv("data/human-data/experiment-1/processed/messages.csv")
    for _, row in df_messages.iterrows():
        args.descriptor = GAME_DESCRIPTORS[row["domain"]]
        args.starting_message = row["message"]
        args.run_name = f"message_{row['trial_id']}"
        asyncio.run(run_simulations(args))


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--naming_model", type=str, default="openai/gpt-oss-20b")
    parser.add_argument("--agent_model", type=str, default="gemini-2.5-flash")
    parser.add_argument("--num-rounds", type=int, default=5)
    parser.add_argument("--num-chains", type=int, default=10)
    parser.add_argument("--chain-length", type=int, default=1)
    parser.add_argument("--output-dir", type=str, default="data/simulations")
    parser.add_argument("--verbose", type=bool, default=False)

    args = parser.parse_args()

    main(args)
