from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset


@dataclass(frozen=True)
class SequenceSample:
    values: list[float]
    label: float


class EarSequenceDataset(Dataset):
    def __init__(self, samples: list[SequenceSample], seq_len: int) -> None:
        self._seq_len = seq_len
        self._samples = samples

    def __len__(self) -> int:
        return len(self._samples)

    def __getitem__(self, index: int):
        sample = self._samples[index]
        sequence = sample.values[: self._seq_len]
        if len(sequence) < self._seq_len:
            pad = [sequence[-1] if sequence else 0.0] * (self._seq_len - len(sequence))
            sequence = sequence + pad

        x = torch.tensor(sequence, dtype=torch.float32).unsqueeze(-1)
        y = torch.tensor([sample.label], dtype=torch.float32)
        return x, y


class LstmDrowsinessModel(nn.Module):
    def __init__(self, hidden_size: int = 32, num_layers: int = 1) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=1,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        return self.classifier(last)


def read_samples(csv_path: Path) -> list[SequenceSample]:
    grouped: dict[str, list[float]] = {}
    labels: dict[str, float] = {}

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"sequence_id", "timestep", "ear", "label"}
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError("CSV must include columns: sequence_id,timestep,ear,label")

        rows = list(reader)

    rows.sort(key=lambda r: (r["sequence_id"], int(r["timestep"])))
    for row in rows:
        seq_id = row["sequence_id"]
        grouped.setdefault(seq_id, []).append(float(row["ear"]))
        labels[seq_id] = float(row["label"])

    return [SequenceSample(values=v, label=labels[k]) for k, v in grouped.items()]


def split_samples(
    samples: list[SequenceSample], val_ratio: float
) -> tuple[list[SequenceSample], list[SequenceSample]]:
    shuffled = samples[:]
    random.shuffle(shuffled)
    val_size = max(1, int(len(shuffled) * val_ratio)) if len(shuffled) > 2 else 1
    return shuffled[val_size:], shuffled[:val_size]


def load_train_val_samples(
    csv_path: Path,
    train_csv_path: Path | None,
    val_csv_path: Path | None,
    val_ratio: float,
) -> tuple[list[SequenceSample], list[SequenceSample]]:
    if train_csv_path is not None and val_csv_path is not None:
        train_samples = read_samples(train_csv_path)
        val_samples = read_samples(val_csv_path)
        return train_samples, val_samples

    samples = read_samples(csv_path)
    if len(samples) < 4:
        raise ValueError("Need at least 4 sequences for train/val split")
    return split_samples(samples, val_ratio)


def eval_model(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            pred = model(x)
            pred_label = (pred >= 0.5).float()
            correct += int((pred_label == y).sum().item())
            total += y.numel()
    return correct / max(1, total)


def train(args) -> None:
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    train_csv_path = Path(args.train_csv) if args.train_csv else None
    val_csv_path = Path(args.val_csv) if args.val_csv else None
    train_samples, val_samples = load_train_val_samples(
        csv_path=Path(args.csv),
        train_csv_path=train_csv_path,
        val_csv_path=val_csv_path,
        val_ratio=args.val_ratio,
    )
    train_ds = EarSequenceDataset(train_samples, seq_len=args.seq_len)
    val_ds = EarSequenceDataset(val_samples, seq_len=args.seq_len)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LstmDrowsinessModel(
        hidden_size=args.hidden_size, num_layers=args.num_layers
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.BCELoss()

    best_acc = 0.0
    save_path = Path(args.output)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        for x, y in train_loader:
            x = x.to(device)
            y = y.to(device)

            optimizer.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item())

        val_acc = eval_model(model, val_loader, device)
        avg_loss = total_loss / max(1, len(train_loader))
        print(f"epoch={epoch} loss={avg_loss:.4f} val_acc={val_acc:.4f}")

        if val_acc >= best_acc:
            best_acc = val_acc
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "seq_len": args.seq_len,
                    "hidden_size": args.hidden_size,
                    "num_layers": args.num_layers,
                },
                save_path,
            )

    print(f"saved_best={save_path} best_val_acc={best_acc:.4f}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train LSTM drowsiness classifier from EAR sequences"
    )
    parser.add_argument(
        "--csv", required=True, help="Path to CSV with sequence_id,timestep,ear,label"
    )
    parser.add_argument("--train-csv", default=None, help="Optional train split CSV")
    parser.add_argument("--val-csv", default=None, help="Optional val split CSV")
    parser.add_argument(
        "--output",
        default="models/lstm_drowsiness.pt",
        help="Path to save best checkpoint",
    )
    parser.add_argument("--seq-len", type=int, default=16)
    parser.add_argument("--hidden-size", type=int, default=32)
    parser.add_argument("--num-layers", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser


if __name__ == "__main__":
    train(build_arg_parser().parse_args())
