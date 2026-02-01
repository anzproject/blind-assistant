"""
Color Identifier - Identifies dominant colors in images
"""

import cv2
import numpy as np
import logging
from typing import List
from sklearn.cluster import KMeans

from utils.logger import setup_logger


class ColorIdentifier:
    """
    Identifies dominant colors using K-means clustering
    """
    
    # Color name mapping (RGB)
    COLOR_NAMES = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (165, 42, 42),
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'gray': (128, 128, 128),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255)
    }
    
    def __init__(self, config):
        """
        Initialize color identifier
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('ColorIdentifier', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.method = config.get('color_identification.method', 'kmeans')
        self.num_colors = config.get('color_identification.num_colors', 3)
    
    def identify(self, image: np.ndarray) -> List[str]:
        """
        Identify dominant colors in image
        
        Args:
            image: Input image
            
        Returns:
            List of color names
        """
        try:
            # Resize image for faster processing
            small_image = cv2.resize(image, (150, 150))
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2RGB)
            
            # Reshape to list of pixels
            pixels = rgb_image.reshape(-1, 3)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=self.num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get cluster centers (dominant colors)
            dominant_colors = kmeans.cluster_centers_.astype(int)
            
            # Map to color names
            color_names = []
            for color in dominant_colors:
                name = self._get_color_name(tuple(color))
                color_names.append(name)
            
            self.logger.info(f"Identified colors: {color_names}")
            return color_names
            
        except Exception as e:
            self.logger.error(f"Error in color identification: {e}")
            return []
    
    def _get_color_name(self, rgb: tuple) -> str:
        """
        Get closest color name for RGB value
        
        Args:
            rgb: RGB tuple
            
        Returns:
            Color name
        """
        min_distance = float('inf')
        closest_color = 'unknown'
        
        for name, color_rgb in self.COLOR_NAMES.items():
            # Calculate Euclidean distance
            distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, color_rgb)))
            
            if distance < min_distance:
                min_distance = distance
                closest_color = name
        
        return closest_color
    
    def shutdown(self):
        """Cleanup resources"""
        self.logger.info("Color identifier shutdown")
