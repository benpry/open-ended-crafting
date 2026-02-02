# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
from pyprojroot import here
import plotnine as p9
import numpy as np

# %%
EXP_NAME = "experiment-1"
df_gameplay = pd.read_csv(here(f"data/human-data/{EXP_NAME}/processed/gameplay.csv"))
df_messages = pd.read_csv(here(f"data/human-data/{EXP_NAME}/processed/messages.csv"))

df_gameplay["participant_id"] = df_gameplay["participant_id"].astype(str)
df_gameplay["chain_id"] = df_gameplay["chain_id"].astype(str)
df_gameplay["score_efficiency"] = df_gameplay["score"] / df_gameplay["n_actions"]

# %%
df_chain = df_gameplay[df_gameplay["condition"] == "chain"]
df_ind = df_gameplay[df_gameplay["condition"] == "individual"]

# %%
p_chain_scores = (
    p9.ggplot(df_chain, p9.aes(x="round_num_abs", y="score", color="chain_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.15, position=p9.position_jitter(width=0.4, height=0.2))
    + p9.geom_vline(xintercept=(10.5, 20.5, 30.5), color="black", linetype="dashed")
    + p9.geom_smooth(
        p9.aes(group=1),
        method="lm",
    )
    + p9.theme_minimal(base_size=18)
    + p9.labs(x="Absolute round number", y="Score", title="Chains")
    + p9.theme(
        legend_position="none",
        # plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p_chain_scores.save(here(f"figures/{EXP_NAME}-chain-scores.pdf"), width=8, height=6)
p_chain_scores

# %%
p_individual_scores = (
    p9.ggplot(df_ind, p9.aes(x="round_num_abs", y="score", color="participant_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.15, position=p9.position_jitter(width=0.4, height=0.2))
    + p9.geom_smooth(
        p9.aes(group=1),
        method="lm",
    )
    + p9.theme_minimal(base_size=18)
    + p9.labs(x="Absolute round number", y="Score", title="Immortal Individuals")
    + p9.theme(
        legend_position="none",
        # plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p_individual_scores.save(
    here(f"figures/{EXP_NAME}-individual-scores.pdf"), width=8, height=6
)
p_individual_scores

# %%
p_all_scores = p9.ggplot(
    df_gameplay, p9.aes(x="round_num_abs", y="score", color="condition")
)

# %%
import random

# chains_to_plot = [
#     np.random.choice(range(1, 20), size=4, replace=False) + d * 20 for d in range(4)
# ]
# # flatten the list
# chains_to_plot = [item for sublist in chains_to_plot for item in sublist]
print(f"chains_to_plot: {chains_to_plot}")
df_chain["chain_id"] = df_chain["chain_id"].astype(int)
df_example_chains = df_chain[df_chain["chain_id"].isin(chains_to_plot)]
p_example_chains = (
    p9.ggplot(df_example_chains, p9.aes(x="round_num_abs", y="score", color="domain"))
    + p9.facet_wrap("~chain_id")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.geom_vline(xintercept=(10.5, 20.5, 30.5), color="black", linetype="dashed")
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.5, position=p9.position_jitter(width=0.2, height=0))
    + p9.stat_smooth(method="mavg", method_args={"window": 5}, se=False)
    + p9.theme_minimal(base_size=14)
    + p9.labs(
        x="Absolute round number",
        y="Score",
        title="Example chains with moving averages",
    )
    # + p9.theme(
    #     plot_background=p9.element_rect(fill="white", color="white"),
    # )
)
p_example_chains.save(here(f"figures/{EXP_NAME}-example-chains.pdf"), width=8, height=6)
p_example_chains

# %%
p_example_chains.save(here(f"figures/{EXP_NAME}-example-chains.png"), width=8, height=6)


# %%
p_round_aggregates = (
    p9.ggplot(df_chain, p9.aes(x="round_num_abs", y="score", color="chain_id"))
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.stat_summary(
        p9.aes(group=1),
        fun_data="mean_cl_boot",
        geom="pointrange",
    )
    + p9.geom_vline(xintercept=(10.5, 20.5, 30.5), color="black", linetype="dashed")
    + p9.theme_minimal(base_size=18)
    + p9.labs(x="Absolute round number", y="Score", title="Aggregate chain performance")
    + p9.theme(
        legend_position="none",
        # plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p_round_aggregates.save(
    here(f"figures/{EXP_NAME}-round-aggregates.pdf"), width=8, height=6
)
p_round_aggregates

# %%
p_individual_round_aggregates = (
    p9.ggplot(df_ind, p9.aes(x="round_num_abs", y="score", color="chain_id"))
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.stat_summary(
        p9.aes(group=1),
        fun_data="mean_cl_boot",
        geom="pointrange",
    )
    # + p9.geom_smooth(
    #     p9.aes(group=1),
    #     method="loess",
    # )
    + p9.theme_minimal(base_size=14)
    + p9.labs(
        x="Absolute round number", y="Score", title="Aggregate individual performance"
    )
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p_individual_round_aggregates.save(
    here(f"figures/{EXP_NAME}-individual-round-aggregates.png"), width=8, height=6
)
p_individual_round_aggregates

# %%
df_chain["running_avg_score"] = df_chain.groupby("chain_id")["score"].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)
df_chain["running_avg_score"] = df_chain["running_avg_score"].fillna(df_chain["score"])
p_chain_running_avg_scores = (
    p9.ggplot(
        df_chain, p9.aes(x="round_num_abs", y="running_avg_score", color="chain_id")
    )
    + p9.facet_wrap("~domain")
    + p9.geom_vline(xintercept=(10.5, 20.5, 30.5), color="black", linetype="dashed")
    + p9.geom_point(alpha=0.3, position=p9.position_jitter(width=0.2, height=0))
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p_chain_running_avg_scores.save(
    here(f"figures/{EXP_NAME}-chain-running-avg-scores.png"), width=8, height=6
)
p_chain_running_avg_scores

# %%
df_chain.head()

# %%
# make the plot with learning rates for each individual
df_chain["participant_chain"] = (
    df_chain["participant_id"].astype(str) + "_" + df_chain["chain_id"].astype(str)
)
p_individual_learning_rates = (
    p9.ggplot(df_chain, p9.aes(x="round_num_abs", y="score", color="chain_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.05, position=p9.position_jitter(width=0.2, height=0))
    + p9.geom_vline(xintercept=(10.5, 20.5, 30.5), color="black", linetype="dashed")
    + p9.geom_line(
        p9.aes(group="participant_chain"),
        stat="smooth",
        method="lm",
        alpha=0.4,
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(
        x="Absolute round number",
        y="Score",
        title="Linear regressions for individuals within chains",
    )
    + p9.theme(
        legend_position="none",
        # plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p_individual_learning_rates.save(
    here(f"figures/{EXP_NAME}-individual-regressions.pdf"), width=8, height=6
)
p_individual_learning_rates

# %%
