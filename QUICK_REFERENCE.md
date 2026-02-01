# AI-Based Blind Assistant - Quick Reference Card

## 🚀 Quick Start Commands

### First Time Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate (Windows)
venv\Scripts\activate
# OR Activate (Linux/Mac/Pi)
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test system
python test_system.py

# 5. Run assistant
python src/main.py
```

## 🎤 Voice Commands

| Command | Action |
|---------|--------|
| "What do you see?" | Scene description |
| "Detect objects" | Object detection + distances |
| "Read text" | OCR text reading |
| "Where am I?" | GPS location |
| "Navigate to [place]" | Start navigation |
| "Who is this?" | Face recognition |
| "What emotion?" | Emotion detection |
| "What color is this?" | Color identification |
| "Identify currency" | Currency recognition |
| "Emergency help" | Trigger SOS |
| "Stop" | Stop current action |

## 📁 Project Structure

```
blind-assistant/
├── config/config.yaml      # Main configuration
├── src/                    # Source code
│   ├── core/              # System manager, commands
│   ├── vision/            # AI vision modules
│   ├── audio/             # Speech & TTS
│   ├── navigation/        # GPS & routing
│   ├── hardware/          # Hardware interfaces
│   └── utils/             # Utilities
├── data/                   # User data & logs
├── models/                 # AI models
└── tests/                  # Test files
```

## ⚙️ Key Configuration Files

**Main Config**: `config/config.yaml`
- Camera settings
- Model selection
- Feature toggles
- Voice settings

**Environment**: `.env`
- API keys (OpenAI, Google Maps)
- Emergency contact info

## 🔧 Common Configurations

### Fast Performance (Laptop)
```yaml
object_detection:
  model: "yolov8n"
camera:
  resolution: [640, 480]
  fps: 15
scene_description:
  mode: "offline"
```

### Best Quality (Raspberry Pi 5)
```yaml
object_detection:
  model: "yolov8s"
camera:
  resolution: [1920, 1080]
  fps: 30
scene_description:
  mode: "auto"
```

## 🐛 Troubleshooting

### Camera Issues
```bash
# Check camera
ls /dev/video*  # Linux/Pi
# Try different index in config.yaml
```

### Microphone Issues
```bash
# Test microphone
arecord -d 5 test.wav  # Linux/Pi
aplay test.wav
```

### Check Logs
```bash
# View logs
cat data/logs/blind_assistant.log

# Follow logs
tail -f data/logs/blind_assistant.log  # Linux/Mac/Pi
Get-Content data/logs/blind_assistant.log -Wait  # Windows
```

### Performance Issues
- Use smaller models (yolov8n)
- Lower camera resolution
- Disable unused features
- Use offline mode

## 📚 Documentation

- **Complete Setup**: `SETUP_FROM_SCRATCH.md`
- **Quick Start**: `QUICKSTART.md`
- **Full Documentation**: `README.md`
- **Implementation Details**: See walkthrough artifact

## 🔑 Important Paths

**Logs**: `data/logs/blind_assistant.log`
**Config**: `config/config.yaml`
**Environment**: `.env`
**Models**: `models/`
**User Data**: `data/user_data/`

## 🎯 Testing Individual Components

```python
# Test camera
python -c "from src.hardware.camera_interface import CameraInterface; from src.utils.config_loader import get_config; c = CameraInterface(get_config()); print(c.capture().shape)"

# Test TTS
python -c "from src.audio.text_to_speech import TextToSpeech; from src.utils.config_loader import get_config; t = TextToSpeech(get_config()); t.speak('Test')"

# Test object detection
python -c "from src.vision.object_detector import ObjectDetector; from src.utils.config_loader import get_config; print('Detector loaded')"
```

## 🚨 Emergency Features

**Trigger SOS**: Say "emergency help"
**Configure Contacts**: Edit `config/config.yaml`
```yaml
emergency_sos:
  contacts:
    - name: "Contact Name"
      phone: "+1234567890"
      email: "email@example.com"
```

## 🔄 Update/Reinstall

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Reinstall from scratch
rm -rf venv  # Linux/Mac/Pi
Remove-Item -Recurse venv  # Windows
python -m venv venv
# Then activate and install
```

## 📊 System Requirements

**Minimum (Laptop)**:
- Python 3.9+
- 8GB RAM
- Webcam
- Microphone

**Recommended (Raspberry Pi 5)**:
- 8GB RAM
- Pi Camera Module 3
- GPS Module
- 20,000mAh power bank

## 🎓 For Final Year Project

**Key Features to Demonstrate**:
1. Real-time object detection
2. Scene description (online/offline)
3. Voice command interface
4. GPS navigation
5. Face/emotion recognition
6. Emergency SOS system
7. Multi-modal AI integration

**Academic Contributions**:
- Hybrid cloud-edge architecture
- Context-aware assistance
- Multi-sensory feedback
- Accessibility-first design

---

**Need Help?** Check the full documentation in `SETUP_FROM_SCRATCH.md`
