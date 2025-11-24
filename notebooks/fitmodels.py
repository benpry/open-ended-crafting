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

import arviz as az

# %%
import bambi as bmb
import pandas as pd
import pytensor
from bambi.interpret import slopes
from pyprojroot import here

pytensor.config.cxx = "/usr/bin/clang++"

# %%
EXP_NAME = "pilot-9"

df_gameplay = pd.read_csv(here(f"data/human-data/{EXP_NAME}/processed/gameplay.csv"))
df_messages = pd.read_csv(here(f"data/human-data/{EXP_NAME}/processed/messages.csv"))

df_gameplay["participant_id"] = df_gameplay["participant_id"].astype(str)
df_gameplay["chain_id"] = df_gameplay["chain_id"].astype(str)
df_gameplay["score_efficiency"] = df_gameplay["score"] / df_gameplay["n_actions"]

# %%
# compute absolute round numbers
df_gameplay["round_num_abs"] = df_gameplay.apply(
    lambda row: row["round_num"] + (row["chain_pos"] - 1) * 10
    if row["condition"] == "chain"
    else row["round_num"],
    axis=1,
)

df_gameplay["round_num_abs_centered"] = (
    df_gameplay["round_num_abs"] - df_gameplay["round_num_abs"].mean()
)

df_gameplay["participant_or_chain_id"] = df_gameplay.apply(
    lambda row: "participant_" + row["participant_id"]
    if row["condition"] == "individual"
    else "chain_" + row["chain_id"],
    axis=1,
)

df_practice = df_gameplay[df_gameplay["domain"] == "practice"]
df_gameplay = df_gameplay[df_gameplay["domain"] != "practice"]

# %%
model = bmb.Model(
    "score ~ 1 + round_num_abs + condition:round_num_abs + (1 + round_num_abs | domain / participant_or_chain_id)",
    df_gameplay,
)

results = model.fit(
    draws=5000,
    chains=4,
)

# %%
az.summary(results, hdi_prob=0.95).loc["round_num_abs"]

# %%
slopes(
    model,
    results,
    wrt="round_num_abs",
    average_by="condition",
    prob=0.95,
)

# %%
az.plot_trace(results)

# %%
# Make posterior predictions
model.predict(results)

az.plot_ppc(results, num_pp_samples=100)

# %%
# %%
