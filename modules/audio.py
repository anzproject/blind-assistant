"""
Audio module for AI Blind Assistant.
Handles text-to-speech, speech-to-text, and voice commands.
Uses offline models where possible.
"""

import pyttsx3
import vosk
import json
import pyaudio
import logging
import threading
import queue

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        self.stt_model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self._setup_tts()
        self._load_stt_model()

    def _setup_tts(self):
        """Setup text-to-speech engine."""
        voices = self.tts_engine.getProperty('voices')
        # Set voice (prefer female voice if available)
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        self.tts_engine.setProperty('rate', 180)  # Speed of speech

    def _load_stt_model(self):
        """Load Vosk STT model."""
        try:
            model_path = "models/vosk-model-small-en-us-0.15"  # Download and place in models/
            self.stt_model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.stt_model, 16000)
            logger.info("STT model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load STT model: {e}. Please ensure model is downloaded.")

    def speak(self, text):
        """Convert text to speech."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS failed: {e}")

    def listen_for_command(self, timeout=5):
        """Listen for voice command and return transcribed text."""
        if not self.recognizer:
            return "STT model not loaded."

        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
            stream.start_stream()

            logger.info("Listening for command...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                data = stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '')
                    if text:
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        return text

            stream.stop_stream()
            stream.close()
            p.terminate()
            return "No command detected."

        except Exception as e:
            logger.error(f"STT failed: {e}")
            return "Speech recognition error."

    def process_voice_command(self, command):
        """Process voice command and return response."""
        command = command.lower()
        if 'describe scene' in command:
            return 'describe_scene'
        elif 'read text' in command:
            return 'read_text'
        elif 'detect objects' in command:
            return 'detect_objects'
        elif 'where am i' in command or 'location' in command:
            return 'get_location'
        elif 'guide me' in command:
            return 'guide_to_location'
        elif 'help' in command:
            return 'help'
        elif 'stop' in command or 'exit' in command:
            return 'stop'
        else:
            return 'unknown_command'

    def continuous_listen(self, callback):
        """Continuously listen for commands in a separate thread."""
        def listen_thread():
            self.is_listening = True
            while self.is_listening:
                command = self.listen_for_command(timeout=10)
                if command and command != "No command detected.":
                    action = self.process_voice_command(command)
                    callback(action, command)

        thread = threading.Thread(target=listen_thread)
        thread.daemon = True
        thread.start()
        return thread

    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
