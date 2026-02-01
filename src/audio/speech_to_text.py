"""
Speech-to-Text - Converts speech to text
"""

import logging
from typing import Optional
import time

from utils.logger import setup_logger

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
    import json
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False


class SpeechToText:
    """
    Speech-to-text engine supporting multiple backends
    """
    
    def __init__(self, config):
        """
        Initialize speech-to-text
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('SpeechToText', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.engine = config.get('speech_to_text.engine', 'vosk')
        self.model_path = config.get('speech_to_text.model_path', 'models/vosk-model-small-en-us-0.15')
        self.language = config.get('speech_to_text.language', 'en-US')
        self.sample_rate = config.get('speech_to_text.sample_rate', 16000)
        
        # Recognizer
        self.recognizer = None
        self.microphone = None
        
        # Vosk specific
        self.vosk_model = None
        self.vosk_recognizer = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize speech recognition"""
        if self.engine == 'vosk':
            self._initialize_vosk()
        else:
            self._initialize_sr()
    
    def _initialize_vosk(self):
        """Initialize Vosk offline recognition"""
        if not VOSK_AVAILABLE:
            self.logger.warning("Vosk not installed. Falling back to speech_recognition.")
            self.engine = 'sr'
            self._initialize_sr()
            return
        
        try:
            self.logger.info(f"Loading Vosk model from: {self.model_path}")
            self.vosk_model = Model(self.model_path)
            self.vosk_recognizer = KaldiRecognizer(self.vosk_model, self.sample_rate)
            self.logger.info("Vosk initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Vosk: {e}")
            self.logger.info("Falling back to speech_recognition")
            self.engine = 'sr'
            self._initialize_sr()
    
    def _initialize_sr(self):
        """Initialize speech_recognition library"""
        if not SR_AVAILABLE:
            self.logger.error("speech_recognition not installed. Install with: pip install SpeechRecognition")
            return
        
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("Speech recognition initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """
        Listen for speech and convert to text
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Recognized text or None
        """
        if self.engine == 'vosk' and self.vosk_recognizer:
            return self._listen_vosk(timeout)
        elif self.recognizer:
            return self._listen_sr(timeout)
        else:
            self.logger.error("No speech recognition engine available")
            return None
    
    def _listen_vosk(self, timeout: int) -> Optional[str]:
        """Listen using Vosk"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=8192
            )
            stream.start_stream()
            
            self.logger.info("Listening...")
            
            start_time = time.time()
            result_text = ""
            
            while time.time() - start_time < timeout:
                data = stream.read(4096, exception_on_overflow=False)
                
                if self.vosk_recognizer.AcceptWaveform(data):
                    result = json.loads(self.vosk_recognizer.Result())
                    result_text = result.get('text', '')
                    
                    if result_text:
                        break
            
            # Get final result
            if not result_text:
                final_result = json.loads(self.vosk_recognizer.FinalResult())
                result_text = final_result.get('text', '')
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if result_text:
                self.logger.info(f"Recognized: {result_text}")
                return result_text
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error in Vosk listening: {e}")
            return None
    
    def _listen_sr(self, timeout: int) -> Optional[str]:
        """Listen using speech_recognition"""
        try:
            with self.microphone as source:
                self.logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Try to recognize using Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                self.logger.info(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Could not request results: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}")
            return None
    
    def shutdown(self):
        """Cleanup resources"""
        if self.vosk_model:
            del self.vosk_model
            del self.vosk_recognizer
        self.logger.info("Speech-to-text shutdown")
