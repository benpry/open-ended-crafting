# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: oecraft
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
from pyprojroot import here
import plotnine as p9

# %%
EXP_NAME = "pilot-9"
df_gameplay = pd.read_csv(here(f"data/human-data/{EXP_NAME}/processed/gameplay.csv"))
df_messages = pd.read_csv(here(f"data/human-data/{EXP_NAME}/processed/messages.csv"))

df_gameplay["participant_id"] = df_gameplay["participant_id"].astype(str)
df_gameplay["chain_id"] = df_gameplay["chain_id"].astype(str)
df_gameplay["score_efficiency"] = df_gameplay["score"] / df_gameplay["n_actions"]

# %%
# plot performance over generations for the chain condition
df_chain = df_gameplay[df_gameplay["condition"] == "chain"]
df_chain["round_num_abs"] = df_chain.apply(
    lambda row: row["round_num"] + (row["chain_pos"] - 1) * 10, axis=1
)

p = (
    p9.ggplot(df_chain, p9.aes(x="round_num_abs", y="score", color="chain_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.5)
    + p9.geom_line(alpha=0.5)
    + p9.geom_vline(xintercept=(10, 20, 30), color="black", linetype="dashed")
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(x="Absolute round number", y="Score", title="Chains")
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p.save(here(f"figures/{EXP_NAME}-chain-scores.png"), width=8, height=6)
p

# %%
# plot performance over generations for the chain condition
df_individual = df_gameplay[df_gameplay["condition"] == "individual"]

p = (
    p9.ggplot(df_individual, p9.aes(x="round_num", y="score", color="participant_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.5)
    + p9.geom_line(alpha=0.5)
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(x="Round number", y="Score", title="Immortal individual")
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p.save(here(f"figures/{EXP_NAME}-individual-scores.png"), width=8, height=6)
p

# %%
# plot performance over generations for the chain condition
df_chain = df_gameplay[df_gameplay["condition"] == "chain"]
df_chain["round_num_abs"] = df_chain.apply(
    lambda row: row["round_num"] + (row["chain_pos"] - 1) * 10, axis=1
)

p = (
    p9.ggplot(df_chain, p9.aes(x="round_num_abs", y="n_actions", color="chain_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    # + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.5)
    + p9.geom_line(alpha=0.5)
    + p9.geom_vline(xintercept=(10, 20, 30), color="black", linetype="dashed")
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(x="Absolute round number", y="Number of actions", title="Chains")
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p.save(here(f"figures/{EXP_NAME}-chain-n_actions.png"), width=8, height=6)
p

# %%
# plot performance over generations for the chain condition
df_ind = df_gameplay[df_gameplay["condition"] == "individual"]

p = (
    p9.ggplot(df_ind, p9.aes(x="round_num", y="n_actions", color="participant_id"))
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    # + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.5)
    + p9.geom_line(alpha=0.5)
    + p9.geom_vline(xintercept=(10, 20, 30), color="black", linetype="dashed")
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(x="Round number", y="Number of actions", title="Immortal individuals")
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p.save(here(f"figures/{EXP_NAME}-individual-n_actions.png"), width=8, height=6)
p

# %%
# plot performance over generations for the chain condition
df_chain = df_gameplay[df_gameplay["condition"] == "chain"]
df_chain["round_num_abs"] = df_chain.apply(
    lambda row: row["round_num"] + (row["chain_pos"] - 1) * 10, axis=1
)

p = (
    p9.ggplot(
        df_chain, p9.aes(x="round_num_abs", y="score_efficiency", color="chain_id")
    )
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    # + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.5)
    + p9.geom_line(alpha=0.5)
    + p9.geom_vline(xintercept=(10, 20, 30), color="black", linetype="dashed")
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(x="Absolute round number", y="Score efficiency", title="Chains")
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p.save(here(f"figures/{EXP_NAME}-chain-score_efficiency.png"), width=8, height=6)
p

# %%
# plot performance over generations for the chain condition
df_ind = df_gameplay[df_gameplay["condition"] == "individual"]

p = (
    p9.ggplot(
        df_ind, p9.aes(x="round_num", y="score_efficiency", color="participant_id")
    )
    + p9.facet_wrap("~domain")
    + p9.scale_x_continuous(breaks=range(1, 41, 4))
    # + p9.coord_cartesian(ylim=(0, 100))
    + p9.geom_point(alpha=0.5)
    + p9.geom_line(alpha=0.5)
    + p9.geom_vline(xintercept=(10, 20, 30), color="black", linetype="dashed")
    + p9.geom_smooth(
        p9.aes(group=1),
        method="loess",
    )
    + p9.theme_minimal(base_size=14)
    + p9.labs(x="Round number", y="Score efficiency", title="Immortal individuals")
    + p9.theme(
        legend_position="none",
        plot_background=p9.element_rect(fill="white", color="white"),
    )
)
p.save(here(f"figures/{EXP_NAME}-individual-score_efficiency.png"), width=8, height=6)
p

# %%
df_messages[(df_messages["domain"] == "cooking") & (df_messages["chain_id"] == 1)][
    "message"
].tolist()

# %%
df_messages[(df_messages["domain"] == "potions") & (df_messages["chain_id"] == 7)][
    "message"
].tolist()

# %%
df_messages[df_messages["condition"] == "individual"]["message"].tolist()
