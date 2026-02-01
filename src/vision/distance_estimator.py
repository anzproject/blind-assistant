"""
Distance Estimator - Estimates distance to objects using depth estimation
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Optional

from utils.logger import setup_logger

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class DistanceEstimator:
    """
    Estimates distance to objects using monocular depth estimation
    """
    
    def __init__(self, config):
        """
        Initialize distance estimator
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('DistanceEstimator', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.model_name = config.get('distance_estimation.model', 'midas')
        self.method = config.get('distance_estimation.method', 'monocular')
        self.max_distance = config.get('distance_estimation.max_distance', 10)
        
        # Model
        self.model = None
        self.transform = None
        
        # Load model if using monocular method
        if self.method == 'monocular':
            self._load_model()
    
    def _load_model(self):
        """Load depth estimation model"""
        if not TORCH_AVAILABLE:
            self.logger.warning("PyTorch not installed. Using heuristic method.")
            self.method = 'heuristic'
            return
        
        try:
            self.logger.info(f"Loading depth model: {self.model_name}")
            
            if self.model_name == 'midas':
                # Load MiDaS model
                self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
                midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
                self.transform = midas_transforms.small_transform
            else:
                self.logger.warning(f"Unknown model: {self.model_name}. Using heuristic method.")
                self.method = 'heuristic'
                return
            
            # Set to eval mode
            self.model.eval()
            
            # Move to device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(device)
            
            self.logger.info(f"Depth model loaded on {device}")
            
        except Exception as e:
            self.logger.error(f"Failed to load depth model: {e}")
            self.method = 'heuristic'
    
    def estimate(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> List[float]:
        """
        Estimate distances to detected objects
        
        Args:
            image: Input image
            detections: List of object detections with bounding boxes
            
        Returns:
            List of distances in meters
        """
        if self.method == 'monocular' and self.model is not None:
            return self._estimate_monocular(image, detections)
        else:
            return self._estimate_heuristic(image, detections)
    
    def _estimate_monocular(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> List[float]:
        """Estimate distance using monocular depth estimation"""
        try:
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Transform image
            input_batch = self.transform(rgb_image)
            
            # Move to device
            device = next(self.model.parameters()).device
            input_batch = input_batch.to(device)
            
            # Predict depth
            with torch.no_grad():
                prediction = self.model(input_batch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=rgb_image.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
            
            depth_map = prediction.cpu().numpy()
            
            # Normalize depth map
            depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
            
            # Get distance for each detection
            distances = []
            for det in detections:
                bbox = det['bbox']
                
                # Get center of bounding box
                center_x = (bbox['x1'] + bbox['x2']) // 2
                center_y = (bbox['y1'] + bbox['y2']) // 2
                
                # Get depth value at center
                depth_value = depth_map[center_y, center_x]
                
                # Convert to distance (inverse relationship)
                # This is a rough approximation
                distance = self.max_distance * (1 - depth_value)
                distances.append(distance)
            
            return distances
            
        except Exception as e:
            self.logger.error(f"Error in monocular estimation: {e}")
            return self._estimate_heuristic(image, detections)
    
    def _estimate_heuristic(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> List[float]:
        """
        Estimate distance using heuristic based on object size
        
        This is a rough approximation based on the assumption that
        larger objects in the image are closer to the camera.
        """
        distances = []
        
        image_height = image.shape[0]
        
        for det in detections:
            bbox = det['bbox']
            
            # Calculate bounding box height
            bbox_height = bbox['y2'] - bbox['y1']
            
            # Estimate distance based on bbox height
            # Larger bbox = closer object
            # This is a very rough heuristic
            if bbox_height > 0:
                # Normalize by image height
                height_ratio = bbox_height / image_height
                
                # Inverse relationship: larger ratio = closer
                distance = self.max_distance * (1 - min(height_ratio, 1.0))
                
                # Ensure minimum distance
                distance = max(distance, 0.5)
            else:
                distance = self.max_distance
            
            distances.append(distance)
        
        return distances
    
    def shutdown(self):
        """Cleanup resources"""
        if self.model is not None:
            del self.model
            del self.transform
        self.logger.info("Distance estimator shutdown")
