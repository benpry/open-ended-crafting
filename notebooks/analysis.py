# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
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

import matplotlib.pyplot as plt
import numpy as np

# %%
import pandas as pd
import plotnine as p9
from pyprojroot import here

# %%
EXP_NAME = "pilot1"
df_trials = pd.read_csv(here(f"data/{EXP_NAME}/trials.csv"))
df_trials["domain"] = df_trials["domain"].apply(
    lambda x: "species" if x == "animals" else x
)
df_trials["actions"] = df_trials["actions"].apply(literal_eval)
df_trials["n_actions"] = df_trials["actions"].apply(len)
df_trials["trial_idx"] = df_trials["trial_idx"] + 1
df_trials = df_trials[df_trials["n_actions"] > 0]
df_messages = pd.read_csv(here(f"data/{EXP_NAME}/messages.csv"))
df_surveys = pd.read_csv(here(f"data/{EXP_NAME}/surveys.csv"))

# %%
# get the baseline means
baseline_means = (
    pd.read_csv(here("data/simulations/random_baseline_results.csv"))
    .assign(
        timestep=lambda x: x["timestep"] + 1,
        run_idx=lambda x: pd.Categorical(x["run_idx"]),
        domain=lambda x: np.where(x["domain"] == "animals", "species", x["domain"]),
    )
    .query("timestep == 10")
    .groupby(["domain"])
    .mean("score")
    .reset_index()
)

# get the trial means
df_trials = pd.read_csv(here("data/pilot1/trials.csv")).assign(
    domain=lambda x: np.where(x["domain"] == "animals", "species", x["domain"]),
)

# get the message means
df_messages = pd.read_csv(here("data/pilot1/messages.csv"))

# %%
df_trials["n_actions"].hist()
plt.xlabel("Number of actions")
plt.ylabel("Number of trials")
plt.grid(False)
plt.savefig(here("figures/n_actions_hist.png"))

# %%
p = (
    p9.ggplot(df_trials, p9.aes(x="trial_idx", y="score", color="player_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 11))
    + p9.geom_hline(
        data=baseline_means,
        mapping=p9.aes(yintercept="score"),
        linetype="dashed",
        size=1,
    )
    + p9.geom_point(alpha=0.5)
    + p9.geom_line(alpha=0.5)
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(x="Trial Number", y="Score")
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white"),
    )
)
p.save(here(f"figures/{EXP_NAME}-scores.png"), dpi=300, width=8, height=6)

# %%
messages = list(df_messages["message"])

# %%
list(df_surveys[df_surveys["question"] == "feedback"]["answer"])

# %%
df_trials["n_actions"] = df_trials["actions"].apply(lambda x: len(x))

# %%
df_trials["n_actions"].value_counts()
