"""
Command Processor - Interprets voice commands and routes to appropriate modules
"""

import re
import logging
from typing import Dict, Any, Optional

from utils.logger import setup_logger


class CommandProcessor:
    """
    Processes voice commands and routes them to appropriate modules
    """
    
    def __init__(self, config, modules: Dict[str, Any]):
        """
        Initialize command processor
        
        Args:
            config: Configuration object
            modules: Dictionary of initialized modules
        """
        self.logger = setup_logger('CommandProcessor', 'data/logs/blind_assistant.log')
        self.config = config
        self.modules = modules
        
        # Command patterns
        self.command_patterns = {
            'describe_scene': [
                r'what do you see',
                r'describe.*scene',
                r'what.*in front',
                r'describe.*around'
            ],
            'detect_objects': [
                r'what.*objects',
                r'detect.*objects',
                r'what.*there',
                r'identify.*objects'
            ],
            'read_text': [
                r'read.*text',
                r'what.*text',
                r'read.*this',
                r'what.*written'
            ],
            'get_location': [
                r'where am i',
                r'current location',
                r'my location'
            ],
            'navigate': [
                r'navigate to (.*)',
                r'take me to (.*)',
                r'directions to (.*)',
                r'how to get to (.*)'
            ],
            'identify_person': [
                r'who is this',
                r'who.*person',
                r'identify.*person',
                r'recognize.*face'
            ],
            'identify_emotion': [
                r'what.*emotion',
                r'how.*feeling',
                r'detect.*emotion'
            ],
            'identify_color': [
                r'what color',
                r'identify.*color',
                r'what.*color'
            ],
            'identify_currency': [
                r'what.*currency',
                r'identify.*money',
                r'what.*denomination',
                r'how much.*money'
            ],
            'detect_obstacles': [
                r'obstacles',
                r'what.*ahead',
                r'clear.*path'
            ],
            'emergency': [
                r'emergency',
                r'help.*emergency',
                r'sos'
            ],
            'stop': [
                r'stop',
                r'cancel',
                r'nevermind'
            ]
        }
    
    def process(self, command: str) -> Optional[str]:
        """
        Process a voice command
        
        Args:
            command: Voice command text
            
        Returns:
            Response message or None
        """
        if not command:
            return None
        
        command = command.lower().strip()
        self.logger.info(f"Processing command: {command}")
        
        # Match command to pattern
        command_type, params = self._match_command(command)
        
        if not command_type:
            self._speak("I didn't understand that command. Please try again.")
            return None
        
        # Route to appropriate handler
        try:
            response = self._route_command(command_type, params)
            return response
        except Exception as e:
            self.logger.error(f"Error processing command: {e}", exc_info=True)
            self._speak("Sorry, I encountered an error processing that command.")
            return None
    
    def _match_command(self, command: str) -> tuple:
        """
        Match command to pattern
        
        Args:
            command: Command text
            
        Returns:
            Tuple of (command_type, parameters)
        """
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    # Extract parameters if any
                    params = match.groups() if match.groups() else ()
                    return cmd_type, params
        
        return None, None
    
    def _route_command(self, command_type: str, params: tuple) -> Optional[str]:
        """
        Route command to appropriate module
        
        Args:
            command_type: Type of command
            params: Command parameters
            
        Returns:
            Response message
        """
        handlers = {
            'describe_scene': self._handle_describe_scene,
            'detect_objects': self._handle_detect_objects,
            'read_text': self._handle_read_text,
            'get_location': self._handle_get_location,
            'navigate': self._handle_navigate,
            'identify_person': self._handle_identify_person,
            'identify_emotion': self._handle_identify_emotion,
            'identify_color': self._handle_identify_color,
            'identify_currency': self._handle_identify_currency,
            'detect_obstacles': self._handle_detect_obstacles,
            'emergency': self._handle_emergency,
            'stop': self._handle_stop
        }
        
        handler = handlers.get(command_type)
        if handler:
            return handler(params)
        
        return None
    
    def _handle_describe_scene(self, params: tuple) -> str:
        """Handle scene description command"""
        self._speak("Let me describe what I see.")
        
        if 'camera' not in self.modules or 'scene_describer' not in self.modules:
            self._speak("Camera or scene description is not available.")
            return None
        
        # Capture image
        image = self.modules['camera'].capture()
        
        # Get scene description
        description = self.modules['scene_describer'].describe(image)
        
        self._speak(description)
        return description
    
    def _handle_detect_objects(self, params: tuple) -> str:
        """Handle object detection command"""
        self._speak("Detecting objects.")
        
        if 'camera' not in self.modules or 'object_detector' not in self.modules:
            self._speak("Camera or object detection is not available.")
            return None
        
        # Capture image
        image = self.modules['camera'].capture()
        
        # Detect objects
        detections = self.modules['object_detector'].detect(image)
        
        if not detections:
            self._speak("I don't see any objects.")
            return None
        
        # Get distances if available
        if 'distance' in self.modules:
            distances = self.modules['distance'].estimate(image, detections)
        else:
            distances = None
        
        # Build response
        response = f"I see {len(detections)} objects. "
        for i, det in enumerate(detections[:5]):  # Limit to 5 objects
            obj_name = det['class']
            confidence = det['confidence']
            
            if distances and i < len(distances):
                dist = distances[i]
                response += f"{obj_name} at {dist:.1f} meters. "
            else:
                response += f"{obj_name}. "
        
        self._speak(response)
        return response
    
    def _handle_read_text(self, params: tuple) -> str:
        """Handle text reading command"""
        self._speak("Reading text.")
        
        if 'camera' not in self.modules or 'ocr' not in self.modules:
            self._speak("Camera or text reading is not available.")
            return None
        
        # Capture image
        image = self.modules['camera'].capture()
        
        # Extract text
        text = self.modules['ocr'].extract_text(image)
        
        if not text or not text.strip():
            self._speak("I don't see any text.")
            return None
        
        self._speak(f"The text says: {text}")
        return text
    
    def _handle_get_location(self, params: tuple) -> str:
        """Handle location query command"""
        if 'gps' not in self.modules:
            self._speak("GPS is not available.")
            return None
        
        location = self.modules['gps'].get_location()
        
        if not location:
            self._speak("Unable to get current location.")
            return None
        
        lat, lon = location
        response = f"Your current location is latitude {lat:.6f}, longitude {lon:.6f}."
        
        # Get address if available
        if 'navigation' in self.modules:
            address = self.modules['navigation'].get_address(lat, lon)
            if address:
                response = f"You are at {address}."
        
        self._speak(response)
        return response
    
    def _handle_navigate(self, params: tuple) -> str:
        """Handle navigation command"""
        if not params or not params[0]:
            self._speak("Where would you like to go?")
            return None
        
        destination = params[0].strip()
        self._speak(f"Navigating to {destination}.")
        
        if 'navigation' not in self.modules:
            self._speak("Navigation is not available.")
            return None
        
        # Start navigation
        success = self.modules['navigation'].navigate_to(destination)
        
        if success:
            return f"Navigation started to {destination}"
        else:
            self._speak("Unable to start navigation.")
            return None
    
    def _handle_identify_person(self, params: tuple) -> str:
        """Handle person identification command"""
        if 'camera' not in self.modules or 'face' not in self.modules:
            self._speak("Camera or face recognition is not available.")
            return None
        
        self._speak("Identifying person.")
        
        # Capture image
        image = self.modules['camera'].capture()
        
        # Recognize face
        person = self.modules['face'].recognize(image)
        
        if person:
            self._speak(f"This is {person}.")
            return person
        else:
            self._speak("I don't recognize this person.")
            return None
    
    def _handle_identify_emotion(self, params: tuple) -> str:
        """Handle emotion identification command"""
        if 'camera' not in self.modules or 'emotion' not in self.modules:
            self._speak("Camera or emotion recognition is not available.")
            return None
        
        self._speak("Detecting emotion.")
        
        # Capture image
        image = self.modules['camera'].capture()
        
        # Recognize emotion
        emotion = self.modules['emotion'].recognize(image)
        
        if emotion:
            self._speak(f"The person appears to be {emotion}.")
            return emotion
        else:
            self._speak("Unable to detect emotion.")
            return None
    
    def _handle_identify_color(self, params: tuple) -> str:
        """Handle color identification command"""
        if 'camera' not in self.modules or 'color' not in self.modules:
            self._speak("Camera or color identification is not available.")
            return None
        
        self._speak("Identifying color.")
        
        # Capture image
        image = self.modules['camera'].capture()
        
        # Identify color
        colors = self.modules['color'].identify(image)
        
        if colors:
            response = f"The dominant colors are {', '.join(colors)}."
            self._speak(response)
            return response
        else:
            self._speak("Unable to identify colors.")
            return None
    
    def _handle_identify_currency(self, params: tuple) -> str:
        """Handle currency identification command"""
        if 'camera' not in self.modules or 'currency' not in self.modules:
            self._speak("Camera or currency recognition is not available.")
            return None
        
        self._speak("Identifying currency.")
        
        # Capture image
        image = self.modules['camera'].capture()
        
        # Recognize currency
        result = self.modules['currency'].recognize(image)
        
        if result:
            currency, denomination = result
            self._speak(f"This is a {denomination} {currency} note.")
            return f"{denomination} {currency}"
        else:
            self._speak("Unable to identify currency.")
            return None
    
    def _handle_detect_obstacles(self, params: tuple) -> str:
        """Handle obstacle detection command"""
        if 'obstacle_sensor' not in self.modules:
            self._speak("Obstacle detection is not available.")
            return None
        
        # Get obstacle distance
        distance = self.modules['obstacle_sensor'].get_distance()
        
        if distance < 100:  # Less than 1 meter
            self._speak(f"Obstacle detected at {distance} centimeters.")
            return f"Obstacle at {distance}cm"
        else:
            self._speak("Path is clear.")
            return "Clear"
    
    def _handle_emergency(self, params: tuple) -> str:
        """Handle emergency SOS command"""
        self._speak("Activating emergency SOS.")
        
        if 'emergency' not in self.modules:
            self._speak("Emergency system is not available.")
            return None
        
        # Trigger emergency
        self.modules['emergency'].trigger()
        
        return "Emergency SOS activated"
    
    def _handle_stop(self, params: tuple) -> str:
        """Handle stop command"""
        self._speak("Stopping.")
        
        # Stop navigation if active
        if 'navigation' in self.modules:
            self.modules['navigation'].stop()
        
        return "Stopped"
    
    def _speak(self, text: str):
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
        """
        if 'audio' in self.modules:
            self.modules['audio'].speak(text)
        else:
            self.logger.info(f"[SPEAK]: {text}")
