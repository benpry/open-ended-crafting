"""
Run models on both variants of the potions game.
"""

import asyncio
from argparse import ArgumentParser

from oecraft.game_descriptors import POTIONS_VARIANT_DESCRIPTORS
from oecraft.optimization.simulation import run_simulations


def main(args):
    for variant in POTIONS_VARIANT_DESCRIPTORS:
        args.descriptor = POTIONS_VARIANT_DESCRIPTORS[variant]
        args.run_name = variant
        asyncio.run(run_simulations(args))


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--naming_model", type=str, default="openai/gpt-oss-20b")
    parser.add_argument("--agent_model", type=str, default="gemini-2.5-flash")
    parser.add_argument("--num-rounds", type=int, default=5)
    parser.add_argument("--num-chains", type=int, default=10)
    parser.add_argument("--chain-length", type=int, default=1)
    parser.add_argument("--output-dir", type=str, default="data/simulations")
    parser.add_argument("--verbose", type=bool, default=False)

    args = parser.parse_args()

    main(args)
