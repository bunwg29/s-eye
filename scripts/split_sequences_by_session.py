from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def _session_key(sequence_id: str) -> str:
    if "_seq_" in sequence_id:
        return sequence_id.split("_seq_", 1)[0]
    return sequence_id


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"sequence_id", "timestep", "ear", "label"}
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError("Input CSV must include: sequence_id,timestep,ear,label")
        return list(reader)


def _split_sessions(
    session_ids: list[str],
    train_ratio: float,
    val_ratio: float,
    seed: int,
) -> tuple[set[str], set[str], set[str]]:
    random.seed(seed)
    items = sorted(set(session_ids))
    random.shuffle(items)

    total = len(items)
    if total < 3:
        raise ValueError("Need at least 3 sessions to create train/val/test split")

    train_n = max(1, int(total * train_ratio))
    val_n = max(1, int(total * val_ratio))
    if train_n + val_n >= total:
        val_n = max(1, total - train_n - 1)

    train_set = set(items[:train_n])
    val_set = set(items[train_n : train_n + val_n])
    test_set = set(items[train_n + val_n :])

    if not test_set:
        last = val_set.pop()
        test_set.add(last)

    return train_set, val_set, test_set


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sequence_id", "timestep", "ear", "label"])
        writer.writeheader()
        writer.writerows(rows)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Split sequence CSV by session into train/val/test"
    )
    parser.add_argument("--input", default="data/ear_sequences.csv")
    parser.add_argument("--out-dir", default="data/splits")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input)
    out_dir = Path(args.out_dir)

    rows = _load_rows(input_path)
    session_ids = [_session_key(r["sequence_id"]) for r in rows]
    train_sessions, val_sessions, test_sessions = _split_sessions(
        session_ids,
        train_ratio=float(args.train_ratio),
        val_ratio=float(args.val_ratio),
        seed=int(args.seed),
    )

    train_rows: list[dict[str, str]] = []
    val_rows: list[dict[str, str]] = []
    test_rows: list[dict[str, str]] = []

    for row in rows:
        s = _session_key(row["sequence_id"])
        if s in train_sessions:
            train_rows.append(row)
        elif s in val_sessions:
            val_rows.append(row)
        else:
            test_rows.append(row)

    _write_rows(out_dir / "train.csv", train_rows)
    _write_rows(out_dir / "val.csv", val_rows)
    _write_rows(out_dir / "test.csv", test_rows)

    print(
        f"sessions train/val/test = {len(train_sessions)}/{len(val_sessions)}/{len(test_sessions)}"
    )
    print(f"rows train/val/test = {len(train_rows)}/{len(val_rows)}/{len(test_rows)}")
    print(f"written={out_dir}")


if __name__ == "__main__":
    main()
