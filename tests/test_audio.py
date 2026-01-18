"""
Unit tests for audio module.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

from audio import AudioProcessor

class TestAudioProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.audio = AudioProcessor()

    @patch('pyttsx3.init')
    def test_tts_initialization(self, mock_init):
        """Test TTS engine initialization."""
        mock_engine = Mock()
        mock_init.return_value = mock_engine

        audio = AudioProcessor()
        self.assertIsNotNone(audio.tts_engine)

    @patch('vosk.Model')
    def test_stt_model_loading(self, mock_model):
        """Test STT model loading."""
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        audio = AudioProcessor()
        # Note: This will fail if model path doesn't exist, but tests the logic
        self.assertIsNotNone(audio.stt_model)

    def test_process_voice_command(self):
        """Test voice command processing."""
        test_cases = [
            ("describe scene", "describe_scene"),
            ("read text", "read_text"),
            ("detect objects", "detect_objects"),
            ("where am i", "get_location"),
            ("guide me", "guide_to_location"),
            ("help", "help"),
            ("stop", "stop"),
            ("unknown command", "unknown_command")
        ]

        for command, expected in test_cases:
            with self.subTest(command=command):
                result = self.audio.process_voice_command(command)
                self.assertEqual(result, expected)

    @patch('pyttsx3.init')
    def test_speak(self, mock_init):
        """Test speak functionality."""
        mock_engine = Mock()
        mock_init.return_value = mock_engine

        audio = AudioProcessor()
        audio.speak("Test message")

        mock_engine.say.assert_called_with("Test message")
        mock_engine.runAndWait.assert_called_once()

if __name__ == '__main__':
    unittest.main()
