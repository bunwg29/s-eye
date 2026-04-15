# ML Workflow for S-Eye

This workflow upgrades S-Eye from classical EAR thresholding to sequence-based ML inference.

## 1. Collect labeled EAR data (recommended)

Run webcam collection with manual labels:

```powershell
python scripts/collect_labeled_ear.py --output logs/manual_labeled_ear.csv
```

Labeling controls in collection window:

- `0`: ALERT label
- `1`: DROWSY label
- `r`: toggle recording on/off
- `q`: quit

Convert collected log to training sequences:

```powershell
python scripts/build_sequences_from_runtime_log.py --input logs/manual_labeled_ear.csv --output data/ear_sequences.csv --window-size 16 --stride 4 --label-column is_drowsy
```

Create leakage-safe session split:

```powershell
python scripts/split_sequences_by_session.py --input data/ear_sequences.csv --out-dir data/splits --train-ratio 0.7 --val-ratio 0.15
```

## 2. Prepare EAR sequence dataset

Expected CSV format:

- `sequence_id`: unique sequence key
- `timestep`: integer order in each sequence
- `ear`: EAR value for this timestep
- `label`: `0` for alert, `1` for drowsy

Example:

```csv
sequence_id,timestep,ear,label
seq_001,0,0.28,0
seq_001,1,0.27,0
seq_002,0,0.14,1
```

You can start quickly with the bundled sample dataset:

```powershell
python scripts/train_lstm.py --csv data/sample_ear_sequences.csv --epochs 30
```

If you run the app in normal mode, EAR runtime logs are automatically saved to `logs/ear_runtime.csv`.
Convert those logs to sequence dataset with:

```powershell
python scripts/build_sequences_from_runtime_log.py --input logs/ear_runtime.csv --output data/ear_sequences.csv --window-size 16 --stride 4
```

## 3. Train LSTM baseline

Install ML dependencies first:

```powershell
pip install -e .[ml]
pip install torch
```

Run training:

```powershell
python scripts/train_lstm.py --csv data/ear_sequences.csv --output models/lstm_drowsiness.pt
```

Recommended (with session split):

```powershell
python scripts/train_lstm.py --csv data/ear_sequences.csv --train-csv data/splits/train.csv --val-csv data/splits/val.csv --output models/lstm_drowsiness.pt
```

## 4. Export ONNX model

```powershell
python scripts/export_lstm_onnx.py --checkpoint models/lstm_drowsiness.pt --output models/drowsiness.onnx
```

## 5. Enable ML mode in app config

In `src/shared/config.py`, set:

- `ml.enabled = True`
- `ml.model_path = "models/drowsiness.onnx"`

Run app and observe `P(drowsy)` in overlay.

## 6. Evaluate trained model

```powershell
python scripts/evaluate_lstm.py --checkpoint models/lstm_drowsiness.pt --csv data/splits/test.csv --threshold 0.5
```

This prints confusion matrix and metrics: precision, recall, F1, and accuracy.

## 7. Per-user calibration (demo stability)

Per-user calibration is enabled by default via `AppConfig.calibration`.
During the first 20 seconds, the app collects EAR samples and derives a personalized threshold.

You can tune in `src/shared/config.py`:

- `calibration.duration_seconds`
- `calibration.threshold_factor`
- `calibration.threshold_min`
- `calibration.threshold_max`
