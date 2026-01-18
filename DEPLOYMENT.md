# Deployment Guide for AI Blind Assistant

## System Requirements

### Hardware Requirements
- **Raspberry Pi 5** (4GB RAM minimum, 8GB recommended)
- **Pi Camera Module 3** or compatible camera
- **GPS Module** (e.g., NEO-6M with UART interface)
- **Bluetooth Headset/Earphones** (for audio I/O)
- **Power Bank** (10000mAh minimum for portability)
- **Laptop** (for initial setup and web GUI access)

### Software Requirements
- **Raspberry Pi OS** (64-bit, Bookworm or later)
- **Python 3.9+**
- **Camera permissions** configured
- **Bluetooth services** enabled

## Installation Steps

### 1. Initial Raspberry Pi Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3-pip python3-venv git
sudo apt install -y libportaudio2 libasound2-dev libatlas-base-dev
sudo apt install -y tesseract-ocr tesseract-ocr-eng
sudo apt install -y bluetooth bluez gpsd gpsd-clients
sudo apt install -y libgtk-3-0 libgstreamer1.0-0 libgstreamer-plugins-base1.0-0
```

### 2. Clone and Setup Project

```bash
# Clone repository
git clone <repository-url>
cd blind-assistant

# Create virtual environment
python3 -m venv blind_assistant_env
source blind_assistant_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Hardware Configuration

#### Camera Setup
```bash
# Run camera setup script
python scripts/setup_camera.py
```

#### GPS Setup
```bash
# Configure GPS device
sudo nano /etc/default/gpsd
# Add: DEVICES="/dev/ttyS0"  # Adjust device path as needed
# Add: GPSD_OPTIONS="-n"

# Restart GPS service
sudo systemctl restart gpsd
sudo systemctl enable gpsd

# Test GPS
python scripts/setup_gps.py
```

#### Bluetooth Setup
```bash
# Enable Bluetooth
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Run Bluetooth setup
python scripts/setup_bluetooth.py <device_address>
```

### 4. Model Downloads

```bash
# Download required ML models
python scripts/download_models.py

# Expected models directory structure:
models/
├── vosk-model-small-en-us-0.15/
├── yolov5s.pt
├── blip-image-captioning-base/
└── emotion-recognition-model/
```

### 5. Configuration

```bash
# Edit configuration file
nano config.py

# Adjust settings as needed:
# - Model paths
# - Hardware device addresses
# - Voice settings
# - GPS parameters
```

### 6. Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Test individual components
python -c "from modules.camera import CameraHandler; cam = CameraHandler(); print('Camera OK' if cam.test() else 'Camera Failed')"
python -c "from modules.audio import AudioProcessor; audio = AudioProcessor(); audio.speak('Audio test')"
```

### 7. Running the Application

#### Direct Execution
```bash
# Activate virtual environment
source blind_assistant_env/bin/activate

# Run main application
python main.py
```

#### Web GUI Setup
```bash
# Start web interface for configuration
python web_gui.py

# Access from laptop: http://raspberry-pi-ip:5000
```

#### Docker Deployment (Alternative)
```bash
# Build Docker image
docker build -t blind-assistant .

# Run container with device access
docker run --privileged \
  --device /dev/video0 \
  --device /dev/ttyS0 \
  --device /dev/bluetooth \
  -p 5000:5000 \
  blind-assistant
```

## Usage Instructions

### Voice Commands
- "Describe scene" - Get scene description
- "Read text" - OCR text recognition
- "Detect objects" - Object detection
- "Where am I" - GPS location
- "Guide me to [location]" - Navigation
- "Help" - Show available commands
- "Stop" - Exit application

### Web Interface
- Access configuration and testing interface
- Adjust voice settings, camera parameters
- Monitor system status
- Test individual components

## Troubleshooting

### Common Issues

#### Camera Not Working
```bash
# Check camera connection
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera access
raspistill -o test.jpg
```

#### GPS Not Getting Fix
```bash
# Check GPS device
ls /dev/tty*
gpsmon /dev/ttyS0

# Verify GPS service
sudo systemctl status gpsd
```

#### Bluetooth Connection Issues
```bash
# Scan for devices
bluetoothctl scan on

# Pair device
bluetoothctl pair <MAC_ADDRESS>
bluetoothctl connect <MAC_ADDRESS>
```

#### Audio Problems
```bash
# Test audio output
speaker-test -c2 -t wav

# Check Bluetooth audio
pactl list sinks
```

### Performance Optimization

#### For Raspberry Pi 5
- Use TensorFlow Lite models for better performance
- Reduce camera resolution if needed: `config.py`
- Enable GPU acceleration where possible
- Monitor CPU temperature: `vcgencmd measure_temp`

#### Memory Management
- Close camera streams when not in use
- Use model quantization for smaller footprint
- Implement model caching

## Maintenance

### Regular Updates
```bash
# Update system and dependencies
sudo apt update && sudo apt upgrade
pip install -r requirements.txt --upgrade

# Update models if needed
python scripts/download_models.py --update
```

### Log Monitoring
```bash
# View application logs
tail -f logs/blind_assistant.log

# Check system logs
journalctl -u gpsd
journalctl -u bluetooth
```

### Backup Configuration
```bash
# Backup user settings
cp config.py config_backup.py
cp -r models models_backup
```

## Safety Considerations

- Always test in controlled environments first
- Ensure GPS accuracy before relying on navigation
- Have manual controls available
- Regular battery checks for power bank
- Emergency stop commands always available

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review troubleshooting section above
3. Test individual components
4. Check hardware connections
5. Update to latest versions

## Advanced Configuration

### Custom Voice Commands
Edit `modules/audio.py` to add new commands in `process_voice_command()` method.

### Additional Sensors
Integrate new sensors by creating new modules following the existing pattern.

### Model Customization
Replace models in `models/` directory and update paths in `config.py`.
