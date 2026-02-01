"""
Scene Describer - Generates natural language descriptions of scenes
Supports both online (GPT-4o) and offline (BLIP-2) modes
"""

import cv2
import numpy as np
import base64
import logging
from typing import Optional
from io import BytesIO
from PIL import Image

from utils.logger import setup_logger

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class SceneDescriber:
    """
    Generates scene descriptions using online or offline models
    """
    
    def __init__(self, config):
        """
        Initialize scene describer
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('SceneDescriber', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.online_model = config.get('scene_description.online_model', 'gpt-4o')
        self.offline_model_name = config.get('scene_description.offline_model', 'blip2')
        self.mode = config.get('scene_description.mode', 'auto')
        self.max_tokens = config.get('scene_description.max_tokens', 150)
        self.temperature = config.get('scene_description.temperature', 0.7)
        
        # API key
        self.api_key = config.get('api_keys.openai_api_key', '')
        
        # Models
        self.offline_model = None
        self.offline_processor = None
        
        # Load offline model if needed
        if self.mode in ['offline', 'auto']:
            self._load_offline_model()
    
    def _load_offline_model(self):
        """Load offline BLIP-2 model"""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers not installed. Offline mode unavailable.")
            return
        
        try:
            self.logger.info(f"Loading offline model: {self.offline_model_name}")
            
            if self.offline_model_name == 'blip2':
                model_id = "Salesforce/blip-image-captioning-large"
            else:
                model_id = "Salesforce/blip-image-captioning-base"
            
            self.offline_processor = BlipProcessor.from_pretrained(model_id)
            self.offline_model = BlipForConditionalGeneration.from_pretrained(model_id)
            
            # Move to CPU (or GPU if available)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.offline_model.to(device)
            
            self.logger.info(f"Offline model loaded on {device}")
            
        except Exception as e:
            self.logger.error(f"Failed to load offline model: {e}")
    
    def describe(self, image: np.ndarray) -> str:
        """
        Generate scene description
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Scene description text
        """
        # Determine which mode to use
        if self.mode == 'online':
            return self._describe_online(image)
        elif self.mode == 'offline':
            return self._describe_offline(image)
        else:  # auto mode
            # Try online first, fallback to offline
            try:
                return self._describe_online(image)
            except Exception as e:
                self.logger.warning(f"Online description failed: {e}. Falling back to offline.")
                return self._describe_offline(image)
    
    def _describe_online(self, image: np.ndarray) -> str:
        """
        Generate description using OpenAI GPT-4o
        
        Args:
            image: Input image
            
        Returns:
            Description text
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            # Convert image to base64
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Call OpenAI API
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.online_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this scene in detail for a visually impaired person. Focus on important objects, people, and spatial relationships. Be concise but informative."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            description = response.choices[0].message.content
            self.logger.info("Online scene description generated")
            return description
            
        except Exception as e:
            self.logger.error(f"Error in online description: {e}")
            raise
    
    def _describe_offline(self, image: np.ndarray) -> str:
        """
        Generate description using offline BLIP model
        
        Args:
            image: Input image
            
        Returns:
            Description text
        """
        if self.offline_model is None:
            return "Offline scene description is not available."
        
        try:
            # Convert to RGB PIL image
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Process image
            inputs = self.offline_processor(pil_image, return_tensors="pt")
            
            # Move to same device as model
            device = next(self.offline_model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate caption
            with torch.no_grad():
                outputs = self.offline_model.generate(
                    **inputs,
                    max_length=self.max_tokens,
                    num_beams=5,
                    temperature=self.temperature
                )
            
            description = self.offline_processor.decode(outputs[0], skip_special_tokens=True)
            
            self.logger.info("Offline scene description generated")
            return description
            
        except Exception as e:
            self.logger.error(f"Error in offline description: {e}")
            return "Unable to generate scene description."
    
    def shutdown(self):
        """Cleanup resources"""
        if self.offline_model is not None:
            del self.offline_model
            del self.offline_processor
        self.logger.info("Scene describer shutdown")
