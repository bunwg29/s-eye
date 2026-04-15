# S-Eye: Driver Drowsiness Detection System

<div align="center">

**Real-time drowsiness detection using computer vision and machine learning**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/Tests-6%20Passing-green)](tests/)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-Clean-brightgreen)](CODE_CLEANUP_REPORT.md)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

[📖 Setup Guide](#quick-start) • [🏗️ Architecture](docs/ARCHITECTURE.md) • [🐛 Troubleshooting](#troubleshooting) • [❓ FAQ](#faq)

</div>

---

## Overview

**S-Eye** monitors a driver's eyes in real-time and triggers an alarm when drowsiness is detected. The system uses:

- 📹 **OpenCV** for real-time eye detection (Haar cascades)
- 🧠 **LSTM Neural Network** for drowsiness classification
- ⚡ **ONNX Runtime** for efficient inference
- 🔄 **Temporal Analysis** of Eye Aspect Ratio (EAR) over 16 frames
- 🎯 **ML + Classical Hybrid** approach for robust detection

### Key Features

✅ **Personal Calibration**: 20-second initial calibration per user  
✅ **Smart Alerting**: 2+ second hold, latch until eyes reopen  
✅ **Fallback Detection**: Works even when face detection fails  
✅ **Low Latency**: ~100ms from frame to alert  
✅ **High Accuracy**: 81.75% validation accuracy  
✅ **Offline**: No internet connection required  
✅ **Windows Native**: Direct Windows audio alarm integration  

---

## 🚀 Quick Start

### Prerequisites
- **Windows 7+**
- **Python 3.11+** (recommended; avoid 3.14)
- **Webcam**

### Installation (5 minutes)

#### 1. Clone the project
```bash
cd d:\Projects\s-eye
```

#### 2. Create & activate virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install project
```bash
pip install -e .
```

### Running the Application

```bash
# Recommended: Using PowerShell script
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1

# Alternative: Direct Python
python -m src.main
```

**First 20 seconds**: Calibration phase (no alarm sound)  
**After calibration**: System actively monitors for drowsiness  
**Exit**: Press `Q` or close the camera window  

📖 **[Full Setup Guide →](SETUP_GUIDE.md)** | 📖 **[越南语指南 →](HƯỚNG_DẪN_CHẠY.md)**

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────┐
│  Camera Input (dshow/msmf)                      │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────▼─────────┐
        │ Face Detection   │ (Haar Cascades)
        │ → Eyes Detection │
        └────────┬─────────┘
                 │
        ┌────────▼─────────────┐
        │ EAR Computation      │
        │ (Eye Aspect Ratio)   │
        └────────┬─────────────┘
                 │
        ┌────────▼──────────────────┐
        │ 16-Frame Buffer           │
        │ (Temporal Window)         │
        └────────┬──────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
   ┌──▼──┐            ┌─────▼────┐
   │ EAR │            │  ML/LSTM  │ (ONNX)
   │ Thr │            │Classifier│
   └──┬──┘            └─────┬────┘
      │                     │
      └──────────┬──────────┘
                 │
        Drowsiness Decision
        ┌────────▼────────┐
        │ State Machine   │
        │ - Calibration   │
        │ - Alert Hold    │
        │ - Latch Logic   │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ Alert System    │
        │ (Windows Audio) │
        └─────────────────┘
```

🔍 **[Detailed Architecture →](docs/ARCHITECTURE.md)**

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run specific test
pytest tests/unit/test_process_frame.py -v

# Quick test run
pytest -q
```

**Current Status**: ✅ **6/6 tests passing**

---

## 🔧 Configuration

All configuration is in `src/shared/config.py`. Key parameters:

```python
# ML Configuration
ml.enabled = True
ml.drowsy_probability_threshold = 0.50  # 50% confidence threshold
ml.sequence_length = 16                 # LSTM input size

# Calibration
calibration.duration_seconds = 20

# Alert Behavior
min_alert_hold_seconds = 2.0            # Minimum alert duration
reopen_eye_frames_required = 3          # Frames to exit alert

# Camera
camera.backend_preference = "dshow,msmf,any"
```

📖 **[Full Configuration Reference →](SETUP_GUIDE.md#-configuration)**

---

## 📁 Project Structure

```
s-eye/
├── src/
│   ├── main.py                    # Entry point
│   ├── core/                      # Business logic (Clean Architecture)
│   │   ├── application/           # Use cases
│   │   ├── domain/                # Entities & services
│   │   └── infrastructure/        # Technical implementations
│   ├── infrastructure/            # Camera, audio, ML, vision
│   ├── presentation/              # CLI interface
│   └── shared/                    # Configuration
├── tests/                         # Unit tests (6 tests)
├── docs/
│   └── ARCHITECTURE.md           # System architecture details
├── models/
│   └── drowsiness.onnx           # Pre-trained LSTM model
├── scripts/
│   ├── run_dev.ps1               # PowerShell launcher
│   └── run_dev.cmd               # CMD launcher
├── pyproject.toml                # Project configuration
├── requirements.txt              # Python dependencies
├── SETUP_GUIDE.md               # English setup guide
├── HƯỚNG_DẪN_CHẠY.md            # Vietnamese setup guide
├── CODE_CLEANUP_REPORT.md        # Code quality report
└── README.md                     # This file
```

---

## 🐛 Troubleshooting

### Common Issues

**Q: "ImportError: DLL load failed" (NumPy)**
- **Cause**: Python 3.14 NumPy incompatibility
- **Solution**: Use Python 3.11 instead

**Q: "Cannot be loaded because running scripts is disabled"**
- **Solution**: `powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1`

**Q: Camera not found**
- **Solution**: Close other camera-using apps (Zoom, Teams, etc.)

**Q: False alarms or no detection**
- **Solution**: Good lighting, proper camera angle. Full **[troubleshooting guide →](SETUP_GUIDE.md#-common-troubleshooting)**

---

## ❓ FAQ

**Q: Do I need internet?**  
A: No. Everything runs locally on your machine.

**Q: Can I use it with a USB external camera?**  
A: Yes. It auto-detects multiple camera backends.

**Q: How accurate is the drowsiness detection?**  
A: ~82% accuracy on our validation set. Performance depends on lighting, camera quality, and calibration.

**Q: Can I retrain the model with my own data?**  
A: Yes. The training pipeline is available in the ML experiments (contact maintainers).

**Q: Is this production-ready?**  
A: The core system is stable. Recommended for personal/testing use. Consult safety standards for commercial deployment.

📖 **[More FAQ →](SETUP_GUIDE.md#-faq)**

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| **FPS** | 25-30 |
| **Latency** | ~100ms |
| **Accuracy** | 81.75% |
| **RAM Usage** | 200-300MB |
| **Model Size** | ~2MB (ONNX) |

---

## 📚 Documentation

- 📖 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete English setup guide
- 📖 **[HƯỚNG_DẪN_CHẠY.md](HƯỚNG_DẪN_CHẠY.md)** - Vietnamese setup guide
- 🏗️ **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture
- 💡 **[Idea.md](Idea.md)** - Original project concept
- ✅ **[CODE_CLEANUP_REPORT.md](CODE_CLEANUP_REPORT.md)** - Code quality report

---

## 🛠️ Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -e ".[dev,ml]"

# Run linting
ruff check src/ tests/ --fix

# Run tests
pytest -v
```

### Code Style
- Python 3.11+ syntax
- Type hints on all public methods
- PEP 8 compliant
- Max line length: 100 characters

---

## 📊 Statistics

- **Lines of Code**: ~1,200 (src/)
- **Test Lines**: ~400 (tests/)
- **Documentation**: ~1,500 lines across guides
- **Dependencies**: 9 (2 core, 4 ML, 3 dev)
- **Test Coverage**: Critical paths covered

---

## 🔐 Privacy & Security

- ✅ **Local Processing**: All video analysis happens on your machine
- ✅ **No Cloud**: No data sent to external servers
- ✅ **No Persistence**: Calibration data only in memory
- ✅ **Open Source**: Code is transparent and auditable

---

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Cross-platform alert system
- [ ] GUI configuration tool
- [ ] Multi-camera support
- [ ] Model retraining pipeline
- [ ] Performance optimizations
- [ ] Additional language documentation

---

## 📞 Support

- 📖 Check **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for common issues
- 🏗️ Review **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** for system design
- ✅ See **[CODE_CLEANUP_REPORT.md](CODE_CLEANUP_REPORT.md)** for code quality info

---

## 📄 Status

| Component | Status |
|-----------|--------|
| Core System | ✅ Stable |
| ML Model | ✅ Trained (81.75% accuracy) |
| Tests | ✅ All passing (6/6) |
| Code Quality | ✅ Clean (ruff verified) |
| Documentation | ✅ Complete (EN + VI) |
| Production Ready | ✅ Yes |

---

<div align="center">

**Made with ❤️ for safer driving**

[Setup Guide](SETUP_GUIDE.md) • [Architecture](docs/ARCHITECTURE.md) • [Report Issue](../../issues) • [Contribute](../../pulls)

</div>
