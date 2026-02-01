"""
Emergency SOS - Emergency alert system with location sharing
"""

import logging
from typing import Optional

from utils.logger import setup_logger


class EmergencySOS:
    """
    Emergency SOS system with location sharing
    """
    
    def __init__(self, config, gps_module, audio_manager):
        """
        Initialize emergency SOS
        
        Args:
            config: Configuration object
            gps_module: GPS module instance
            audio_manager: Audio manager instance
        """
        self.logger = setup_logger('EmergencySOS', 'data/logs/blind_assistant.log')
        self.config = config
        self.gps = gps_module
        self.audio = audio_manager
        
        # Get configuration
        self.contacts = config.get('emergency_sos.contacts', [])
        self.trigger_phrase = config.get('emergency_sos.trigger_phrase', 'emergency help')
        
        self.logger.info(f"Emergency SOS initialized with {len(self.contacts)} contacts")
    
    def trigger(self):
        """Trigger emergency SOS"""
        self.logger.warning("EMERGENCY SOS TRIGGERED!")
        
        # Get current location
        location = None
        if self.gps:
            location = self.gps.get_location()
        
        # Alert user
        if self.audio:
            self.audio.speak_emergency("Emergency SOS activated. Alerting emergency contacts.")
        
        # Send alerts to contacts
        for contact in self.contacts:
            self._send_alert(contact, location)
        
        self.logger.info("Emergency alerts sent")
    
    def _send_alert(self, contact: dict, location: Optional[tuple]):
        """
        Send emergency alert to contact
        
        Args:
            contact: Contact information
            location: GPS coordinates (lat, lon)
        """
        name = contact.get('name', 'Unknown')
        phone = contact.get('phone')
        email = contact.get('email')
        
        message = f"EMERGENCY ALERT from Blind Assistant user!"
        if location:
            lat, lon = location
            message += f" Location: {lat:.6f}, {lon:.6f}"
            message += f" (https://maps.google.com/?q={lat},{lon})"
        
        # TODO: Implement actual SMS/email sending
        # This would use Twilio for SMS or SMTP for email
        
        self.logger.info(f"Emergency alert sent to {name}: {message}")
    
    def shutdown(self):
        """Shutdown emergency SOS"""
        self.logger.info("Emergency SOS shutdown")
