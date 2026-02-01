"""
Object Detector - Detects objects in images using YOLO
"""

import cv2
import numpy as np
from typing import List, Dict, Any
import logging

from utils.logger import setup_logger

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class ObjectDetector:
    """
    Object detection using YOLOv8/v9
    """
    
    def __init__(self, config):
        """
        Initialize object detector
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('ObjectDetector', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.model_name = config.get('object_detection.model', 'yolov8n')
        self.confidence_threshold = config.get('object_detection.confidence_threshold', 0.5)
        self.iou_threshold = config.get('object_detection.iou_threshold', 0.45)
        self.max_detections = config.get('object_detection.max_detections', 10)
        self.device = config.get('object_detection.device', 'cpu')
        
        # Load model
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model"""
        if not YOLO_AVAILABLE:
            self.logger.error("Ultralytics YOLO not installed. Install with: pip install ultralytics")
            return
        
        try:
            self.logger.info(f"Loading YOLO model: {self.model_name}")
            self.model = YOLO(f"{self.model_name}.pt")
            self.logger.info("YOLO model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {e}")
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect objects in image
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detections with class, confidence, and bounding box
        """
        if self.model is None:
            self.logger.warning("Model not loaded, returning empty detections")
            return []
        
        try:
            # Run inference
            results = self.model(
                image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                device=self.device,
                verbose=False
            )
            
            # Parse results
            detections = []
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get box data
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy()
                    
                    # Get class name
                    class_name = result.names[cls]
                    
                    detection = {
                        'class': class_name,
                        'confidence': conf,
                        'bbox': {
                            'x1': int(xyxy[0]),
                            'y1': int(xyxy[1]),
                            'x2': int(xyxy[2]),
                            'y2': int(xyxy[3])
                        }
                    }
                    
                    detections.append(detection)
                    
                    # Limit number of detections
                    if len(detections) >= self.max_detections:
                        break
            
            self.logger.info(f"Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            self.logger.error(f"Error during object detection: {e}", exc_info=True)
            return []
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw bounding boxes on image
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            Image with drawn bounding boxes
        """
        output = image.copy()
        
        for det in detections:
            bbox = det['bbox']
            class_name = det['class']
            confidence = det['confidence']
            
            # Draw rectangle
            cv2.rectangle(
                output,
                (bbox['x1'], bbox['y1']),
                (bbox['x2'], bbox['y2']),
                (0, 255, 0),
                2
            )
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            cv2.putText(
                output,
                label,
                (bbox['x1'], bbox['y1'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        return output
    
    def shutdown(self):
        """Cleanup resources"""
        self.logger.info("Object detector shutdown")
