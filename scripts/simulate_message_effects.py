"""
Simulate agents receiving different messages and see how well they do on the tasks.
"""

import asyncio
from argparse import ArgumentParser

import pandas as pd

from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.optimization.simulation import run_simulations

MESSAGES = {
    "none": {
        "animals": "I have no advice for you.",
        "cooking": "I have no advice for you.",
        "decorations": "I have no advice for you.",
        "potions": "I have no advice for you.",
    },
    "gold": {
        "animals": "Combine one animal of each habitat: air, land, and water. Before combining, you should use the growth serum once on large animals, twice on medium animals, and three times on small animals. The mutation catalyst makes animals worse the first time you use it but better the second time, so you should apply it to your combined animal twice.",
        "cooking": "Combine three items to get a score of 100: one grain, one vegetable, and one protein. Everything gets better when cooked with the stove once, but if you cook it more than once it becomes overcooked and loses value. You need to soak grains with water first before cooking them.",
        "decorations": "Soft items get better when cut with the scissors once. Hard items get worse when cut once but better when cut twice. For the best score, you should cut one natural and one artificial item correctly, then combine them. Finally, you should apply the frame. The frame has to go last because doing anything to an item after framing it will ruin the frame.",
        "potions": "A perfect potion has one magical ingredient and one mundane ingredient, so you should pick one of each type to combine. Before combining ingredients, you should use the vial on solid ingredients and the filter on liquid or gas ingredients. This will increase their value and turn them into liquids. Combining those liquids should get you a score of 100.",
    },
    "best_sender": {
        "animals": "Use growth until an animal gets to 15 before combining. Do not combine more than three animals. Mutate only twice after combining three animals.",
        "cooking": "cook things that would go together in real life, one at a time then combine. The stove is more successful.",
        "decorations": "Use 2 scissors on hard objects, 1 on soft. Then combine two and frame. Combine 2 natural soft then frame, or a natural soft and artificial hard for best results.",
        "potions": "Filter non-solids. Vial the solids. Combine the ones that seem more alike. One filtered non-solid, and one vial of solid added together becomes a higher score.",
    },
    "worst_sender": {
        "animals": "this is really hard to combine",
        "cooking": "it is hard",
        "decorations": "it is impossible to reach 80",
        "potions": "The vial and filter do not work together",
    },
    "best_receiver": {
        "animals": "You can individually get each creature high by doing mutant>growth>mutant>growth. After doing that you can combine up to 3 of them. I haven't figured out how to combine all 4.",
        "cooking": "Don't cook twice, 3 combinations at most for the highest score",
        "decorations": "You can only place ONE item in frame or it ruins the frame and you get a negative score.  So, place ribbons, sunflower, leaf or mushroom on top of frame by themselves.",
        "potions": "Filter non-solids. Vial the solids. Combine the ones that seem more alike.",
    },
    "worst_receiver": {
        "animals": "Avoid overly mutating combinations, sometimes two is alright. Focus more on growth, do three growths on combos of small animals, no more than one on those with two large animals.",
        "cooking": "You should not add stove and water together. And also raw food are best for the stove. Items may be 0, but when combined they could equal a higher score.",
        "decorations": "dont use frame",
        "potions": "Use your judgement to test each item with the vial or filter. Combine two that were successful, but lean away from combining mundane and magical items.",
    },
}


def main(args):
    df_all_sims = pd.DataFrame()
    for message_type in MESSAGES:
        for domain in MESSAGES[message_type]:
            args.descriptor = GAME_DESCRIPTORS[domain]
            args.starting_message = MESSAGES[message_type][domain]
            args.run_name = f"message_{message_type}_{domain}"
            df_sims = asyncio.run(run_simulations(args))
            df_sims["domain"] = domain
            df_sims["message_type"] = message_type
            df_all_sims = pd.concat([df_all_sims, df_sims])
            break
        break

    # compute the average scores in each simulation
    df_scores = (
        df_all_sims[(df_all_sims["score"].notna()) & (df_all_sims["chain_pos"] == 0)]
        .sort_values("timestep")
        .groupby(["round_num", "chain_id", "message_type", "domain"])
        .tail(1)
        .reset_index(drop=True)
    )

    # print mean scores by message type and domain
    print(df_scores.groupby(["message_type", "domain"])["score"].mean())


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
