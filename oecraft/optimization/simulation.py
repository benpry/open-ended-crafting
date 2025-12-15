"""
Set up an agent in the crafting game and run it.
"""

import asyncio
import os

import numpy as np
import pandas as pd
from pyprojroot import here

from oecraft.agents.lm_agent import CraftingAgent
from oecraft.environment import CraftingGame, LMCraftingGame


async def run_chain(
    descriptor, chain_num, args, output_path, file_lock, existing_df=None
):
    # Create independent environment and agent for each chain
    game = CraftingGame(
        descriptor=descriptor, model=args.naming_model, assign_names=True
    )
    env = LMCraftingGame(game)
    agent = CraftingAgent(
        env,
        model=args.agent_model,
        api_base_url=args.api_base_url,
        generate_kwargs={
            "top_p": 0.95,
            "temperature": 1.0,
        },
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
    agent_model_name = args.agent_model.replace("/", "--")
    output_path = here(
        f"{args.output_dir}/gameplay_{agent_model_name}_{args.sim_name}.csv"
    )

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
                args.descriptor, chain_num, args, output_path, file_lock, existing_df
            )
        )

    results = await asyncio.gather(*tasks)

    # results is a list of lists of DataFrames (one list per chain)
    all_agent_dfs = [df for chain_dfs in results for df in chain_dfs]

    df_all_agents = pd.concat(all_agent_dfs)
    # Final save to ensure clean file (though checkpointing appended data)
    df_all_agents.to_csv(output_path, index=False)
    return df_all_agents


def evaluate_simulations(df: pd.DataFrame):
    # compute summary statistics for the simulation
    df_scores = (
        df[df["score"].notna()]
        .sort_values("timestep")
        .groupby(["chain_id", "chain_pos", "round_num"], as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )
    average_by_round_num = df_scores.groupby("round_num")["score"].mean() / 100
    print(f"average_by_round_num: {average_by_round_num}")

    # measure the MSE between the average score by round number and a line that goes from 0 to 100
    optimal_scores = np.linspace(0, 1, len(average_by_round_num))
    print(f"optimal_scores: {optimal_scores}")
    mse = np.mean((average_by_round_num - optimal_scores) ** 2)

    # line of best fit:
    best_fit = np.polyfit(range(len(average_by_round_num)), average_by_round_num, 1)

    return {
        "mse": mse,
        "best_fit": best_fit,
    }
