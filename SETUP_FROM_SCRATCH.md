# AI-Based Blind Assistant - Complete Setup Guide from Scratch

This guide will walk you through setting up the AI-Based Blind Assistant system from scratch, whether you're using a laptop for development or deploying to a Raspberry Pi 5.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Setup](#hardware-setup)
3. [Software Installation](#software-installation)
4. [Project Setup](#project-setup)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Running the System](#running-the-system)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### For Development (Laptop/Desktop)

**Hardware:**
- Computer with Windows, Linux, or macOS
- Webcam (built-in or USB)
- Microphone and speakers/headphones
- Minimum 8GB RAM (16GB recommended)
- 10GB free disk space

**Software:**
- Python 3.9 or higher
- Git (optional, for version control)
- Internet connection

### For Production (Raspberry Pi 5)

**Hardware:**
- Raspberry Pi 5 (8GB RAM recommended)
- Pi Camera Module 3 (12MP with autofocus)
- GPS Module (NEO-6M or NEO-M8N)
- Bluetooth headset/earphones
- Power bank (20,000mAh+ for 6-8 hours)
- MicroSD card (64GB+ recommended)
- Optional: HC-SR04 ultrasonic sensors
- Optional: Vibration motors for haptic feedback

**Software:**
- Raspberry Pi OS (64-bit) - Latest version
- Internet connection for initial setup

---

## Hardware Setup

### Option A: Laptop Development Setup

1. **Verify Webcam**:
   - Open your camera app to ensure webcam works
   - Note the camera index (usually 0 for built-in)

2. **Test Microphone**:
   - Record a test audio to verify microphone works
   - Check audio settings for correct input device

3. **Test Speakers/Headphones**:
   - Play audio to verify output works

### Option B: Raspberry Pi 5 Setup

#### 1. Install Raspberry Pi OS

```bash
# Download Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# Flash Raspberry Pi OS (64-bit) to microSD card
# Enable SSH and configure WiFi during imaging
```

#### 2. Connect Hardware

**Pi Camera Module 3:**
```bash
# Connect camera ribbon cable to camera port
# Enable camera in raspi-config
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
```

**GPS Module (NEO-6M):**
```bash
# Connect GPS module to Raspberry Pi:
# VCC -> Pin 2 (5V)
# GND -> Pin 6 (Ground)
# TX  -> Pin 10 (GPIO 15 / RX)
# RX  -> Pin 8 (GPIO 14 / TX)

# Disable serial console
sudo raspi-config
# Navigate to: Interface Options > Serial Port
# Login shell: No
# Serial port hardware: Yes
```

**Ultrasonic Sensor (HC-SR04) - Optional:**
```bash
# Connect ultrasonic sensor:
# VCC  -> Pin 2 (5V)
# GND  -> Pin 6 (Ground)
# TRIG -> Pin 16 (GPIO 23)
# ECHO -> Pin 18 (GPIO 24)
```

**Vibration Motor - Optional:**
```bash
# Connect vibration motor:
# VCC -> Pin 12 (GPIO 18)
# GND -> Pin 14 (Ground)
```

#### 3. Initial Pi Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv git
sudo apt install -y libportaudio2 portaudio19-dev
sudo apt install -y tesseract-ocr
sudo apt install -y python3-opencv
sudo apt install -y gpsd gpsd-clients
```

---

## Software Installation

### Step 1: Install Python (if not already installed)

**Windows:**
```powershell
# Download Python from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
# Verify installation:
python --version
```

**Linux/macOS:**
```bash
# Python 3.9+ should be pre-installed
# Verify:
python3 --version

# If not installed:
# Ubuntu/Debian:
sudo apt install python3 python3-pip python3-venv

# macOS:
brew install python@3.11
```

**Raspberry Pi:**
```bash
# Python 3 is pre-installed
python3 --version
```

### Step 2: Clone or Download Project

**Option A: Using Git**
```bash
# Clone the repository (if hosted on GitHub)
git clone https://github.com/yourusername/blind-assistant.git
cd blind-assistant
```

**Option B: Manual Download**
```bash
# If you have the project folder already:
cd c:\Users\anush\OneDrive\Desktop\blind-assistant  # Windows
# OR
cd ~/blind-assistant  # Linux/macOS
```

### Step 3: Create Virtual Environment

**Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

**Linux/macOS/Raspberry Pi:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 4: Install Python Dependencies

**For Laptop (Windows/Linux/macOS):**
```bash
# Upgrade pip
pip install --upgrade pip

# Install PyTorch (CPU version for laptop)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install all other dependencies
pip install -r requirements.txt
```

**For Raspberry Pi:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install system packages first
sudo apt install -y python3-opencv python3-picamera2

# Install PyTorch for ARM
pip install torch torchvision torchaudio

# Install remaining dependencies
pip install -r requirements.txt

# Install Raspberry Pi specific packages
pip install RPi.GPIO gpiozero
```

> **Note**: Installation may take 15-30 minutes depending on your internet speed.

### Step 5: Download AI Models

The system will auto-download most models on first run, but you can pre-download them:

**Download Vosk Speech Model:**
```bash
# Create models directory
mkdir -p models

# Download Vosk model (English)
# Windows PowerShell:
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -OutFile "models/vosk-model.zip"
Expand-Archive -Path "models/vosk-model.zip" -DestinationPath "models/"

# Linux/macOS/Raspberry Pi:
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -P models/
unzip models/vosk-model-small-en-us-0.15.zip -d models/
```

**Other Models (Auto-downloaded):**
- YOLOv8: Downloads automatically on first use
- BLIP-2: Downloads from Hugging Face on first use
- MiDaS: Downloads from PyTorch Hub on first use

---

## Project Setup

### Step 1: Configure Environment Variables

```bash
# Copy environment template
# Windows:
copy .env.example .env

# Linux/macOS/Raspberry Pi:
cp .env.example .env
```

Edit `.env` file and add your API keys (optional):

```bash
# OpenAI API Key (for GPT-4o scene descriptions)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Maps API Key (for navigation)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Optional: Twilio for SMS emergency alerts
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Optional: Email for emergency alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

> **Note**: API keys are optional for testing. The system works offline without them.

### Step 2: Configure System Settings

Edit `config/config.yaml` to customize settings:

**For Laptop Development:**
```yaml
system:
  mode: "development"
  device: "laptop"

camera:
  resolution: [640, 480]  # Lower for faster processing
  fps: 15

scene_description:
  mode: "offline"  # Use BLIP-2 locally

object_detection:
  model: "yolov8n"  # Nano model for speed
```

**For Raspberry Pi:**
```yaml
system:
  mode: "production"
  device: "raspberry_pi"

camera:
  resolution: [1920, 1080]
  fps: 30
  auto_focus: true

scene_description:
  mode: "auto"  # Try online, fallback to offline

object_detection:
  model: "yolov8s"  # Small model for Pi 5
```

### Step 3: Create Data Directories

```bash
# Create necessary directories
mkdir -p data/logs
mkdir -p data/user_data/faces
mkdir -p models
```

---

## Configuration

### Essential Settings

Edit `config/config.yaml` for your use case:

#### 1. Voice Settings
```yaml
text_to_speech:
  engine: "pyttsx3"  # Offline TTS
  rate: 175          # Words per minute (adjust for comfort)
  volume: 1.0        # 0.0 to 1.0

speech_to_text:
  engine: "vosk"     # Offline STT
  language: "en-US"
```

#### 2. Emergency Contacts
```yaml
emergency_sos:
  enabled: true
  contacts:
    - name: "Emergency Contact 1"
      phone: "+1234567890"
      email: "emergency@example.com"
  trigger_phrase: "emergency help"
```

#### 3. Feature Toggles
```yaml
# Enable/disable features as needed
emotion_recognition:
  enabled: true

face_recognition:
  enabled: true

obstacle_detection:
  enabled: true  # Requires ultrasonic sensor

haptic_feedback:
  enabled: true  # Requires vibration motor
```

---

## Testing

### Step 1: Run System Test

```bash
# Activate virtual environment if not already active
# Windows:
venv\Scripts\activate
# Linux/macOS/Raspberry Pi:
source venv/bin/activate

# Run test script
python test_system.py
```

Expected output:
```
============================================================
AI-Based Blind Assistant - System Test
============================================================
Testing imports...
✓ Config loader
✓ Logger
✓ System Manager
✓ Command Processor
...
✅ All core modules imported successfully!

Testing configuration...
✓ Device: laptop
✓ Camera resolution: [640, 480]
✅ Configuration loaded successfully!

Testing camera...
✓ Captured image: (480, 640, 3)
✅ Camera test passed!

Testing text-to-speech...
Speaking test message...
✅ Text-to-speech test passed!

============================================================
Test Summary
============================================================
Imports: ✅ PASS
Configuration: ✅ PASS
Camera: ✅ PASS
Text-to-Speech: ✅ PASS

Total: 4/4 tests passed

🎉 All tests passed! System is ready to use.
```

### Step 2: Test Individual Components

**Test Camera:**
```python
python -c "
from src.hardware.camera_interface import CameraInterface
from src.utils.config_loader import get_config
import cv2

config = get_config()
camera = CameraInterface(config)
image = camera.capture()
print(f'Captured: {image.shape}')
cv2.imwrite('test_capture.jpg', image)
print('Saved to test_capture.jpg')
camera.release()
"
```

**Test Object Detection:**
```python
python -c "
from src.vision.object_detector import ObjectDetector
from src.hardware.camera_interface import CameraInterface
from src.utils.config_loader import get_config

config = get_config()
camera = CameraInterface(config)
detector = ObjectDetector(config)

image = camera.capture()
detections = detector.detect(image)
print(f'Detected {len(detections)} objects:')
for det in detections:
    print(f\"  - {det['class']}: {det['confidence']:.2f}\")

camera.release()
"
```

**Test Text-to-Speech:**
```python
python -c "
from src.audio.text_to_speech import TextToSpeech
from src.utils.config_loader import get_config

config = get_config()
tts = TextToSpeech(config)
tts.speak('Hello, this is a test of the blind assistant system.')
tts.shutdown()
"
```

---

## Running the System

### Start the Blind Assistant

```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/macOS/Raspberry Pi:
source venv/bin/activate

# Run the main application
python src/main.py
```

Expected startup output:
```
2026-02-01 12:00:00 - main - INFO - ============================================================
2026-02-01 12:00:00 - main - INFO - AI-Based Blind Assistant Starting...
2026-02-01 12:00:00 - main - INFO - ============================================================
2026-02-01 12:00:00 - SystemManager - INFO - Initializing system modules...
2026-02-01 12:00:00 - SystemManager - INFO - Initializing hardware modules...
2026-02-01 12:00:00 - CameraInterface - INFO - Initializing webcam...
2026-02-01 12:00:00 - CameraInterface - INFO - Webcam initialized successfully
...
2026-02-01 12:00:05 - SystemManager - INFO - All modules initialized successfully
2026-02-01 12:00:05 - main - INFO - System initialized successfully!
2026-02-01 12:00:05 - main - INFO - Blind Assistant is ready. Listening for commands...
```

### Voice Commands

Once running, try these commands:

| Command | Description |
|---------|-------------|
| "What do you see?" | Get detailed scene description |
| "Detect objects" | List objects with distances |
| "Read text" | Read text from camera view |
| "Where am I?" | Get GPS location |
| "Navigate to [place]" | Start navigation |
| "Who is this?" | Recognize person's face |
| "What color is this?" | Identify colors |
| "Emergency help" | Trigger SOS alert |
| "Stop" | Stop current action |

### Stopping the System

Press `Ctrl+C` to gracefully shutdown:
```
2026-02-01 12:30:00 - main - INFO - Shutdown signal received. Cleaning up...
2026-02-01 12:30:00 - SystemManager - INFO - Shutting down system...
2026-02-01 12:30:00 - SystemManager - INFO - System shutdown complete
2026-02-01 12:30:00 - main - INFO - Blind Assistant stopped
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'xyz'`

**Solution**:
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/macOS/Raspberry Pi:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Camera Not Working

**Problem**: `Failed to open webcam` or `No camera available`

**Solution**:
```bash
# Check camera permissions
# Windows: Settings > Privacy > Camera
# Linux: Check /dev/video0 exists
ls /dev/video*

# Try different camera index in config.yaml
camera:
  device: 1  # Try 0, 1, 2, etc.
```

**Raspberry Pi specific**:
```bash
# Enable camera
sudo raspi-config
# Interface Options > Camera > Enable

# Test camera
libcamera-hello
```

#### 3. Microphone Not Working

**Problem**: Speech recognition not responding

**Solution**:
```bash
# Windows: Check microphone permissions
# Settings > Privacy > Microphone

# Linux: Test microphone
arecord -l  # List recording devices
arecord -d 5 test.wav  # Record 5 seconds
aplay test.wav  # Play back

# Check config.yaml
speech_to_text:
  sample_rate: 16000  # Try 44100 if issues persist
```

#### 4. Slow Performance

**Problem**: System is too slow

**Solution**:
```yaml
# Edit config/config.yaml

# Use smaller models
object_detection:
  model: "yolov8n"  # Nano model

# Reduce resolution
camera:
  resolution: [320, 240]
  fps: 10

# Use offline mode
scene_description:
  mode: "offline"
```

#### 5. GPU Not Detected

**Problem**: Want to use GPU acceleration

**Solution**:
```bash
# Install CUDA-enabled PyTorch (if you have NVIDIA GPU)
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update config.yaml
object_detection:
  device: "cuda"
```

#### 6. GPS Not Working (Raspberry Pi)

**Problem**: GPS not getting fix

**Solution**:
```bash
# Check GPS connection
sudo cat /dev/ttyAMA0

# Start GPS daemon
sudo systemctl start gpsd
sudo systemctl enable gpsd

# Configure GPS daemon
sudo nano /etc/default/gpsd
# Set: DEVICES="/dev/ttyAMA0"

# Test GPS
cgps -s
```

#### 7. Out of Memory (Raspberry Pi)

**Problem**: System crashes with memory errors

**Solution**:
```yaml
# Edit config/config.yaml

# Disable some features
emotion_recognition:
  enabled: false

face_recognition:
  enabled: false

# Use smaller models
scene_description:
  offline_model: "blip2-base"  # Instead of large

# Reduce cache
performance:
  model_cache_size: 1
```

### Logs and Debugging

**Check logs:**
```bash
# View logs
cat data/logs/blind_assistant.log

# Follow logs in real-time
# Windows PowerShell:
Get-Content data/logs/blind_assistant.log -Wait -Tail 50

# Linux/macOS/Raspberry Pi:
tail -f data/logs/blind_assistant.log
```

**Enable debug mode:**
```yaml
# config/config.yaml
system:
  log_level: "DEBUG"  # More verbose logging
```

---

## Auto-Start on Boot (Raspberry Pi)

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/blind-assistant.service
```

Add this content:
```ini
[Unit]
Description=AI Blind Assistant
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/blind-assistant
Environment="PATH=/home/pi/blind-assistant/venv/bin"
ExecStart=/home/pi/blind-assistant/venv/bin/python /home/pi/blind-assistant/src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable blind-assistant

# Start service
sudo systemctl start blind-assistant

# Check status
sudo systemctl status blind-assistant

# View logs
sudo journalctl -u blind-assistant -f
```

---

## Performance Optimization

### For Raspberry Pi 5

**1. Increase GPU Memory:**
```bash
sudo nano /boot/config.txt
# Add or modify:
gpu_mem=256
```

**2. Overclock (optional, use with caution):**
```bash
sudo nano /boot/config.txt
# Add:
over_voltage=6
arm_freq=2400
```

**3. Disable Desktop (headless mode):**
```bash
sudo raspi-config
# System Options > Boot / Auto Login > Console
```

**4. Use Swap File:**
```bash
# Increase swap size
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## Next Steps

1. **Test all features** with voice commands
2. **Add known faces** for face recognition
3. **Configure emergency contacts**
4. **Customize voice settings** for comfort
5. **Deploy to Raspberry Pi** for portable use
6. **Conduct user testing** with target users

---

## Getting Help

- **Documentation**: See [README.md](README.md) for detailed info
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for fast setup
- **Logs**: Check `data/logs/blind_assistant.log`
- **Configuration**: Review `config/config.yaml`

---

## Summary Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Vosk model downloaded
- [ ] `.env` file configured (optional)
- [ ] `config/config.yaml` customized
- [ ] Test script passed (`python test_system.py`)
- [ ] System runs successfully (`python src/main.py`)
- [ ] Voice commands working
- [ ] Camera capturing images
- [ ] Audio feedback working

**Congratulations! Your AI-Based Blind Assistant is ready to use! 🎉**
