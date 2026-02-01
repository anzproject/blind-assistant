"""
Audio Manager - Manages audio output and prioritization
"""

import logging
import queue
import threading
from typing import Optional

from utils.logger import setup_logger


class AudioManager:
    """
    Manages audio output with priority queue
    """
    
    def __init__(self, config, tts_engine):
        """
        Initialize audio manager
        
        Args:
            config: Configuration object
            tts_engine: Text-to-speech engine instance
        """
        self.logger = setup_logger('AudioManager', 'data/logs/blind_assistant.log')
        self.config = config
        self.tts = tts_engine
        
        # Audio queue (priority, message)
        self.audio_queue = queue.PriorityQueue()
        
        # Worker thread
        self.running = False
        self.worker_thread = None
        
        # Priority levels
        self.PRIORITY_EMERGENCY = 0
        self.PRIORITY_HIGH = 1
        self.PRIORITY_NORMAL = 2
        self.PRIORITY_LOW = 3
        
        # Start worker
        self._start_worker()
    
    def _start_worker(self):
        """Start audio worker thread"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.worker_thread.start()
        self.logger.info("Audio worker started")
    
    def _audio_worker(self):
        """Audio worker thread that processes queue"""
        while self.running:
            try:
                # Get next item from queue (blocks with timeout)
                priority, text = self.audio_queue.get(timeout=0.5)
                
                # Speak the text
                self.tts.speak(text, blocking=True)
                
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in audio worker: {e}")
    
    def speak(self, text: str, priority: int = None):
        """
        Queue text for speech
        
        Args:
            text: Text to speak
            priority: Priority level (0=highest, 3=lowest)
        """
        if priority is None:
            priority = self.PRIORITY_NORMAL
        
        self.audio_queue.put((priority, text))
        self.logger.debug(f"Queued audio (priority {priority}): {text[:50]}...")
    
    def speak_emergency(self, text: str):
        """Speak with emergency priority"""
        self.speak(text, self.PRIORITY_EMERGENCY)
    
    def speak_high(self, text: str):
        """Speak with high priority"""
        self.speak(text, self.PRIORITY_HIGH)
    
    def speak_low(self, text: str):
        """Speak with low priority"""
        self.speak(text, self.PRIORITY_LOW)
    
    def clear_queue(self):
        """Clear all pending audio"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()
            except queue.Empty:
                break
        
        self.logger.info("Audio queue cleared")
    
    def stop_current(self):
        """Stop current speech"""
        self.tts.stop()
    
    def shutdown(self):
        """Shutdown audio manager"""
        self.logger.info("Shutting down audio manager...")
        self.running = False
        
        # Wait for worker to finish
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        
        # Clear queue
        self.clear_queue()
        
        self.logger.info("Audio manager shutdown")
