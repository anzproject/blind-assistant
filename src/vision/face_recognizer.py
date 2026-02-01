"""
Face Recognizer - Recognizes familiar faces
"""

import cv2
import numpy as np
import logging
import os
import pickle
from typing import Optional
from pathlib import Path

from utils.logger import setup_logger

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


class FaceRecognizer:
    """
    Face recognition for identifying familiar people
    """
    
    def __init__(self, config):
        """
        Initialize face recognizer
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('FaceRecognizer', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.model = config.get('face_recognition.model', 'facenet')
        self.tolerance = config.get('face_recognition.tolerance', 0.6)
        self.database_path = Path(config.get('face_recognition.database_path', 'data/user_data/faces'))
        
        # Face database
        self.known_faces = {}
        
        # Initialize
        if FACE_RECOGNITION_AVAILABLE:
            self._load_database()
        else:
            self.logger.warning("face_recognition not installed. Face recognition unavailable.")
    
    def _load_database(self):
        """Load known faces from database"""
        self.database_path.mkdir(parents=True, exist_ok=True)
        
        db_file = self.database_path / "faces.pkl"
        if db_file.exists():
            try:
                with open(db_file, 'rb') as f:
                    self.known_faces = pickle.load(f)
                self.logger.info(f"Loaded {len(self.known_faces)} known faces")
            except Exception as e:
                self.logger.error(f"Error loading face database: {e}")
    
    def recognize(self, image: np.ndarray) -> Optional[str]:
        """
        Recognize face in image
        
        Args:
            image: Input image
            
        Returns:
            Name of recognized person or None
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return None
        
        if not self.known_faces:
            return None
        
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            if not face_locations:
                return None
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            # Compare with known faces
            for face_encoding in face_encodings:
                for name, known_encoding in self.known_faces.items():
                    matches = face_recognition.compare_faces(
                        [known_encoding],
                        face_encoding,
                        tolerance=self.tolerance
                    )
                    
                    if matches[0]:
                        self.logger.info(f"Recognized: {name}")
                        return name
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in face recognition: {e}")
            return None
    
    def add_face(self, image: np.ndarray, name: str) -> bool:
        """
        Add a new face to the database
        
        Args:
            image: Image containing the face
            name: Name of the person
            
        Returns:
            True if face added successfully
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return False
        
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(rgb_image)
            
            if not face_encodings:
                self.logger.error("No face found in image")
                return False
            
            # Add to database
            self.known_faces[name] = face_encodings[0]
            
            # Save database
            db_file = self.database_path / "faces.pkl"
            with open(db_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
            
            self.logger.info(f"Added face for {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding face: {e}")
            return False
    
    def shutdown(self):
        """Cleanup resources"""
        self.logger.info("Face recognizer shutdown")
