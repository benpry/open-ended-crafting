"""
Given a raw dataset, preprocess it, make plots, and fit models.
"""

import os
import warnings
from argparse import ArgumentParser

import arviz as az
import bambi as bmb
import pandas as pd
import plotnine as p9
from bambi.interpret import slopes
from preprocess_psynet_data import process_gameplay, process_messages
from pyprojroot import here


def fit_models(df_gameplay: pd.DataFrame, args):
    model = bmb.Model(
        "score ~ 1 + round_num_abs + condition:round_num_abs + (1 + round_num_abs | domain / participant_or_chain_id)",
        df_gameplay,
    )

    results = model.fit(
        draws=5000,
        chains=4,
    )

    summary = az.summary(results, hdi_prob=0.95)
    if "condition:round_num_abs[individual]" in summary.index:
        interaction = summary.loc["condition:round_num_abs[individual]"]
    elif "condition:round_num_abs[chain]" in summary.index:
        interaction = summary.loc["condition:round_num_abs[chain]"]
    else:
        interaction = "Couldn't find interaction in summary"
        warnings.warn("Couldn't find interaction in summary")

    marginal_effects = slopes(
        model,
        results,
        wrt="round_num_abs",
        average_by="condition",
        prob=0.95,
    )

    with open(here(f"data/results/{args.exp_name}-model-results.txt"), "w") as f:
        f.write("MARGINAL EFFECTS\n" + marginal_effects.to_string() + "\n")
        f.write("INTERACTION\n" + interaction.to_string() + "\n")
        f.write("SUMMARY\n" + summary.to_string() + "\n")


def make_plots(df_gameplay: pd.DataFrame, args):
    df_chain = df_gameplay[df_gameplay["condition"] == "chain"]
    df_chain["round_num_abs"] = df_chain.apply(
        lambda row: row["round_num"] + (row["chain_pos"] - 1) * 10, axis=1
    )

    p_chain_scores = (
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
    p_chain_scores.save(
        here(f"figures/{args.exp_name}-chain-scores.png"), width=8, height=6
    )

    df_individual = df_gameplay[df_gameplay["condition"] == "individual"]

    p_individual_scores = (
        p9.ggplot(
            df_individual, p9.aes(x="round_num", y="score", color="participant_id")
        )
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
    p_individual_scores.save(
        here(f"figures/{args.exp_name}-individual-scores.png"), width=8, height=6
    )


def main(args):
    data_dir = here(f"data/human-data/{args.exp_name}")
    df_gameplay_chain = process_gameplay(data_dir, "CraftingGameChainTrial")
    df_gameplay_chain["condition"] = "chain"
    df_gameplay_individual = process_gameplay(data_dir, "CraftingGameIndividualTrial")
    df_gameplay_individual["condition"] = "individual"
    df_gameplay = pd.concat([df_gameplay_chain, df_gameplay_individual])

    df_gameplay["participant_id"] = df_gameplay["participant_id"].astype(str)
    df_gameplay["chain_id"] = df_gameplay["chain_id"].astype(str)
    df_gameplay["score_efficiency"] = df_gameplay["score"] / df_gameplay["n_actions"]

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

    df_messages_chain = process_messages(data_dir, "CraftingGameChainTrial")
    df_messages_chain["condition"] = "chain"
    df_messages_individual = process_messages(data_dir, "CraftingGameIndividualTrial")
    df_messages_individual["condition"] = "individual"
    df_messages = pd.concat([df_messages_chain, df_messages_individual])

    # save the gameplay data
    os.makedirs(here(f"{data_dir}/processed"), exist_ok=True)
    df_gameplay.to_csv(here(f"{data_dir}/processed/gameplay.csv"), index=False)
    # save the messages data
    df_messages.to_csv(here(f"{data_dir}/processed/messages.csv"), index=False)

    df_gameplay = df_gameplay[df_gameplay["domain"] != "practice"]

    make_plots(df_gameplay, args)
    fit_models(df_gameplay, args)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--exp_name", type=str, default="pilot-9")
    args = parser.parse_args()
    main(args)
