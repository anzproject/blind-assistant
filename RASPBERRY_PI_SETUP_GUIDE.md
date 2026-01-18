# Step-by-Step Guide: Running AI Blind Assistant on Raspberry Pi 5

## Prerequisites
- **Hardware**: Raspberry Pi 5 (8GB RAM recommended), Pi Camera Module 3, GPS module (NEO-6M), Bluetooth headset, Power bank (10000mAh+)
- **Software**: Raspberry Pi OS (64-bit, Bookworm or later)
- **Network**: Internet connection for initial setup

---

## Step 1: Initial Raspberry Pi Setup

### 1.1 Install Raspberry Pi OS
1. Download Raspberry Pi Imager from raspberrypi.com
2. Choose Raspberry Pi OS (64-bit) → Bookworm
3. Flash to microSD card
4. Boot Raspberry Pi and complete initial setup

### 1.2 System Update
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git vim
```

### 1.3 Enable Required Interfaces
```bash
sudo raspi-config
```
- **Interface Options**:
  - Camera: Enable
  - SSH: Enable
  - VNC: Enable (optional)
  - Serial Port: Enable (for GPS)
  - Bluetooth: Enable

---

## Step 2: Hardware Connections

### 2.1 Camera Setup
1. Connect Pi Camera Module 3 to CSI port
2. Verify connection:
```bash
vcgencmd get_camera
# Should show: supported=1 detected=1
```

### 2.2 GPS Module Setup
1. Connect GPS module to UART pins (GPIO 14/15)
2. Install GPS software:
```bash
sudo apt install -y gpsd gpsd-clients
```

### 2.3 Bluetooth Headset
1. Pair your Bluetooth headset:
```bash
bluetoothctl
# In bluetoothctl:
scan on
# Wait for your device to appear
pair <MAC_ADDRESS>
connect <MAC_ADDRESS>
trust <MAC_ADDRESS>
exit
```

---

## Step 3: Project Installation

### 3.1 Clone and Setup Project
```bash
cd ~
git clone <your-repository-url> blind-assistant
cd blind-assistant

# Create virtual environment
python3 -m venv blind_assistant_env
source blind_assistant_env/bin/activate
```

### 3.2 Install Dependencies
```bash
# Install system packages
sudo apt install -y libportaudio2 libasound2-dev libatlas-base-dev
sudo apt install -y tesseract-ocr tesseract-ocr-eng
sudo apt install -y libgtk-3-0 libgstreamer1.0-0 libgstreamer-plugins-base1.0-0

# Install Python packages
pip install -r requirements.txt
```

---

## Step 4: Download AI Models

### 4.1 Create Models Directory
```bash
mkdir -p models
cd models
```

### 4.2 Download Required Models
```bash
# Vosk STT Model (English)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 vosk-model-small-en-us-0.15

# YOLOv5 Object Detection Model
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt

# BLIP Image Captioning Model
pip install transformers
python -c "
from transformers import BlipProcessor, BlipForConditionalGeneration
processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
processor.save_pretrained('./blip-image-captioning-base')
model.save_pretrained('./blip-image-captioning-base')
"
```

---

## Step 5: Hardware Configuration

### 5.1 GPS Configuration
```bash
# Configure GPS device
sudo nano /etc/default/gpsd
# Change DEVICES to:
DEVICES="/dev/ttyS0"
GPSD_OPTIONS="-n"

# Restart GPS service
sudo systemctl restart gpsd
sudo systemctl enable gpsd

# Test GPS
gpsmon /dev/ttyS0
```

### 5.2 Camera Testing
```bash
cd ~/blind-assistant
python scripts/setup_camera.py
```

### 5.3 Bluetooth Testing
```bash
python scripts/setup_bluetooth.py <your_headset_mac_address>
```

---

## Step 6: Configuration

### 6.1 Edit Configuration File
```bash
nano config.py
```

Update settings as needed:
```python
# Hardware settings
CAMERA_DEVICE = 0
GPS_DEVICE = "/dev/ttyS0"
BLUETOOTH_DEVICE = "your_headset_mac"

# Model paths
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"
YOLO_MODEL_PATH = "models/yolov5s.pt"
BLIP_MODEL_PATH = "models/blip-image-captioning-base"

# Voice settings
VOICE_RATE = 180
VOICE_VOLUME = 0.8
```

---

## Step 7: Testing

### 7.1 Test Individual Components
```bash
cd ~/blind-assistant
source blind_assistant_env/bin/activate

# Test camera
python -c "from modules.camera import CameraHandler; cam = CameraHandler(); print('Camera OK' if cam.test() else 'Camera Failed')"

# Test audio
python -c "from modules.audio import AudioProcessor; audio = AudioProcessor(); audio.speak('Audio test'); print('Audio OK')"

# Test GPS
python -c "from modules.gps import GPSHandler; gps = GPSHandler(); print('GPS OK' if gps.test() else 'GPS Failed')"
```

### 7.2 Run Unit Tests
```bash
python -m pytest tests/ -v
```

---

## Step 8: Running the Application

### 8.1 Direct Execution
```bash
cd ~/blind-assistant
source blind_assistant_env/bin/activate
python main.py
```

### 8.2 Web GUI Setup (Optional)
```bash
# Run web interface for configuration
python web_gui.py &
# Access from laptop: http://raspberry-pi-ip:5000
```

### 8.3 Docker Deployment (Alternative)
```bash
# Build and run with Docker
sudo docker build -t blind-assistant .
sudo docker run --privileged \
  --device /dev/video0 \
  --device /dev/ttyS0 \
  --device /dev/bluetooth \
  -p 5000:5000 \
  blind-assistant
```

---

## Step 9: Voice Commands

Once running, use these voice commands:
- **"Describe scene"** - Get scene description
- **"Read text"** - OCR text recognition
- **"Detect objects"** - Object detection
- **"Where am I"** - GPS location
- **"Guide me to [location]"** - Navigation
- **"Help"** - Show available commands
- **"Stop"** - Exit application

---

## Step 10: Troubleshooting

### Common Issues:

#### Camera Not Working
```bash
# Check camera connection
vcgencmd get_camera
raspistill -o test.jpg
```

#### GPS Not Getting Fix
```bash
# Check GPS device
ls /dev/tty*
gpsmon /dev/ttyS0
```

#### Audio Problems
```bash
# Test audio output
speaker-test -c2 -t wav
# Check Bluetooth audio
pactl list sinks
```

#### Permission Issues
```bash
# Add user to required groups
sudo usermod -a -G video,bluetooth,gpio,tty $USER
# Reboot required
```

#### Memory Issues
```bash
# Monitor memory usage
htop
# Free up memory if needed
sudo apt autoremove
```

---

## Step 11: Auto-Start on Boot (Optional)

### 11.1 Create Service File
```bash
sudo nano /etc/systemd/system/blind-assistant.service
```

Add content:
```ini
[Unit]
Description=AI Blind Assistant
After=network.target gpsd.service bluetooth.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/blind-assistant
ExecStart=/home/pi/blind_assistant_env/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 11.2 Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable blind-assistant
sudo systemctl start blind-assistant
sudo systemctl status blind-assistant
```

---

## Step 12: Maintenance

### Regular Updates
```bash
cd ~/blind-assistant
source blind_assistant_env/bin/activate
git pull
pip install -r requirements.txt --upgrade
```

### Log Monitoring
```bash
# View application logs
tail -f logs/blind_assistant.log

# System logs
journalctl -u blind-assistant
```

---

## Quick Start Checklist

- [ ] Raspberry Pi OS installed and updated
- [ ] Camera, GPS, Bluetooth hardware connected
- [ ] Interfaces enabled in raspi-config
- [ ] Project cloned and virtual environment created
- [ ] Dependencies installed
- [ ] AI models downloaded
- [ ] Hardware configured and tested
- [ ] Configuration file updated
- [ ] Individual components tested
- [ ] Application runs successfully
- [ ] Voice commands work
- [ ] Auto-start configured (optional)

---

## Support

If you encounter issues:
1. Check the DEPLOYMENT.md file for detailed troubleshooting
2. Verify hardware connections
3. Test individual components
4. Check logs in `logs/` directory
5. Ensure all dependencies are installed

The assistant is now ready to help visually impaired users with AI-powered scene understanding, navigation, and daily tasks!
