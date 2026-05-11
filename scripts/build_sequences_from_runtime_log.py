from __future__ import annotations

import argparse
import csv
from pathlib import Path


def load_rows(input_csv: Path) -> list[dict[str, str]]:
    with input_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"session_id", "frame_index", "ear", "is_drowsy"}
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError(
                "Input CSV must include: session_id,frame_index,ear,is_drowsy"
            )
        rows = list(reader)

    rows.sort(key=lambda r: (r["session_id"], int(r["frame_index"])))
    return rows


def build_sequences(
    rows: list[dict[str, str]],
    window_size: int,
    stride: int,
    label_column: str,
) -> list[tuple[str, int, float, int]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["session_id"], []).append(row)

    output_rows: list[tuple[str, int, float, int]] = []
    seq_counter = 0

    for session_id, samples in grouped.items():
        ears = [float(x["ear"]) for x in samples if x.get("ear") not in (None, "")]
        labels = [
            float(x[label_column]) for x in samples if x.get("ear") not in (None, "")
        ]
        n = len(ears)
        if n < window_size:
            continue

        for start in range(0, n - window_size + 1, stride):
            end = start + window_size
            seq_ears = ears[start:end]
            seq_labels = labels[start:end]
            seq_label = 1 if (sum(seq_labels) / max(1, len(seq_labels))) >= 0.5 else 0
            sequence_id = f"{session_id}_seq_{seq_counter:05d}"
            for t, ear in enumerate(seq_ears):
                output_rows.append((sequence_id, t, ear, seq_label))
            seq_counter += 1

    return output_rows


def write_output(output_csv: Path, rows: list[tuple[str, int, float, int]]) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sequence_id", "timestep", "ear", "label"])
        for row in rows:
            writer.writerow(row)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert runtime EAR log to training sequence CSV"
    )
    parser.add_argument("--input", default="logs/ear_runtime.csv")
    parser.add_argument("--output", default="data/ear_sequences.csv")
    parser.add_argument("--window-size", type=int, default=16)
    parser.add_argument("--stride", type=int, default=4)
    parser.add_argument("--label-column", default="is_drowsy")
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    rows = load_rows(Path(args.input))
    seq_rows = build_sequences(
        rows=rows,
        window_size=max(2, int(args.window_size)),
        stride=max(1, int(args.stride)),
        label_column=args.label_column,
    )
    write_output(Path(args.output), seq_rows)
    print(f"sequences={len(seq_rows)} output={args.output}")
