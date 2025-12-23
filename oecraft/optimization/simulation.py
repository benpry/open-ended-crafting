"""
Set up an agent in the crafting game and run it.
"""

import asyncio
import json
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from pyprojroot import here

from oecraft.agents.lm_agent import CraftingAgent
from oecraft.environment import CraftingGame, LMCraftingGame


async def run_chain(
    descriptor, chain_num, args, output_path, file_lock, existing_df=None, verbose=True
):
    # Create independent environment and agent for each chain
    game = CraftingGame(
        descriptor=descriptor, model=args.naming_model, assign_names=True
    )
    env = LMCraftingGame(game)
    agent = CraftingAgent(
        env,
        model=args.agent_model,
        generate_kwargs={
            "top_p": 0.95,
            "temperature": 1.0,
        },
        verbose=verbose,
    )

    chain_dfs = []
    message = None
    for i in range(args.chain_length):
        # Check if this step is already completed
        if existing_df is not None:
            mask = (existing_df["chain_id"] == chain_num) & (
                existing_df["chain_pos"] == i
            )
            if mask.any():
                print(f"Skipping chain {chain_num} pos {i} (already completed)")
                step_df = existing_df[mask].copy()
                chain_dfs.append(step_df)

                # Retrieve message for next step
                messages = step_df[step_df["message"].notna()]["message"]
                if not messages.empty:
                    message = messages.iloc[0]
                continue

        message, df_gameplay = await agent.play_games(
            num_rounds=args.num_rounds, incoming_message=message, verbose=True
        )
        df_gameplay["chain_id"] = chain_num
        df_gameplay["chain_pos"] = i
        chain_dfs.append(df_gameplay)

        # Save checkpoint
        async with file_lock:
            header = not os.path.exists(output_path)
            df_gameplay.to_csv(output_path, mode="a", header=header, index=False)

    print(f"Chain {chain_num} final message: {message}")
    return chain_dfs


async def run_simulations(args):
    output_path = here(f"{args.output_dir}/gameplay_{args.run_name}.csv")

    existing_df = None
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        try:
            existing_df = pd.read_csv(output_path)
            print(f"Loaded checkpoint from {output_path}")
        except Exception as e:
            print(f"Failed to load checkpoint: {e}")

    file_lock = asyncio.Lock()
    tasks = []
    for chain_num in range(args.num_chains):
        tasks.append(
            run_chain(
                args.descriptor,
                chain_num,
                args,
                output_path,
                file_lock,
                existing_df,
                verbose=args.verbose,
            )
        )

    results = await asyncio.gather(*tasks)

    # results is a list of lists of DataFrames (one list per chain)
    all_agent_dfs = [df for chain_dfs in results for df in chain_dfs]

    df_all_agents = pd.concat(all_agent_dfs)
    # Final save to ensure clean file (though checkpointing appended data)
    df_all_agents.to_csv(output_path, index=False)
    return df_all_agents


def compute_simulation_statistics(df_sims):
    df_scores = (
        df_sims[(df_sims["score"].notna()) & (df_sims["chain_pos"] == 0)]
        .sort_values("timestep")
        .groupby(["round_num", "chain_id"])
        .tail(1)
        .reset_index(drop=True)
    )

    # normalize the scores
    df_scores["score"] = df_scores["score"]

    ideal_learning_curve = pd.Series(
        np.linspace(0, 100, 10), index=range(10), name="ideal_score"
    )
    df_scores_with_ideal = df_scores.merge(
        ideal_learning_curve, left_on="round_num", right_index=True
    )

    # Calculate squared error for each individual score
    # Assuming max score is 100 based on previous context
    df_scores_with_ideal["squared_error"] = (
        df_scores_with_ideal["score"] - df_scores_with_ideal["ideal_score"]
    ) ** 2

    # get the scores by generation
    mean_sd_scores_by_round = df_scores.groupby("round_num")["score"].agg(
        ["mean", "std"]
    )
    # calculate the MSE with the average score in each round
    average_mse_per_round = (
        mean_sd_scores_by_round["mean"] - ideal_learning_curve
    ) ** 2
    average_mse = average_mse_per_round.mean()

    # compute the mean variance over rounds
    average_sd = mean_sd_scores_by_round["std"].mean()

    # fit a simple linear model to the scores and get the slope
    model = sm.OLS(
        df_scores["score"],
        sm.add_constant(df_scores["round_num"]),
    )
    model_res = model.fit()
    lm_results = f"intercept: {model_res.params['const']:.3f}, slope: {model_res.params['round_num']:.3f}, p_value: {model_res.pvalues['round_num']:.3f}"

    loss = average_mse + average_sd

    return {
        "loss": float(loss.round(3)),
        "average_mse": float(average_mse.round(3)),
        "average_sd": float(average_sd.round(3)),
        "average_mse_per_round": average_mse_per_round.round(3).to_dict(),
        "mean_scores_by_round": mean_sd_scores_by_round["mean"].round(3).to_dict(),
        "sd_scores_by_round": mean_sd_scores_by_round["std"].round(3).to_dict(),
        "linear_model_results": lm_results,
    }


def inspect_sample_round(df_sims, round_num):
    """
    Inspect a sample round to see the actions taken, the reasoning behind the actions, and the result.
    """
    df_round = df_sims[df_sims["round_num"] == round_num]
    sample_chain_id = df_round["chain_id"].sample(1).values[0]
    df_individual = df_round[df_round["chain_id"] == sample_chain_id].sort_values(
        "timestep"
    )
    ret = ""
    for i, row in df_individual.iterrows():
        action = json.loads(row["action"])
        ret += f"Timestep {int(row['timestep'])}\n---\n"
        ret += f"State: {row['state']}\n"
        ret += f"Reasoning: {action['reasoning']}\n"
        ret += f"Action: {action['action']}\n"
        ret += f"Score: {row['score']}\n\n"

    return ret
