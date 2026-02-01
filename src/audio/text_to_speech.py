"""
Text-to-Speech - Converts text to speech
"""

import logging
from typing import Optional
import os

from utils.logger import setup_logger

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


class TextToSpeech:
    """
    Text-to-speech engine supporting multiple backends
    """
    
    def __init__(self, config):
        """
        Initialize text-to-speech
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('TextToSpeech', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.engine_name = config.get('text_to_speech.engine', 'pyttsx3')
        self.voice = config.get('text_to_speech.voice', 'default')
        self.rate = config.get('text_to_speech.rate', 175)
        self.volume = config.get('text_to_speech.volume', 1.0)
        
        # Engine
        self.engine = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize TTS engine"""
        if self.engine_name == 'pyttsx3':
            self._initialize_pyttsx3()
        elif self.engine_name == 'gtts':
            self._initialize_gtts()
        else:
            self.logger.error(f"Unknown TTS engine: {self.engine_name}")
    
    def _initialize_pyttsx3(self):
        """Initialize pyttsx3 offline TTS"""
        if not PYTTSX3_AVAILABLE:
            self.logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            return
        
        try:
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Set voice if specified
            if self.voice != 'default':
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if self.voice.lower() in v.name.lower():
                        self.engine.setProperty('voice', v.id)
                        break
            
            self.logger.info("pyttsx3 TTS initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
    
    def _initialize_gtts(self):
        """Initialize Google TTS"""
        if not GTTS_AVAILABLE:
            self.logger.error("gTTS not installed. Install with: pip install gtts pygame")
            return
        
        try:
            # Initialize pygame mixer for audio playback
            pygame.mixer.init()
            self.engine = 'gtts'
            self.logger.info("gTTS initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize gTTS: {e}")
    
    def speak(self, text: str, blocking: bool = True):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            blocking: Wait for speech to complete
        """
        if not text:
            return
        
        self.logger.info(f"Speaking: {text[:50]}...")
        
        try:
            if self.engine_name == 'pyttsx3' and self.engine:
                self._speak_pyttsx3(text, blocking)
            elif self.engine_name == 'gtts' and self.engine:
                self._speak_gtts(text)
            else:
                self.logger.warning("No TTS engine available")
        except Exception as e:
            self.logger.error(f"Error during speech: {e}")
    
    def _speak_pyttsx3(self, text: str, blocking: bool):
        """Speak using pyttsx3"""
        self.engine.say(text)
        if blocking:
            self.engine.runAndWait()
    
    def _speak_gtts(self, text: str):
        """Speak using gTTS"""
        try:
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            temp_file = "data/temp_speech.mp3"
            os.makedirs("data", exist_ok=True)
            tts.save(temp_file)
            
            # Play audio
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            pygame.mixer.music.unload()
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            self.logger.error(f"Error in gTTS speech: {e}")
    
    def stop(self):
        """Stop current speech"""
        if self.engine_name == 'pyttsx3' and self.engine:
            self.engine.stop()
        elif self.engine_name == 'gtts':
            pygame.mixer.music.stop()
    
    def shutdown(self):
        """Cleanup resources"""
        if self.engine_name == 'pyttsx3' and self.engine:
            self.engine.stop()
        elif self.engine_name == 'gtts':
            pygame.mixer.quit()
        
        self.logger.info("Text-to-speech shutdown")
