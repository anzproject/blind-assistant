# AI-Based Blind Assistant 🦯🤖

A comprehensive AI-powered assistive system for visually impaired individuals, built as a final year computer science engineering project. This system combines advanced computer vision, natural language processing, GPS navigation, and voice interaction to provide real-time environmental awareness and assistance.

## 🌟 Features

### Core Features
- **Object Detection**: Real-time object detection using YOLOv8/v9 with distance estimation
- **Scene Description**: Detailed scene descriptions using GPT-4o (online) or BLIP-2 (offline)
- **OCR Text Reading**: Extract and read text from images using EasyOCR/Tesseract
- **Voice Commands**: Natural voice interaction with speech-to-text and text-to-speech
- **GPS Navigation**: Turn-by-turn navigation with route guidance
- **Emotion Recognition**: Detect facial emotions in social situations
- **Face Recognition**: Recognize familiar people

### Novel Features (Final Year Project Enhancements)
- **Currency Recognition**: Identify currency denominations
- **Color Identification**: Identify dominant colors in objects
- **Context-Aware Assistance**: Adapts behavior based on context (shopping, navigation, social)
- **Emergency SOS**: Emergency alert system with GPS location sharing
- **Obstacle Detection**: Ultrasonic sensor-based obstacle avoidance with haptic feedback
- **Personalized Learning**: Learns user preferences and frequently visited locations
- **Multi-Language Support**: Supports multiple languages for TTS, STT, and OCR
- **Offline Mode**: Works without internet using local AI models

## 🛠️ Hardware Requirements

### Required Components
- **Raspberry Pi 5** (8GB RAM recommended)
- **Pi Camera Module 3** (12MP with autofocus)
- **GPS Module** (NEO-6M or NEO-M8N)
- **Bluetooth Headset/Earphones**
- **Power Bank** (20,000mAh+ for 6-8 hours operation)

### Optional Components
- **Ultrasonic Sensors** (HC-SR04) for obstacle detection
- **Vibration Motors** for haptic feedback
- **Physical Emergency Button**

## 📋 Software Requirements

### Operating System
- Raspberry Pi OS (64-bit) for Pi deployment
- Windows/Linux/macOS for development

### Python Version
- Python 3.9 or higher

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/blind-assistant.git
cd blind-assistant
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac/Raspberry Pi
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

#### For Development (Laptop)
```bash
pip install -r requirements.txt
```

#### For Raspberry Pi
```bash
# Install system dependencies first
sudo apt-get update
sudo apt-get install -y python3-opencv python3-picamera2 tesseract-ocr portaudio19-dev

# Install Python packages
pip install -r requirements.txt
```

### 4. Download AI Models

The system will automatically download required models on first run, but you can pre-download them:

```bash
# YOLOv8 (will auto-download)
# BLIP-2 (will auto-download from Hugging Face)
# Vosk speech model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/
```

### 5. Configure API Keys

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 6. Configure System

Edit `config/config.yaml` to customize settings:
- Camera resolution and FPS
- Model selection (online/offline)
- Voice settings
- Feature toggles

## 🎯 Usage

### Running on Laptop (Development)
```bash
python src/main.py
```

### Running on Raspberry Pi
```bash
# Set device to raspberry_pi in config.yaml
python3 src/main.py
```

### Voice Commands

Once the system starts, you can use these voice commands:

- **"What do you see?"** - Get a detailed scene description
- **"Detect objects"** - List objects in view with distances
- **"Read text"** - Read text from the camera view
- **"Where am I?"** - Get current GPS location
- **"Navigate to [place]"** - Start navigation to a destination
- **"Who is this?"** - Recognize a person's face
- **"What color is this?"** - Identify colors
- **"Identify currency"** - Recognize currency denomination
- **"Emergency help"** - Trigger emergency SOS

## 📁 Project Structure

```
blind-assistant/
├── config/                 # Configuration files
│   └── config.yaml        # Main configuration
├── src/
│   ├── core/              # Core system components
│   │   ├── system_manager.py
│   │   └── command_processor.py
│   ├── vision/            # Computer vision modules
│   │   ├── object_detector.py
│   │   ├── scene_describer.py
│   │   ├── ocr_engine.py
│   │   └── distance_estimator.py
│   ├── audio/             # Audio processing
│   │   ├── speech_to_text.py
│   │   ├── text_to_speech.py
│   │   └── audio_manager.py
│   ├── navigation/        # GPS and navigation
│   │   ├── gps_module.py
│   │   └── navigation_engine.py
│   ├── hardware/          # Hardware interfaces
│   │   ├── camera_interface.py
│   │   ├── gps_interface.py
│   │   └── bluetooth_manager.py
│   └── utils/             # Utility functions
│       ├── logger.py
│       └── config_loader.py
├── models/                # AI models (downloaded)
├── data/                  # User data and logs
├── tests/                 # Unit and integration tests
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🧪 Testing

Run unit tests:
```bash
pytest tests/unit/ -v
```

Run integration tests:
```bash
pytest tests/integration/ -v
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 🔧 Configuration

### Switching Between Online and Offline Modes

Edit `config/config.yaml`:

```yaml
scene_description:
  mode: "auto"  # Options: online, offline, auto
```

- **online**: Uses GPT-4o (requires API key and internet)
- **offline**: Uses BLIP-2 (runs locally, no internet needed)
- **auto**: Tries online first, falls back to offline

### Adjusting Voice Settings

```yaml
text_to_speech:
  engine: "pyttsx3"  # Options: pyttsx3, gtts
  rate: 175          # Words per minute
  volume: 1.0        # 0.0 to 1.0
```

## 🎓 Academic Context

This project is designed as a **final year computer science engineering project** with the following academic contributions:

1. **Multi-Modal AI Integration**: Combines vision, audio, and GPS for comprehensive assistance
2. **Hybrid Architecture**: Seamless online/offline operation for reliability
3. **Context-Aware Computing**: Adapts behavior based on user activity
4. **Edge AI Optimization**: Runs advanced AI models on resource-constrained devices
5. **Accessibility-First Design**: Entirely voice-controlled interface

### Potential Research Areas
- Real-time object detection optimization on edge devices
- Hybrid cloud-edge AI architectures
- Context-aware assistive systems
- Multi-sensory feedback mechanisms

## 📊 Performance Benchmarks

### On Raspberry Pi 5 (8GB)
- Object Detection: ~5-10 FPS (YOLOv8n)
- Scene Description (offline): ~3-5 seconds per image
- OCR: ~1-2 seconds per image
- Voice Response: <1 second latency

### On Laptop (with GPU)
- Object Detection: ~30-60 FPS
- Scene Description (online): ~2-3 seconds
- All operations: Real-time performance

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- Ultralytics for YOLOv8
- Salesforce for BLIP-2
- The open-source community for various libraries and tools

## 📧 Contact

For questions or support, please contact:
- Email: your.email@example.com
- Project Link: [https://github.com/yourusername/blind-assistant](https://github.com/yourusername/blind-assistant)

## 🔮 Future Enhancements

- [ ] Integration with smart home devices
- [ ] 3D spatial audio for enhanced navigation
- [ ] Collaborative assistance (connect with remote helpers)
- [ ] AI-powered obstacle prediction
- [ ] Support for more languages
- [ ] Mobile app companion
- [ ] Cloud synchronization for personalization data

---

**Note**: This is an academic project designed to demonstrate advanced AI and assistive technology concepts. For production use with visually impaired individuals, additional testing, validation, and user studies are recommended.