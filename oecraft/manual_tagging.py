"""
Code for tagging messages.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import pandas as pd

TAG_FIELDS = [
    ("abstractions", "Does it have abstractions?"),
    ("concrete_recipes", "Does it have concrete recipes?"),
    ("positive_valence", "Does it have positively-valenced information?"),
    (
        "negative_valence",
        "Does it have negatively-valenced information?",
    ),
    ("policy", "Does it talk about policy (what people should do)?"),
    ("dynamics", "Does it talk about dynamics (how the world works)?"),
    ("avoidance", "Does it talk about avoidance (what to avoid)?"),
]

BASE_FIELDS = [
    "message_id",
    "trial_id",
    "participant_id",
    "chain_id",
    "domain",
    "chain_pos",
    "condition",
    "message",
]

OUTPUT_FIELDS = BASE_FIELDS + [field for field, _ in TAG_FIELDS]


class TagCommand:
    QUIT = "quit"
    SKIP = "skip"


def _normalize_response(raw: str) -> str | None:
    text = raw.strip().lower()
    if text in {"q", "quit", "exit"}:
        return TagCommand.QUIT
    if text in {"s", "skip"}:
        return TagCommand.SKIP
    if text in {"y", "yes", "1", "true", "t"}:
        return "1"
    if text in {"n", "no", "0", "false", "f"}:
        return "0"
    return None


def _prompt_yes_no(prompt: str) -> str:
    while True:
        raw = input(f"{prompt} [y/n/s/q]: ")
        normalized = _normalize_response(raw)
        if normalized is not None:
            return normalized
        print("Please enter y/n, s to skip, or q to quit.")


def _resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def _load_messages(input_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    df = df.reset_index().rename(columns={"index": "message_id"})
    return df


def _load_existing_tag_ids(output_path: Path) -> set[int]:
    if not output_path.exists():
        return set()
    tagged_ids: set[int] = set()
    with output_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            message_id = row.get("message_id")
            if message_id is None:
                continue
            try:
                tagged_ids.add(int(message_id))
            except ValueError:
                continue
    return tagged_ids


def _load_selection_ids(selection_path: Path) -> list[int]:
    if not selection_path.exists():
        return []
    selection: list[int] = []
    with selection_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            message_id = row.get("message_id")
            if message_id is None:
                continue
            try:
                selection.append(int(message_id))
            except ValueError:
                continue
    return selection


def _save_selection_ids(selection_path: Path, message_ids: list[int]) -> None:
    _ensure_parent_dir(selection_path)
    with selection_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["message_id"])
        writer.writeheader()
        for message_id in message_ids:
            writer.writerow({"message_id": message_id})


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _rewrite_with_fields(output_path: Path, fieldnames: list[str]) -> None:
    if not output_path.exists():
        return
    with output_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _ensure_output_schema(output_path: Path) -> None:
    if not output_path.exists():
        return
    with output_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        existing_fields = reader.fieldnames or []
    if any(field not in existing_fields for field in OUTPUT_FIELDS):
        _rewrite_with_fields(output_path, OUTPUT_FIELDS)


def _append_tag_row(output_path: Path, row: dict) -> None:
    _ensure_parent_dir(output_path)
    file_exists = output_path.exists()
    if file_exists:
        _ensure_output_schema(output_path)

    with output_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _format_message_intro(row: pd.Series, index: int, total: int) -> str:
    return (
        f"\n[{index}/{total}] domain={row.get('domain')} "
        f"trial_id={row.get('trial_id')} participant_id={row.get('participant_id')} "
        f"condition={row.get('condition')}"
    )


def run_cli(args: argparse.Namespace) -> int:
    input_path = _resolve_path(args.input)
    output_path = _resolve_path(args.output)
    selection_path = _resolve_path(args.selection_file)

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1

    df = _load_messages(input_path)
    df_by_id = df.set_index("message_id", drop=False)
    _ensure_output_schema(output_path)
    tagged_ids = _load_existing_tag_ids(output_path)

    rng = random.Random(args.seed)
    selection_ids = [] if args.reset_selection else _load_selection_ids(selection_path)
    if not selection_ids:
        available_ids = [int(mid) for mid in df_by_id.index if mid not in tagged_ids]
        if not available_ids:
            print("No untagged messages found. You're done.")
            return 0
        if args.shuffle:
            rng.shuffle(available_ids)
        if args.count > len(available_ids):
            print(
                "Requested selection is larger than available untagged messages: "
                f"{args.count} requested, {len(available_ids)} available."
            )
            return 1
        selection_ids = available_ids[: args.count]
        _save_selection_ids(selection_path, selection_ids)
        print(f"Saved selection of {len(selection_ids)} messages to {selection_path}.")

    missing_ids = [mid for mid in selection_ids if mid not in df_by_id.index]
    if missing_ids:
        print(
            "Warning: selection contains message_ids not in the input file. "
            "They will be skipped."
        )

    pending_ids = [mid for mid in selection_ids if mid not in tagged_ids]
    if not pending_ids:
        print("All messages in the selection are already tagged. You're done.")
        return 0

    print(
        f"Tagging {len(pending_ids)} messages from selection of "
        f"{len(selection_ids)}. Output: {output_path}"
    )

    tagged_count = 0
    for position, message_id in enumerate(pending_ids, start=1):
        if message_id not in df_by_id.index:
            continue
        row = df_by_id.loc[message_id]
        print(_format_message_intro(row, position, len(pending_ids)))
        print("-" * 80)
        print(row.get("message", ""))
        print("-" * 80)

        tags: dict[str, str] = {}
        skip_message = False
        for field, prompt in TAG_FIELDS:
            response = _prompt_yes_no(prompt)
            if response == TagCommand.QUIT:
                print("Exiting. Progress saved.")
                return 0
            if response == TagCommand.SKIP:
                skip_message = True
                break
            tags[field] = response

        if skip_message:
            print("Message skipped.")
            continue

        output_row = {
            "message_id": int(row["message_id"]),
            "trial_id": row.get("trial_id"),
            "participant_id": row.get("participant_id"),
            "chain_id": row.get("chain_id"),
            "domain": row.get("domain"),
            "chain_pos": row.get("chain_pos"),
            "condition": row.get("condition"),
            "message": row.get("message"),
            **tags,
        }
        _append_tag_row(output_path, output_row)
        tagged_count += 1
        print(f"Saved ({tagged_count} tagged so far).")

    print(f"Done. Tagged {tagged_count} messages.")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manual CLI for tagging human messages."
    )
    parser.add_argument(
        "--input",
        default="data/human-data/experiment-1/processed/messages.csv",
        help="Path to messages CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/human-data/experiment-1/processed/message-tags.csv",
        help="Path to output tags CSV.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of messages to select for tagging.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2026,
        help="Random seed for shuffling.",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle before selecting messages.",
    )
    parser.add_argument(
        "--selection-file",
        default="data/human-data/experiment-1/processed/message-tagging-selection.csv",
        help="CSV file that stores the fixed selection of message_ids.",
    )
    parser.add_argument(
        "--reset-selection",
        action="store_true",
        help="Ignore any existing selection file and create a new selection.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
