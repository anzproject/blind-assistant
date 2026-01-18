"""
Audio module for AI Blind Assistant.
Handles text-to-speech, speech-to-text, and voice commands.
Uses offline models where possible.
Enhanced with comprehensive error handling and logging.
"""

import pyttsx3
import vosk
import json
import pyaudio
import logging
import threading
import queue
import time
import os

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.tts_engine = None
        self.stt_model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.tts_available = False
        self.stt_available = False

        # Initialize components with error handling
        self._init_tts()
        self._init_stt()

    def _init_tts(self):
        """Initialize text-to-speech with error handling."""
        try:
            logger.info("Initializing TTS engine...")
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')

            # Set voice preferences
            selected_voice = None
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    selected_voice = voice.id
                    break

            if selected_voice:
                self.tts_engine.setProperty('voice', selected_voice)
                logger.info(f"Selected voice: {selected_voice}")

            self.tts_engine.setProperty('rate', 180)  # Speed of speech
            self.tts_available = True
            logger.info("TTS engine initialized successfully")

        except Exception as e:
            logger.error(f"TTS initialization failed: {e}")
            self.tts_available = False

    def _init_stt(self):
        """Initialize speech-to-text with error handling."""
        try:
            logger.info("Initializing STT model...")
            model_path = "models/vosk-model-small-en-us-0.15"

            if not os.path.exists(model_path):
                logger.warning(f"Vosk model not found at {model_path}. STT will be unavailable.")
                logger.info("To enable STT, download the model from https://alphacephei.com/vosk/models")
                self.stt_available = False
                return

            self.stt_model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.stt_model, 16000)
            self.stt_available = True
            logger.info("STT model loaded successfully")

        except Exception as e:
            logger.error(f"STT initialization failed: {e}")
            self.stt_available = False

    def speak(self, text, priority=False):
        """Convert text to speech with error handling."""
        if not self.tts_available:
            logger.warning("TTS not available. Cannot speak text.")
            return False

        if not text or not isinstance(text, str):
            logger.warning("Invalid text provided to speak()")
            return False

        try:
            logger.debug(f"Speaking: {text[:50]}...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return False

    def listen_for_command(self, timeout=5):
        """Listen for voice command with comprehensive error handling."""
        if not self.stt_available:
            logger.warning("STT not available. Cannot listen for commands.")
            return "Speech recognition unavailable."

        if timeout <= 0:
            logger.warning("Invalid timeout value")
            return "Invalid timeout."

        p = None
        stream = None

        try:
            logger.info("Initializing audio stream...")
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000
            )
            stream.start_stream()

            logger.info(f"Listening for command (timeout: {timeout}s)...")
            start_time = time.time()

            while time.time() - start_time < timeout and self.is_listening:
                try:
                    data = stream.read(4000, exception_on_overflow=False)
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip()
                        if text:
                            logger.info(f"Recognized: {text}")
                            return text

                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Audio processing error: {e}")
                    break

            return "No command detected."

        except Exception as e:
            logger.error(f"STT listening failed: {e}")
            return "Speech recognition error."

        finally:
            # Clean up resources
            try:
                if stream:
                    stream.stop_stream()
                    stream.close()
                if p:
                    p.terminate()
            except Exception as e:
                logger.error(f"Error cleaning up audio resources: {e}")

    def process_voice_command(self, command):
        """Process voice command with improved pattern matching."""
        if not command or not isinstance(command, str):
            logger.warning("Invalid command provided")
            return "unknown_command"

        command = command.lower().strip()

        # Define command patterns
        command_patterns = {
            'describe_scene': ['describe scene', 'describe the scene', 'what do you see', 'scene description'],
            'read_text': ['read text', 'read the text', 'read this', 'ocr', 'read'],
            'detect_objects': ['detect objects', 'find objects', 'what objects', 'object detection'],
            'get_location': ['where am i', 'my location', 'current location', 'location', 'where'],
            'guide_to_location': ['guide me', 'navigate', 'directions', 'guide to', 'take me to'],
            'help': ['help', 'commands', 'what can you do', 'assist'],
            'stop': ['stop', 'exit', 'quit', 'shutdown', 'end']
        }

        for action, patterns in command_patterns.items():
            if any(pattern in command for pattern in patterns):
                logger.info(f"Command matched: '{command}' -> {action}")
                return action

        logger.info(f"Unknown command: '{command}'")
        return 'unknown_command'

    def continuous_listen(self, callback):
        """Continuously listen for commands with improved error handling."""
        if not callable(callback):
            logger.error("Invalid callback provided to continuous_listen")
            return None

        def listen_thread():
            logger.info("Starting continuous listening thread")
            self.is_listening = True
            consecutive_errors = 0
            max_consecutive_errors = 5

            while self.is_listening and consecutive_errors < max_consecutive_errors:
                try:
                    command = self.listen_for_command(timeout=10)
                    if command and command not in [
                        "No command detected.",
                        "Speech recognition unavailable.",
                        "Speech recognition error.",
                        "Invalid timeout."
                    ]:
                        action = self.process_voice_command(command)
                        try:
                            callback(action, command)
                            consecutive_errors = 0  # Reset error count on success
                        except Exception as e:
                            logger.error(f"Error in callback: {e}")
                    else:
                        consecutive_errors += 1

                except Exception as e:
                    logger.error(f"Error in continuous listening: {e}")
                    consecutive_errors += 1
                    time.sleep(1)  # Brief pause before retrying

            if consecutive_errors >= max_consecutive_errors:
                logger.error("Too many consecutive errors, stopping continuous listening")
                self.is_listening = False

        try:
            thread = threading.Thread(target=listen_thread, daemon=True)
            thread.start()
            logger.info("Continuous listening thread started")
            return thread
        except Exception as e:
            logger.error(f"Failed to start listening thread: {e}")
            return None

    def stop_listening(self):
        """Stop continuous listening."""
        logger.info("Stopping continuous listening")
        self.is_listening = False

    def get_status(self):
        """Get comprehensive status of audio components."""
        return {
            "tts_available": self.tts_available,
            "stt_available": self.stt_available,
            "is_listening": self.is_listening,
            "tts_engine": type(self.tts_engine).__name__ if self.tts_engine else None,
            "stt_model_loaded": self.stt_model is not None,
            "queue_size": self.audio_queue.qsize()
        }

    def test_components(self):
        """Test audio components and return results."""
        results = {}

        # Test TTS
        try:
            if self.tts_available:
                self.speak("Testing text to speech", priority=True)
                results["tts"] = "working"
            else:
                results["tts"] = "unavailable"
        except Exception as e:
            results["tts"] = f"error: {e}"

        # Test STT
        try:
            if self.stt_available:
                # Quick test - try to initialize audio (don't actually listen)
                p = pyaudio.PyAudio()
                p.terminate()
                results["stt"] = "initialized"
            else:
                results["stt"] = "unavailable"
        except Exception as e:
            results["stt"] = f"error: {e}"

        return results
