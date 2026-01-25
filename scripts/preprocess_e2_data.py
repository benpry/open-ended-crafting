import json
import os

import pandas as pd
from pyprojroot import here

message_condition_aggregator = {
    "none": "none",
    "gold": "gold",
    "best": "best 3",
    "second_best": "best 3",
    "third_best": "best 3",
    "worst": "worst 2",
    "second_worst": "worst 2",
}


def process_gameplay(data_dir: str, trial_type: str):
    """
    Process the actions and rewards for each trial.
    Transform from one row per trial to one row per round.
    """
    df_trial = pd.read_csv(here(f"{data_dir}/{trial_type}.csv"))
    # filter out failed trials
    df_trial = df_trial[~df_trial["failed"]]
    df_trial["vars"] = df_trial["vars"].apply(json.loads)

    # Transform to one row per round
    rows = []
    for _, trial_row in df_trial.iterrows():
        trial_id = trial_row["id"]
        participant_id = trial_row["participant_id"]
        domain = trial_row["domain"]
        network_id = trial_row["network_id"]
        message_condition = trial_row["message_condition"]
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
                    "network_id": network_id,
                    "message_condition": message_condition,
                    "message_condition_agg": message_condition_aggregator[
                        message_condition
                    ],
                    "domain": domain,
                    "round_num": round_num_int,
                    "score": score,
                    "n_actions": n_actions,
                }
            )

    return pd.DataFrame(rows)


def main():
    DATA_DIR = "data/human-data/experiment-2"
    df_gameplay = process_gameplay(DATA_DIR, "CraftingGameTrial")
    os.makedirs(here(f"{DATA_DIR}/processed"), exist_ok=True)
    df_gameplay.to_csv(here(f"{DATA_DIR}/processed/gameplay.csv"), index=False)


if __name__ == "__main__":
    main()
