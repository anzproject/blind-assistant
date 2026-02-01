"""
Camera Interface - Manages Pi Camera Module
"""

import cv2
import numpy as np
import logging
from typing import Optional

from utils.logger import setup_logger

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False


class CameraInterface:
    """
    Interface for Pi Camera Module or webcam
    """
    
    def __init__(self, config):
        """
        Initialize camera interface
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('CameraInterface', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.resolution = tuple(config.get('camera.resolution', [1920, 1080]))
        self.fps = config.get('camera.fps', 30)
        self.rotation = config.get('camera.rotation', 0)
        self.device = config.get('system.device', 'laptop')
        
        # Camera object
        self.camera = None
        self.cap = None
        
        # Initialize camera
        self._initialize()
    
    def _initialize(self):
        """Initialize camera"""
        if self.device == 'raspberry_pi' and PICAMERA2_AVAILABLE:
            self._initialize_picamera()
        else:
            self._initialize_webcam()
    
    def _initialize_picamera(self):
        """Initialize Pi Camera"""
        try:
            self.logger.info("Initializing Pi Camera...")
            self.camera = Picamera2()
            
            # Configure camera
            config = self.camera.create_still_configuration(
                main={"size": self.resolution}
            )
            self.camera.configure(config)
            
            # Start camera
            self.camera.start()
            
            self.logger.info("Pi Camera initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Pi Camera: {e}")
            self.logger.info("Falling back to webcam")
            self._initialize_webcam()
    
    def _initialize_webcam(self):
        """Initialize webcam"""
        try:
            self.logger.info("Initializing webcam...")
            self.cap = cv2.VideoCapture(0)
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            if not self.cap.isOpened():
                raise RuntimeError("Failed to open webcam")
            
            self.logger.info("Webcam initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize webcam: {e}")
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Capture a single frame
        
        Returns:
            Captured image or None
        """
        try:
            if self.camera:
                # Pi Camera
                image = self.camera.capture_array()
                
                # Convert from RGB to BGR for OpenCV
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Apply rotation if needed
                if self.rotation != 0:
                    image = self._rotate_image(image, self.rotation)
                
                return image
                
            elif self.cap:
                # Webcam
                ret, frame = self.cap.read()
                
                if not ret:
                    self.logger.error("Failed to capture frame")
                    return None
                
                # Apply rotation if needed
                if self.rotation != 0:
                    frame = self._rotate_image(frame, self.rotation)
                
                return frame
            else:
                self.logger.error("No camera available")
                return None
                
        except Exception as e:
            self.logger.error(f"Error capturing image: {e}")
            return None
    
    def _rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by angle"""
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            return image
    
    def release(self):
        """Release camera resources"""
        if self.camera:
            self.camera.stop()
            self.camera.close()
        
        if self.cap:
            self.cap.release()
    
    def shutdown(self):
        """Shutdown camera"""
        self.release()
        self.logger.info("Camera shutdown")
