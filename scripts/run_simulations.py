import asyncio
from argparse import ArgumentParser

from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.optimization.simulation import (
    compute_simulation_statistics,
    run_simulations,
)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--domain", type=str, default="potions")
    parser.add_argument("--naming_model", type=str, default="openai/gpt-oss-20b")
    parser.add_argument("--agent_model", type=str, default="gemini-2.5-flash")
    parser.add_argument("--num-rounds", type=int, default=5)
    parser.add_argument("--num-chains", type=int, default=3)
    parser.add_argument("--chain-length", type=int, default=1)
    parser.add_argument("--output-dir", type=str, default="data/simulations")
    parser.add_argument("--verbose", type=bool, default=True)

    args = parser.parse_args()
    args.descriptor = GAME_DESCRIPTORS[args.domain]
    args.run_name = f"{args.domain}_num_chains-{args.num_chains}_chain_length-{args.chain_length}_num_rounds-{args.num_rounds}"
    df_sims = asyncio.run(run_simulations(args))
    eval_results = compute_simulation_statistics(df_sims)

    print(eval_results)
