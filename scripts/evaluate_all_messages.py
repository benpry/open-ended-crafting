"""
Evaluate all the messages that people wrote in the experiment.
"""

import asyncio
from argparse import ArgumentParser

import pandas as pd
from pyprojroot import here

from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.optimization.simulation import run_simulations


def main(args):
    df_messages = pd.read_csv("data/human-data/experiment-1/processed/messages.csv")
    if args.num_messages is not None:
        df_messages = df_messages.sample(args.num_messages)
    all_sim_dfs = []
    for _, row in df_messages.iterrows():
        print(f"Evaluating message {row['trial_id']}")
        args.descriptor = GAME_DESCRIPTORS[row["domain"]]
        args.starting_message = row["message"]
        args.run_name = f"message_{row['trial_id']}"
        df_sims = asyncio.run(run_simulations(args))
        df_sims["message_id"] = row["trial_id"]
        all_sim_dfs.append(df_sims)

    df_all_sims = pd.concat(all_sim_dfs)
    df_all_sims.to_csv(here(f"{args.output_dir}/all_message_evaluation_sims.csv"), index=False)
    print(f"Saved all simulation results to {args.output_dir}/all_message_evaluation_sims.csv")

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--naming_model", type=str, default="openai/gpt-oss-20b")
    parser.add_argument("--agent_model", type=str, default="gemini-2.5-flash")
    parser.add_argument("--num-rounds", type=int, default=5)
    parser.add_argument("--num-chains", type=int, default=10)
    parser.add_argument("--chain-length", type=int, default=1)
    parser.add_argument("--output-dir", type=str, default="data/simulations")
    parser.add_argument("--verbose", type=bool, default=False)
    parser.add_argument("--num-messages", type=int, default=None)

    args = parser.parse_args()

    main(args)
