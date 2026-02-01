"""
Emotion Recognizer - Detects facial emotions
"""

import cv2
import numpy as np
import logging
from typing import Optional

from utils.logger import setup_logger

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


class EmotionRecognizer:
    """
    Facial emotion recognition using DeepFace
    """
    
    def __init__(self, config):
        """
        Initialize emotion recognizer
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('EmotionRecognizer', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.model = config.get('emotion_recognition.model', 'deepface')
        self.emotions = config.get('emotion_recognition.emotions', 
                                  ['happy', 'sad', 'angry', 'surprise', 'neutral', 'fear', 'disgust'])
        
        if not DEEPFACE_AVAILABLE:
            self.logger.warning("DeepFace not installed. Emotion recognition unavailable.")
    
    def recognize(self, image: np.ndarray) -> Optional[str]:
        """
        Recognize emotion in image
        
        Args:
            image: Input image
            
        Returns:
            Detected emotion or None
        """
        if not DEEPFACE_AVAILABLE:
            return None
        
        try:
            # Analyze emotion
            result = DeepFace.analyze(
                image,
                actions=['emotion'],
                enforce_detection=False
            )
            
            if isinstance(result, list):
                result = result[0]
            
            # Get dominant emotion
            emotion = result['dominant_emotion']
            
            self.logger.info(f"Detected emotion: {emotion}")
            return emotion
            
        except Exception as e:
            self.logger.error(f"Error in emotion recognition: {e}")
            return None
    
    def shutdown(self):
        """Cleanup resources"""
        self.logger.info("Emotion recognizer shutdown")
