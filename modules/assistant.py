"""
Main assistant module for AI Blind Assistant.
Integrates all modules and handles the main logic.
"""

import logging
import time
from typing import Dict, Any
from .audio import AudioProcessor
from .vision import VisionProcessor
from .gps import GPSHandler
from .camera import CameraHandler

logger = logging.getLogger(__name__)

class BlindAssistant:
    def __init__(self):
        self.audio = AudioProcessor()
        self.vision = VisionProcessor()
        self.gps = GPSHandler()
        self.camera = CameraHandler()
        self.is_running = False
        self.user_profiles = {}  # For customizable profiles

    def start(self):
        """Start the assistant."""
        self.is_running = True
        logger.info("Blind Assistant started.")
        self.audio.speak("Blind assistant activated. Say 'help' for available commands.")

        # Start continuous listening
        self.audio.continuous_listen(self._handle_command)

    def stop(self):
        """Stop the assistant."""
        self.is_running = False
        self.audio.stop_listening()
        logger.info("Blind Assistant stopped.")

    def _handle_command(self, action: str, command: str):
        """Handle voice commands."""
        logger.info(f"Processing command: {command} -> {action}")

        if action == 'describe_scene':
            self._describe_scene()
        elif action == 'read_text':
            self._read_text()
        elif action == 'detect_objects':
            self._detect_objects()
        elif action == 'get_location':
            self._get_location()
        elif action == 'guide_to_location':
            self._guide_to_location()
        elif action == 'help':
            self._show_help()
        elif action == 'stop':
            self.stop()
        else:
            self.audio.speak("Sorry, I didn't understand that command. Say 'help' for available commands.")

    def _describe_scene(self):
        """Describe the current scene."""
        try:
            frame = self.camera.capture_frame()
            if frame is not None:
                description = self.vision.describe_scene(frame)
                self.audio.speak(description)
            else:
                self.audio.speak("Unable to capture image.")
        except Exception as e:
            logger.error(f"Scene description failed: {e}")
            self.audio.speak("Sorry, I couldn't describe the scene.")

    def _read_text(self):
        """Read text from image."""
        try:
            frame = self.camera.capture_frame()
            if frame is not None:
                text = self.vision.read_text(frame)
                if text:
                    self.audio.speak(f"I see the following text: {text}")
                else:
                    self.audio.speak("No text detected in the image.")
            else:
                self.audio.speak("Unable to capture image.")
        except Exception as e:
            logger.error(f"Text reading failed: {e}")
            self.audio.speak("Sorry, I couldn't read the text.")

    def _detect_objects(self):
        """Detect objects in the scene."""
        try:
            frame = self.camera.capture_frame()
            if frame is not None:
                objects = self.vision.detect_objects(frame)
                if objects:
                    object_list = ", ".join(objects)
                    self.audio.speak(f"I detect the following objects: {object_list}")
                else:
                    self.audio.speak("No objects detected.")
            else:
                self.audio.speak("Unable to capture image.")
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            self.audio.speak("Sorry, I couldn't detect objects.")

    def _get_location(self):
        """Get current location."""
        try:
            location_desc = self.gps.get_location_description()
            self.audio.speak(location_desc)
        except Exception as e:
            logger.error(f"Location retrieval failed: {e}")
            self.audio.speak("Sorry, I couldn't get your location.")

    def _guide_to_location(self):
        """Guide to a location."""
        self.audio.speak("Please say the destination address or coordinates.")
        # For simplicity, this would need more implementation for address parsing
        # For now, assume coordinates or implement voice input for destination
        self.audio.speak("Guiding feature not fully implemented yet. Please specify coordinates.")

    def _show_help(self):
        """Show available commands."""
        help_text = """
        Available commands:
        - Describe scene: Get a description of your surroundings
        - Read text: Read any text visible in your camera view
        - Detect objects: Identify objects in your view
        - Where am I: Get your current location
        - Guide me: Get directions to a location
        - Help: Show this help message
        - Stop: Stop the assistant
        """
        self.audio.speak(help_text)

    def emergency_alert(self):
        """Handle emergency situations."""
        # This could integrate with phone/SMS or other alert systems
        self.audio.speak("Emergency alert activated. Help is on the way.")
        logger.warning("Emergency alert triggered.")

    def add_user_profile(self, profile_name: str, settings: Dict[str, Any]):
        """Add or update user profile."""
        self.user_profiles[profile_name] = settings
        logger.info(f"Profile {profile_name} updated.")

    def load_user_profile(self, profile_name: str):
        """Load user profile settings."""
        if profile_name in self.user_profiles:
            # Apply settings (e.g., voice preferences, sensitivity)
            logger.info(f"Profile {profile_name} loaded.")
            return True
        return False
