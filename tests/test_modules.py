"""
Comprehensive tests for all modules.
"""

import unittest
import sys
from unittest.mock import Mock, patch, MagicMock
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

class TestModules(unittest.TestCase):
    """Test all modules for import and basic functionality."""

    def test_audio_processor_import(self):
        """Test AudioProcessor can be imported and instantiated."""
        try:
            from audio import AudioProcessor
            # Mock the TTS engine to avoid hardware dependencies
            with patch('pyttsx3.init') as mock_init:
                mock_engine = Mock()
                mock_init.return_value = mock_engine
                audio = AudioProcessor()
                self.assertIsNotNone(audio)
                print("✓ AudioProcessor import and instantiation successful")
        except Exception as e:
            self.fail(f"AudioProcessor test failed: {e}")

    def test_vision_processor_import(self):
        """Test VisionProcessor can be imported."""
        try:
            from vision import VisionProcessor
            vision = VisionProcessor()
            self.assertIsNotNone(vision)
            print("✓ VisionProcessor import and instantiation successful")
        except Exception as e:
            self.fail(f"VisionProcessor test failed: {e}")

    def test_gps_handler_import(self):
        """Test GPSHandler can be imported."""
        try:
            from gps import GPSHandler
            gps = GPSHandler()
            self.assertIsNotNone(gps)
            print("✓ GPSHandler import and instantiation successful")
        except Exception as e:
            self.fail(f"GPSHandler test failed: {e}")

    def test_camera_handler_import(self):
        """Test CameraHandler can be imported."""
        try:
            from camera import CameraHandler
            camera = CameraHandler()
            self.assertIsNotNone(camera)
            print("✓ CameraHandler import and instantiation successful")
        except Exception as e:
            self.fail(f"CameraHandler test failed: {e}")

    def test_smart_navigation_import(self):
        """Test SmartNavigation can be imported."""
        try:
            from smart_navigation import SmartNavigation
            # Mock dependencies
            mock_camera = Mock()
            mock_gps = Mock()
            nav = SmartNavigation(mock_camera, mock_gps)
            self.assertIsNotNone(nav)
            print("✓ SmartNavigation import and instantiation successful")
        except Exception as e:
            self.fail(f"SmartNavigation test failed: {e}")

    def test_emotion_aware_import(self):
        """Test EmotionAware can be imported."""
        try:
            from emotion_aware import EmotionAware
            # Mock dependencies
            mock_vision = Mock()
            mock_audio = Mock()
            emotion = EmotionAware(mock_vision, mock_audio)
            self.assertIsNotNone(emotion)
            print("✓ EmotionAware import and instantiation successful")
        except Exception as e:
            self.fail(f"EmotionAware test failed: {e}")

    def test_blind_assistant_import(self):
        """Test BlindAssistant can be imported and basic methods exist."""
        try:
            from assistant import BlindAssistant
            # Check if class exists and has expected methods
            self.assertTrue(hasattr(BlindAssistant, 'start'))
            self.assertTrue(hasattr(BlindAssistant, 'stop'))
            print("✓ BlindAssistant import and structure validation successful")
        except Exception as e:
            self.fail(f"BlindAssistant test failed: {e}")

    def test_voice_command_processing(self):
        """Test voice command processing logic."""
        try:
            from audio import AudioProcessor
            with patch('pyttsx3.init'):
                audio = AudioProcessor()

                test_commands = [
                    ("describe scene", "describe_scene"),
                    ("read text", "read_text"),
                    ("detect objects", "detect_objects"),
                    ("where am i", "get_location"),
                    ("help", "help"),
                    ("stop", "stop"),
                    ("unknown command", "unknown_command")
                ]

                for command, expected in test_commands:
                    result = audio.process_voice_command(command)
                    self.assertEqual(result, expected, f"Failed for command: {command}")

                print("✓ Voice command processing logic working correctly")
        except Exception as e:
            self.fail(f"Voice command processing test failed: {e}")

    def test_navigation_path_planning(self):
        """Test basic path planning logic."""
        try:
            from smart_navigation import SmartNavigation
            mock_camera = Mock()
            mock_gps = Mock()

            nav = SmartNavigation(mock_camera, mock_gps)

            # Test path planning with simple coordinates
            start = (0.0, 0.0)
            goal = (1.0, 1.0)
            path = nav.plan_path(start, goal)

            # Should return a path (may be empty if no valid path found in simple test)
            self.assertIsInstance(path, list)
            print("✓ Navigation path planning logic working")
        except Exception as e:
            self.fail(f"Navigation path planning test failed: {e}")

if __name__ == '__main__':
    print("Running comprehensive module tests...")
    print("=" * 50)
    unittest.main(verbosity=2)
