"""
System Manager - Coordinates all modules and manages system lifecycle
"""

import time
import threading
from typing import Dict, Any
import logging

from utils.config_loader import get_config
from utils.logger import setup_logger


class SystemManager:
    """
    Central system manager that coordinates all modules
    """
    
    def __init__(self):
        """Initialize system manager"""
        self.logger = setup_logger('SystemManager', 'data/logs/blind_assistant.log')
        self.config = get_config()
        
        # Module instances
        self.modules: Dict[str, Any] = {}
        
        # System state
        self.running = False
        self.initialized = False
        
        # Threading
        self.threads: Dict[str, threading.Thread] = {}
        self.lock = threading.Lock()
    
    def initialize(self):
        """Initialize all system modules"""
        self.logger.info("Initializing system modules...")
        
        try:
            # Initialize modules in order of dependency
            self._init_hardware_modules()
            self._init_audio_modules()
            self._init_vision_modules()
            self._init_navigation_modules()
            self._init_core_modules()
            
            self.initialized = True
            self.logger.info("All modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}", exc_info=True)
            raise
    
    def _init_hardware_modules(self):
        """Initialize hardware interface modules"""
        self.logger.info("Initializing hardware modules...")
        
        # Camera
        try:
            from hardware.camera_interface import CameraInterface
            self.modules['camera'] = CameraInterface(self.config)
            self.logger.info("✓ Camera module initialized")
        except Exception as e:
            self.logger.warning(f"Camera initialization failed: {e}")
        
        # GPS
        try:
            from hardware.gps_interface import GPSInterface
            self.modules['gps'] = GPSInterface(self.config)
            self.logger.info("✓ GPS module initialized")
        except Exception as e:
            self.logger.warning(f"GPS initialization failed: {e}")
        
        # Bluetooth
        try:
            from hardware.bluetooth_manager import BluetoothManager
            self.modules['bluetooth'] = BluetoothManager(self.config)
            self.logger.info("✓ Bluetooth module initialized")
        except Exception as e:
            self.logger.warning(f"Bluetooth initialization failed: {e}")
        
        # Obstacle sensors (if enabled)
        if self.config.get('obstacle_detection.enabled', False):
            try:
                from hardware.obstacle_sensor import ObstacleSensor
                self.modules['obstacle_sensor'] = ObstacleSensor(self.config)
                self.logger.info("✓ Obstacle sensor initialized")
            except Exception as e:
                self.logger.warning(f"Obstacle sensor initialization failed: {e}")
        
        # Haptic feedback (if enabled)
        if self.config.get('haptic_feedback.enabled', False):
            try:
                from hardware.haptic_feedback import HapticFeedback
                self.modules['haptic'] = HapticFeedback(self.config)
                self.logger.info("✓ Haptic feedback initialized")
            except Exception as e:
                self.logger.warning(f"Haptic feedback initialization failed: {e}")
    
    def _init_audio_modules(self):
        """Initialize audio processing modules"""
        self.logger.info("Initializing audio modules...")
        
        # Speech-to-Text
        try:
            from audio.speech_to_text import SpeechToText
            self.modules['stt'] = SpeechToText(self.config)
            self.logger.info("✓ Speech-to-Text initialized")
        except Exception as e:
            self.logger.error(f"STT initialization failed: {e}")
            raise
        
        # Text-to-Speech
        try:
            from audio.text_to_speech import TextToSpeech
            self.modules['tts'] = TextToSpeech(self.config)
            self.logger.info("✓ Text-to-Speech initialized")
        except Exception as e:
            self.logger.error(f"TTS initialization failed: {e}")
            raise
        
        # Audio Manager
        try:
            from audio.audio_manager import AudioManager
            self.modules['audio'] = AudioManager(self.config, self.modules['tts'])
            self.logger.info("✓ Audio Manager initialized")
        except Exception as e:
            self.logger.error(f"Audio Manager initialization failed: {e}")
            raise
    
    def _init_vision_modules(self):
        """Initialize computer vision modules"""
        self.logger.info("Initializing vision modules...")
        
        # Object Detector
        try:
            from vision.object_detector import ObjectDetector
            self.modules['object_detector'] = ObjectDetector(self.config)
            self.logger.info("✓ Object Detector initialized")
        except Exception as e:
            self.logger.warning(f"Object Detector initialization failed: {e}")
        
        # Scene Describer
        try:
            from vision.scene_describer import SceneDescriber
            self.modules['scene_describer'] = SceneDescriber(self.config)
            self.logger.info("✓ Scene Describer initialized")
        except Exception as e:
            self.logger.warning(f"Scene Describer initialization failed: {e}")
        
        # OCR Engine
        try:
            from vision.ocr_engine import OCREngine
            self.modules['ocr'] = OCREngine(self.config)
            self.logger.info("✓ OCR Engine initialized")
        except Exception as e:
            self.logger.warning(f"OCR Engine initialization failed: {e}")
        
        # Distance Estimator
        try:
            from vision.distance_estimator import DistanceEstimator
            self.modules['distance'] = DistanceEstimator(self.config)
            self.logger.info("✓ Distance Estimator initialized")
        except Exception as e:
            self.logger.warning(f"Distance Estimator initialization failed: {e}")
        
        # Emotion Recognizer (if enabled)
        if self.config.get('emotion_recognition.enabled', False):
            try:
                from vision.emotion_recognizer import EmotionRecognizer
                self.modules['emotion'] = EmotionRecognizer(self.config)
                self.logger.info("✓ Emotion Recognizer initialized")
            except Exception as e:
                self.logger.warning(f"Emotion Recognizer initialization failed: {e}")
        
        # Face Recognizer (if enabled)
        if self.config.get('face_recognition.enabled', False):
            try:
                from vision.face_recognizer import FaceRecognizer
                self.modules['face'] = FaceRecognizer(self.config)
                self.logger.info("✓ Face Recognizer initialized")
            except Exception as e:
                self.logger.warning(f"Face Recognizer initialization failed: {e}")
        
        # Currency Recognizer (if enabled)
        if self.config.get('currency_recognition.enabled', False):
            try:
                from vision.currency_recognizer import CurrencyRecognizer
                self.modules['currency'] = CurrencyRecognizer(self.config)
                self.logger.info("✓ Currency Recognizer initialized")
            except Exception as e:
                self.logger.warning(f"Currency Recognizer initialization failed: {e}")
        
        # Color Identifier (if enabled)
        if self.config.get('color_identification.enabled', False):
            try:
                from vision.color_identifier import ColorIdentifier
                self.modules['color'] = ColorIdentifier(self.config)
                self.logger.info("✓ Color Identifier initialized")
            except Exception as e:
                self.logger.warning(f"Color Identifier initialization failed: {e}")
    
    def _init_navigation_modules(self):
        """Initialize navigation modules"""
        self.logger.info("Initializing navigation modules...")
        
        # Navigation Engine
        try:
            from navigation.navigation_engine import NavigationEngine
            self.modules['navigation'] = NavigationEngine(
                self.config,
                self.modules.get('gps'),
                self.modules.get('audio')
            )
            self.logger.info("✓ Navigation Engine initialized")
        except Exception as e:
            self.logger.warning(f"Navigation Engine initialization failed: {e}")
        
        # POI Detector
        try:
            from navigation.poi_detector import POIDetector
            self.modules['poi'] = POIDetector(self.config, self.modules.get('gps'))
            self.logger.info("✓ POI Detector initialized")
        except Exception as e:
            self.logger.warning(f"POI Detector initialization failed: {e}")
    
    def _init_core_modules(self):
        """Initialize core system modules"""
        self.logger.info("Initializing core modules...")
        
        # Command Processor
        try:
            from core.command_processor import CommandProcessor
            self.modules['command_processor'] = CommandProcessor(self.config, self.modules)
            self.logger.info("✓ Command Processor initialized")
        except Exception as e:
            self.logger.error(f"Command Processor initialization failed: {e}")
            raise
        
        # Context Analyzer (if enabled)
        if self.config.get('context_awareness.enabled', False):
            try:
                from core.context_analyzer import ContextAnalyzer
                self.modules['context'] = ContextAnalyzer(self.config, self.modules)
                self.logger.info("✓ Context Analyzer initialized")
            except Exception as e:
                self.logger.warning(f"Context Analyzer initialization failed: {e}")
        
        # Emergency SOS (if enabled)
        if self.config.get('emergency_sos.enabled', False):
            try:
                from core.emergency_sos import EmergencySOS
                self.modules['emergency'] = EmergencySOS(
                    self.config,
                    self.modules.get('gps'),
                    self.modules.get('audio')
                )
                self.logger.info("✓ Emergency SOS initialized")
            except Exception as e:
                self.logger.warning(f"Emergency SOS initialization failed: {e}")
    
    def run(self):
        """Run main system loop"""
        if not self.initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        self.running = True
        self.logger.info("Starting main system loop...")
        
        # Welcome message
        if 'audio' in self.modules:
            self.modules['audio'].speak("Blind assistant is ready. How can I help you?")
        
        try:
            # Main loop
            while self.running:
                # Listen for voice commands
                if 'stt' in self.modules and 'command_processor' in self.modules:
                    command = self.modules['stt'].listen()
                    
                    if command:
                        self.logger.info(f"Command received: {command}")
                        
                        # Process command
                        self.modules['command_processor'].process(command)
                else:
                    # If STT or command processor is missing, don't spin too fast
                    time.sleep(1.0)
                
                # Small delay to prevent CPU spinning
                time.sleep(0.1)
                
            self.logger.info("Main system loop finished")
            
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt in main loop")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
            # Add a small delay on error to prevent rapid looping
            time.sleep(1.0)
    
    def shutdown(self):
        """Shutdown all modules gracefully"""
        self.logger.info("Shutting down system...")
        self.running = False
        
        # Shutdown modules in reverse order
        for name, module in reversed(list(self.modules.items())):
            try:
                if hasattr(module, 'shutdown'):
                    module.shutdown()
                    self.logger.info(f"✓ {name} shutdown")
            except Exception as e:
                self.logger.error(f"Error shutting down {name}: {e}")
        
        self.logger.info("System shutdown complete")
