"""
This script takes data from psynet and preprocesses it into a format that's easier to analyze.
"""

import json
import os

import pandas as pd
from pyprojroot import here


def process_gameplay(data_dir: str, trial_type: str):
    """
    Process the actions and rewards for each trial.
    Transform from one row per trial to one row per round.
    """
    df_trial = pd.read_csv(here(f"{data_dir}/{trial_type}.csv"))
    # filter out failed trials
    df_trial = df_trial[~df_trial["failed"]]
    df_trial["vars"] = df_trial["vars"].apply(json.loads)

    # Calculate chain positions for chain trials
    if trial_type == "CraftingGameChainTrial":
        # Sort by network_id and participant_id to get chain positions
        df_trial_sorted = df_trial.sort_values(["network_id", "participant_id"])
        df_trial_sorted["chain_pos"] = (
            df_trial_sorted.groupby("network_id").cumcount() + 1
        )
        # Merge back the chain_pos to original dataframe
        df_trial = df_trial.merge(
            df_trial_sorted[["id", "chain_pos"]], on="id", how="left"
        )
    else:
        df_trial["chain_pos"] = None

    # Transform to one row per round
    rows = []
    for _, trial_row in df_trial.iterrows():
        trial_id = trial_row["id"]
        participant_id = trial_row["participant_id"]
        domain = trial_row["domain"]
        chain_id = trial_row["network_id"]
        chain_pos = trial_row["chain_pos"]
        vars_data = trial_row["vars"]

        # Extract scores and actions for each round
        scores = vars_data.get("scores", {})
        actions = vars_data.get("actions", {})

        # Create one row per round
        for round_num in scores.keys():
            round_num_int = int(round_num)
            score = float(scores[round_num]) if scores[round_num] else 0.0
            round_actions = actions.get(round_num, [])
            n_actions = len(round_actions)

            rows.append(
                {
                    "trial_id": trial_id,
                    "participant_id": participant_id,
                    "chain_id": chain_id,
                    "domain": domain,
                    "round_num": round_num_int,
                    "score": score,
                    "n_actions": n_actions,
                    "chain_pos": chain_pos,
                }
            )

    return pd.DataFrame(rows)


def process_messages(data_dir: str, trial_type: str):
    """
    Process the messages for each trial.
    Extract messages from the messages column (if it exists) and link them to trials.
    """
    df_trial = pd.read_csv(here(f"{data_dir}/{trial_type}.csv"))
    # filter out failed trials
    df_trial = df_trial[~df_trial["failed"]]

    df_trial["vars"] = df_trial["vars"].apply(json.loads)

    # Calculate chain positions for chain trials
    if trial_type == "CraftingGameChainTrial":
        # Sort by network_id and participant_id to get chain positions
        df_trial_sorted = df_trial.sort_values(["network_id", "participant_id"])
        df_trial_sorted["chain_pos"] = (
            df_trial_sorted.groupby("network_id").cumcount() + 1
        )
        # Merge back the chain_pos to original dataframe
        df_trial = df_trial.merge(
            df_trial_sorted[["id", "chain_pos"]], on="id", how="left"
        )
    else:
        df_trial["chain_pos"] = None

    # Transform to one row per message
    rows = []
    for _, trial_row in df_trial.iterrows():
        trial_id = trial_row["id"]
        participant_id = trial_row["participant_id"]
        domain = trial_row["domain"]
        chain_id = trial_row["network_id"]
        message = trial_row["answer"]
        chain_pos = trial_row["chain_pos"]

        rows.append(
            {
                "trial_id": trial_id,
                "participant_id": participant_id,
                "chain_id": chain_id,
                "domain": domain,
                "message": message,
                "chain_pos": chain_pos,
            }
        )

    return pd.DataFrame(rows)


def main():
    DATA_DIR = "data/human-data/pilot-9"

    df_gameplay_chain = process_gameplay(DATA_DIR, "CraftingGameChainTrial")
    df_gameplay_chain["condition"] = "chain"
    df_gameplay_individual = process_gameplay(DATA_DIR, "CraftingGameIndividualTrial")
    df_gameplay_individual["condition"] = "individual"
    df_gameplay = pd.concat([df_gameplay_chain, df_gameplay_individual])

    df_messages_chain = process_messages(DATA_DIR, "CraftingGameChainTrial")
    df_messages_chain["condition"] = "chain"
    df_messages_individual = process_messages(DATA_DIR, "CraftingGameIndividualTrial")
    df_messages_individual["condition"] = "individual"
    df_messages = pd.concat([df_messages_chain, df_messages_individual])

    # save the gameplay data
    os.makedirs(here(f"{DATA_DIR}/processed"), exist_ok=True)
    df_gameplay.to_csv(here(f"{DATA_DIR}/processed/gameplay.csv"), index=False)
    # save the messages data
    df_messages.to_csv(here(f"{DATA_DIR}/processed/messages.csv"), index=False)


if __name__ == "__main__":
    main()
