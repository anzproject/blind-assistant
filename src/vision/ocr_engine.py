"""
OCR Engine - Extracts text from images
"""

import cv2
import numpy as np
import logging
from typing import Optional

from utils.logger import setup_logger

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCREngine:
    """
    Optical Character Recognition for text extraction
    """
    
    def __init__(self, config):
        """
        Initialize OCR engine
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('OCREngine', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.engine = config.get('ocr.engine', 'easyocr')
        self.languages = config.get('ocr.languages', ['en'])
        self.gpu = config.get('ocr.gpu', False)
        
        # Initialize reader
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize OCR reader"""
        if self.engine == 'easyocr':
            if not EASYOCR_AVAILABLE:
                self.logger.error("EasyOCR not installed. Install with: pip install easyocr")
                return
            
            try:
                self.logger.info(f"Initializing EasyOCR with languages: {self.languages}")
                self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
                self.logger.info("EasyOCR initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize EasyOCR: {e}")
        
        elif self.engine == 'tesseract':
            if not TESSERACT_AVAILABLE:
                self.logger.error("Tesseract not installed. Install with: pip install pytesseract")
                return
            
            self.logger.info("Using Tesseract OCR")
            self.reader = 'tesseract'
    
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from image
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Extracted text
        """
        if self.reader is None:
            self.logger.warning("OCR reader not initialized")
            return ""
        
        try:
            if self.engine == 'easyocr':
                return self._extract_easyocr(image)
            elif self.engine == 'tesseract':
                return self._extract_tesseract(image)
            else:
                return ""
        except Exception as e:
            self.logger.error(f"Error during text extraction: {e}", exc_info=True)
            return ""
    
    def _extract_easyocr(self, image: np.ndarray) -> str:
        """Extract text using EasyOCR"""
        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Read text
        results = self.reader.readtext(rgb_image)
        
        # Combine all text
        text_parts = [result[1] for result in results]
        text = ' '.join(text_parts)
        
        self.logger.info(f"Extracted text: {text[:100]}...")
        return text
    
    def _extract_tesseract(self, image: np.ndarray) -> str:
        """Extract text using Tesseract"""
        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract text
        text = pytesseract.image_to_string(thresh)
        
        self.logger.info(f"Extracted text: {text[:100]}...")
        return text.strip()
    
    def shutdown(self):
        """Cleanup resources"""
        self.logger.info("OCR engine shutdown")
