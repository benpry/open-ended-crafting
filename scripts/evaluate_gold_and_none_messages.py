"""
Evaluate the gold and none messages in experiment 2.
"""

import asyncio
from argparse import ArgumentParser

from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.optimization.simulation import run_simulations

MESSAGES = {
    "gold": {
        "animals": "Combine one animal of each habitat: air, land, and water. Before combining, you should use the growth serum once on large animals, twice on medium animals, and three times on small animals. The mutation catalyst makes animals worse the first time you use it but better the second time, so you should apply it to your combined animal twice. This will get you a score of 100.",
        "cooking": "Combine three items to get a score of 100: one grain, one vegetable, and one protein. Everything gets better when cooked with the stove once, but if you cook it more than once it becomes overcooked and loses value. You need to soak grains with water first before cooking them.",
        "decorations": "Soft items get better when cut with the scissors once. Hard items get worse when cut once but better when cut twice. For a score of 100 you should cut one natural and one artificial item correctly, then combine them. Finally, you should apply the frame. The frame has to go last because doing anything to an item after framing it will ruin the frame.",
        "potions": "A perfect potion has one magical ingredient and one mundane ingredient, so you should pick one of each type to combine. Before combining ingredients, you should use the vial on solid ingredients and the filter on liquid or gas ingredients. This will increase their value and turn them into liquids. Combining those liquids will get you a score of 100.",
    },
    "none": {
        "animals": "There is no message for you to read.",
        "cooking": "There is no message for you to read.",
        "decorations": "There is no message for you to read.",
        "potions": "There is no message for you to read.",
    },
}


def main(args):
    for message_type in MESSAGES:
        for domain in MESSAGES[message_type]:
            args.descriptor = GAME_DESCRIPTORS[domain]
            args.starting_message = MESSAGES[message_type][domain]
            args.run_name = f"message_{message_type}_{domain}"
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
