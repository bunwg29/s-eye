# S-Eye: Project Setup & Running Guide

**S-Eye** is a driver drowsiness detection system using computer vision and machine learning. It analyzes Eye Aspect Ratio (EAR) from a webcam and uses an LSTM model to classify driver state (alert vs. drowsy).

## 📋 System Requirements

- **OS**: Windows 7+
- **Python**: 3.11+ (recommended 3.11, avoid 3.14 due to NumPy DLL issues on Windows)
- **Camera**: Webcam or USB camera
- **RAM**: Minimum 4GB

## 🚀 Initial Setup

### 1. Open Project Directory
```bash
cd d:\Projects\s-eye
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.\.venv\Scripts\activate.bat
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Install Project in Development Mode
```bash
pip install -e .
```

## ▶️ Running the Application

### Method 1: PowerShell Script (Recommended)
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

### Method 2: Direct Python Execution
```bash
python -m src.main
```

## 📊 Application Workflow

1. **System Initialization** (~2 seconds)
   - Load ML model (ONNX format)
   - Connect to camera
   - Auto-select camera backend: `dshow` → `msmf` → auto

2. **Calibration Phase** (20 seconds)
   - ❌ **NO ALARM SOUND** during this phase
   - System collects EAR data to calculate personal threshold
   - Keep eyes open naturally
   - Displays: `[S-Eye] Calibration complete. samples=XXX threshold=Y.YY`

3. **Drowsiness Detection** (continuous after calibration)
   - System tracks EAR from camera feed
   - LSTM model predicts drowsiness probability
   - Alarm triggers if probability > 50%

4. **Exit Application**
   - Press `Q` or close camera window

## 🎯 Alert Behavior

### When Drowsiness Detected:
- 🔊 Continuous beeping sound (~0.75 seconds interval)
- ⏱️ Alert holds for minimum **2 seconds** even if eyes open briefly
- 👁️ Alert **STOPS** only after **3 consecutive frames** with open eyes

### When Eyes Fully Closed:
- Alarm continues uninterrupted
- Stops when eyes detected open again

## 🔧 Configuration

Main config file: `src/shared/config.py`

### Key Parameters:

```python
# ML Configuration
ml.enabled = True                                  # Enable/disable ML mode
ml.model_path = "models/drowsiness.onnx"         # Model path
ml.drowsy_probability_threshold = 0.50            # Probability threshold (0.5 = 50%)
ml.sequence_length = 16                           # Number of frames for LSTM

# Calibration
calibration.duration_seconds = 20                 # Calibration time (seconds)

# Alert Behavior
min_alert_hold_seconds = 2.0                      # Minimum alert duration (seconds)
reopen_eye_frames_required = 3                    # Frames needed to stop alert

# Camera
camera.backend_preference = "dshow,msmf,any"     # Camera backend preference
camera.camera_index = 0                           # Camera index (0 = default)
```

## 🧪 Running Unit Tests

```bash
# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_process_frame.py -v

# Quick test (quiet mode)
pytest -q
```

## 📁 Project Structure

```
s-eye/
├── src/                              # Main source code
│   ├── main.py                       # Entry point
│   ├── core/                         # Business logic (Clean Architecture)
│   │   ├── application/              # Use cases
│   │   │   ├── use_cases/
│   │   │   │   └── process_frame.py # Frame processing state machine
│   │   │   └── ports/               # Interfaces
│   │   ├── domain/                   # Entities & Services
│   │   │   ├── entities/
│   │   │   │   └── driver_state.py  # Driver state tracking
│   │   │   ├── services/
│   │   │   │   └── drowsiness_rules.py # EAR computation
│   │   │   └── value_objects/
│   │   │       └── eye_landmarks.py
│   ├── infrastructure/               # Technical implementations
│   │   ├── camera/
│   │   │   └── opencv_camera.py     # Backend selection (dshow/msmf)
│   │   ├── vision/
│   │   │   ├── manual_eye_detector.py # Haar cascade + temporal smoothing
│   │   │   └── preprocess.py         # Image preprocessing
│   │   ├── audio/
│   │   │   └── system_alarm.py       # Windows winsound alarm
│   │   └── ml/
│   │       └── onnx_drowsiness_classifier.py # ONNX Runtime inference
│   ├── presentation/
│   │   └── cli/
│   │       └── monitor_loop.py       # Main execution loop
│   └── shared/
│       └── config.py                  # Global configuration
├── tests/                             # Unit tests
│   ├── conftest.py
│   └── unit/
│       ├── test_drowsiness_rules.py
│       └── test_process_frame.py
├── models/
│   └── drowsiness.onnx               # Exported LSTM model
├── scripts/
│   ├── run_dev.ps1                   # PowerShell run script
│   └── run_dev.cmd                   # CMD run script
├── docs/
│   └── ARCHITECTURE.md               # Detailed architecture
├── pyproject.toml                    # Project configuration
├── requirements.txt                  # Dependencies
└── README.md
```

## 🐛 Common Troubleshooting

### 1. Error: `ImportError: DLL load failed while importing _umath_linalg`
**Cause**: Python 3.14+ has NumPy compatibility issues on Windows (App Control policy)
**Solution**:
- Upgrade to Python 3.11
- Or whitelist NumPy DLL in Windows App Control settings

### 2. Error: `Cannot be loaded because running scripts is disabled`
**Cause**: ExecutionPolicy restriction
**Solution**:
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

### 3. Error: `Camera not found` or `Cannot open video capture`
**Cause**: Camera in use or driver issue
**Solution**:
- Check Device Manager for camera presence
- Close other apps using camera (Zoom, Teams, OBS, etc.)
- Try changing `camera.backend_preference` in config.py

### 4. False Alarms When Eyes Are Open
**Cause**: Calibration threshold too low
**Solution**:
- Restart application for recalibration
- Or adjust `ml.drowsy_probability_threshold` to 0.55-0.60

### 5. No Alert Sound
**Cause**: May be in calibration phase (first 20 seconds)
**Solution**:
- Wait until `[S-Eye] Calibration complete` appears
- Check Windows volume settings
- Verify `alarm_enabled` parameter in code

## 📈 Performance Metrics

- **FPS**: 25-30 FPS (depends on camera)
- **Latency**: ~100ms from frame to alert
- **ML Accuracy**: 81.75% (validation set from 3 sessions)
- **RAM Usage**: ~200-300MB

## 🔐 Privacy & Security

- All video processing is local only
- No internet connectivity required
- Calibration data stored in memory only (not persisted)

## 📚 Additional Resources

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed architecture documentation
- [Idea.md](Idea.md) - Original project concept
- [README.md](README.md) - Project overview

## ❓ FAQ

**Q: How can I improve accuracy?**
A:
- Ensure good camera positioning and lighting
- Allow full 20-second calibration period
- If needed, retrain model with new data sessions

**Q: Can I disable the alarm sound?**
A: Set `alarm_enabled = False` or comment out trigger call in `system_alarm.py`

**Q: Why is alarm delayed compared to when I close my eyes?**
A: Processing latency (~100ms) + need 16 frames accumulated for LSTM

**Q: Can I integrate with other applications?**
A: Yes. Modify `monitor_loop.py` to decouple from `SystemAlarm` and integrate your notification system.

**Q: What's the difference between Python versions?**
A: Python 3.11+ is stable. 3.14+ has NumPy DLL issues on Windows with certain security policies.

---

**Version**: 0.1.0  
**Last Updated**: April 2026  
**Project**: S-Eye Drowsiness Detection System
