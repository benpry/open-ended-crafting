# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: analysis
#     language: python
#     name: python3
# ---

from ast import literal_eval

# %%
import bambi as bmb
import pandas as pd
from pyprojroot import here

# %%
EXP_NAME = "pilot-7"
df_trials = pd.read_csv(here(f"data/human-data/{EXP_NAME}/trials.csv"))
df_trials["actions"] = df_trials["actions"].apply(literal_eval)
df_trials["n_actions"] = df_trials["actions"].apply(len)
df_trials["score_per_action"] = df_trials["score"] / df_trials["n_actions"]
df_trials["trial_idx"] = df_trials["trial_idx"] + 1
df_trials = df_trials[df_trials["n_actions"] > 0]
df_messages = pd.read_csv(here(f"data/human-data/{EXP_NAME}/messages.csv"))
df_surveys = pd.read_csv(here(f"data/human-data/{EXP_NAME}/surveys.csv"))

# %%
# recompute trial index
df_trials["trial_idx"] = (
    df_trials.sort_values(["player_id", "domain", "trial_idx"])
    .groupby(["player_id", "domain"])
    .cumcount()
    + 1
)

# only consider trials from participants who completed the practice
completed_player_ids = df_surveys["player_id"].unique()
df_trials = df_trials[df_trials["player_id"].isin(completed_player_ids)]

df_practice = df_trials[df_trials["domain"] == "practice"]
df_trials = df_trials[df_trials["domain"] != "practice"]

# %%
df_trials

# %%
model = bmb.Model(
    "score ~ trial_idx + (trial_idx | player_id) + (trial_idx | domain)",
    df_trials[["score", "trial_idx", "player_id", "domain"]],
)

results = model.fit(
    draws=3000,
    chains=3,
)

# %%
