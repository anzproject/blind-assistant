"""
Haptic Feedback - Vibration motor control for tactile alerts
"""

import logging
import time
from typing import List
from utils.logger import setup_logger

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class HapticFeedback:
    """
    Haptic feedback using vibration motors
    """
    
    def __init__(self, config):
        """
        Initialize haptic feedback
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('HapticFeedback', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.motor_pin = config.get('haptic_feedback.motor_pin', 18)
        self.patterns = config.get('haptic_feedback.patterns', {})
        
        # Initialize GPIO
        self._initialize()
    
    def _initialize(self):
        """Initialize GPIO for vibration motor"""
        if not GPIO_AVAILABLE:
            self.logger.warning("RPi.GPIO not available. Using simulated haptic feedback.")
            return
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.motor_pin, GPIO.OUT)
            self.logger.info("Haptic feedback initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize haptic feedback: {e}")
    
    def vibrate(self, pattern: List[int]):
        """
        Vibrate with pattern
        
        Args:
            pattern: List of durations in milliseconds (on, off, on, off, ...)
        """
        if not GPIO_AVAILABLE:
            self.logger.info(f"Simulated vibration: {pattern}")
            return
        
        try:
            for i, duration in enumerate(pattern):
                if i % 2 == 0:
                    # On
                    GPIO.output(self.motor_pin, GPIO.HIGH)
                else:
                    # Off
                    GPIO.output(self.motor_pin, GPIO.LOW)
                
                time.sleep(duration / 1000.0)
            
            # Ensure motor is off
            GPIO.output(self.motor_pin, GPIO.LOW)
            
        except Exception as e:
            self.logger.error(f"Error in haptic feedback: {e}")
    
    def obstacle_alert(self):
        """Alert for nearby obstacle"""
        pattern = self.patterns.get('obstacle_near', [200, 100, 200])
        self.vibrate(pattern)
    
    def navigation_alert(self):
        """Alert for navigation turn"""
        pattern = self.patterns.get('navigation_turn', [500])
        self.vibrate(pattern)
    
    def emergency_alert(self):
        """Alert for emergency"""
        pattern = self.patterns.get('emergency', [1000, 500, 1000, 500, 1000])
        self.vibrate(pattern)
    
    def shutdown(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE:
            GPIO.cleanup()
        self.logger.info("Haptic feedback shutdown")
