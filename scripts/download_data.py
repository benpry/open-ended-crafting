import os
from argparse import ArgumentParser

import pandas as pd
import pymongo
from pyprojroot import here


def get_players(db: pymongo.database.Database):
    players = db["players"].find()
    rows = []
    for player in players:
        del player["_id"]
        # del player["prolific_id"]
        rows.append(player)
    return pd.DataFrame(rows)


def get_trials(db: pymongo.database.Database):
    trials = db["trials"].find()
    rows = []
    for trial in trials:
        del trial["_id"]
        rows.append(trial)
    return pd.DataFrame(rows)


def get_messages(db: pymongo.database.Database):
    messages = db["messages"].find()
    rows = []
    for message in messages:
        del message["_id"]
        rows.append(message)
    return pd.DataFrame(rows)


def get_surveys(db: pymongo.database.Database):
    surveys = db["surveys"].find()
    rows = []
    for survey in surveys:
        del survey["_id"]
        for question in survey["questions"]:
            rows.append(
                {
                    "player_id": survey["player_id"],
                    "question": question["question"],
                    "answer": question["answer"],
                }
            )
    return pd.DataFrame(rows)


def main(args):
    client = pymongo.MongoClient(args.mongo_uri)
    db = client["crafting"]

    df_players = get_players(db)
    df_trials = get_trials(db)
    df_messages = get_messages(db)
    df_surveys = get_surveys(db)

    os.makedirs(here(args.output_dir), exist_ok=True)
    df_players.to_csv(here(args.output_dir) / "players.csv", index=False)
    df_trials.to_csv(here(args.output_dir) / "trials.csv", index=False)
    df_messages.to_csv(here(args.output_dir) / "messages.csv", index=False)
    df_surveys.to_csv(here(args.output_dir) / "surveys.csv", index=False)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--output_dir", type=str, default="data/human-data")
    parser.add_argument("--mongo_uri", type=str, default="mongodb://localhost:27017")
    args = parser.parse_args()
    main(args)
