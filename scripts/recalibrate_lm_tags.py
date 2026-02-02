"""
Recalibrate LM tag predictions using log-probability thresholds.
"""

from argparse import ArgumentParser

import numpy as np
import pandas as pd
from pyprojroot import here

TAG_FIELDS = [
    "abstractions",
    "concrete_recipes",
    "positive_valence",
    "negative_valence",
    "policy",
    "dynamics",
    "avoidance",
]


def _choose_threshold(x_train: np.ndarray, y_train: np.ndarray) -> float:
    unique_vals = np.unique(x_train)
    if unique_vals.size == 1:
        return unique_vals[0]

    thresholds = [unique_vals[0] - 1.0]
    thresholds += [
        (left + right) / 2.0 for left, right in zip(unique_vals[:-1], unique_vals[1:])
    ]
    thresholds.append(unique_vals[-1] + 1.0)

    best_threshold = thresholds[0]
    best_accuracy = -1.0
    for threshold in thresholds:
        preds = x_train >= threshold
        accuracy = (preds == y_train).mean()
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = threshold

    return best_threshold


def _loocv_thresholds(df: pd.DataFrame, tag: str) -> tuple[list[bool], list[float]]:
    logprob_col = f"{tag}_lm_logprob"
    y_values = df[tag].astype(bool).to_numpy()
    x_values = df[logprob_col].to_numpy()

    predictions = []
    thresholds = []
    for idx in range(len(df)):
        mask = np.ones(len(df), dtype=bool)
        mask[idx] = False
        x_train = x_values[mask]
        y_train = y_values[mask]

        threshold = _choose_threshold(x_train, y_train)
        thresholds.append(threshold)

        predictions.append(x_values[idx] >= threshold)

    return predictions, thresholds


def main(args):
    df_eval = pd.read_csv(here(args.eval_filepath))

    for tag in TAG_FIELDS:
        logprob_col = f"{tag}_lm_logprob"
        if logprob_col not in df_eval.columns:
            raise ValueError(
                f"Missing column '{logprob_col}'. Run lm_tagging first to compute log-probs."
            )

    for tag in TAG_FIELDS:
        preds, thresholds = _loocv_thresholds(df_eval, tag)
        df_eval[f"{tag}_lm_recalibrated"] = preds
        df_eval[f"{tag}_lm_threshold_loocv"] = thresholds
        df_eval[f"{tag}_lm_recalibrated_accuracy"] = (
            df_eval[tag].astype(bool) == df_eval[f"{tag}_lm_recalibrated"]
        )

    df_eval["recalibrated_all_tags_accuracy"] = df_eval[
        [f"{tag}_lm_recalibrated_accuracy" for tag in TAG_FIELDS]
    ].all(axis=1)

    print(
        df_eval[[f"{tag}_lm_recalibrated_accuracy" for tag in TAG_FIELDS]]
        .mean()
        .sort_values(ascending=False)
    )
    print("Overall accuracy:", df_eval["recalibrated_all_tags_accuracy"].mean())

    output_path = args.eval_filepath.replace(".csv", "_lm_recalibrated.csv")
    df_eval.to_csv(here(output_path), index=False)
    print(f"Wrote recalibrated results to {output_path}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--eval_filepath",
        type=str,
        default="data/human-data/experiment-1/processed/message-tags-eval_lm_tags.csv",
    )
    args = parser.parse_args()
    main(args)
