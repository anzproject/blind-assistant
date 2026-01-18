"""
Emotion-Aware Interaction module for AI Blind Assistant.
Adapts responses based on detected emotions and user context.
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional
import time
from collections import deque

logger = logging.getLogger(__name__)

class EmotionAwareAssistant:
    def __init__(self, vision_processor, audio_processor):
        self.vision = vision_processor
        self.audio = audio_processor
        self.emotion_history = deque(maxlen=10)  # Keep last 10 emotion readings
        self.user_mood = "neutral"
        self.interaction_context = {}
        self.adaptation_rules = self._load_adaptation_rules()

    def _load_adaptation_rules(self) -> Dict[str, Dict]:
        """Load rules for adapting responses based on emotions."""
        return {
            "happy": {
                "voice_rate": 1.2,  # Slightly faster speech
                "tone": "enthusiastic",
                "responses": [
                    "I'm glad you're feeling positive!",
                    "That's wonderful to hear!",
                    "Let's keep that great energy going!"
                ]
            },
            "sad": {
                "voice_rate": 0.8,  # Slower, more comforting speech
                "tone": "gentle",
                "responses": [
                    "I'm here to help you through this.",
                    "Take your time, I'm not going anywhere.",
                    "Would you like me to guide you to a familiar place?"
                ]
            },
            "angry": {
                "voice_rate": 0.9,  # Calm, measured speech
                "tone": "calm",
                "responses": [
                    "I understand this is frustrating. Let's work through it together.",
                    "Take a deep breath. I'm here to help.",
                    "Let's focus on what we can do right now."
                ]
            },
            "fearful": {
                "voice_rate": 0.85,  # Slow, reassuring speech
                "tone": "reassuring",
                "responses": [
                    "You're safe with me. I won't let anything happen to you.",
                    "Let's stay calm and take this step by step.",
                    "I'm right here beside you."
                ]
            },
            "surprised": {
                "voice_rate": 1.1,  # Slightly faster, excited speech
                "tone": "excited",
                "responses": [
                    "Oh! That's unexpected!",
                    "Wow, that caught me off guard too!",
                    "Let's figure this out together!"
                ]
            },
            "neutral": {
                "voice_rate": 1.0,  # Normal speech rate
                "tone": "neutral",
                "responses": [
                    "I understand.",
                    "Let me help you with that.",
                    "How can I assist you?"
                ]
            }
        }

    def analyze_emotion(self, frame) -> Optional[str]:
        """Analyze emotion from facial expression in frame."""
        try:
            emotion = self.vision.detect_emotion(frame)
            if emotion:
                self.emotion_history.append(emotion)
                # Determine dominant emotion from recent history
                self.user_mood = self._get_dominant_emotion()
            return emotion
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return None

    def _get_dominant_emotion(self) -> str:
        """Get the most frequent emotion in recent history."""
        if not self.emotion_history:
            return "neutral"

        emotion_counts = {}
        for emotion in self.emotion_history:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        return max(emotion_counts, key=emotion_counts.get)

    def adapt_response(self, base_response: str, emotion: Optional[str] = None) -> str:
        """Adapt response based on user's emotional state."""
        if not emotion:
            emotion = self.user_mood

        rules = self.adaptation_rules.get(emotion, self.adaptation_rules["neutral"])

        # Add emotional prefix
        emotional_prefix = np.random.choice(rules["responses"])

        # Adapt voice settings
        self._adapt_voice_settings(rules)

        return f"{emotional_prefix} {base_response}"

    def _adapt_voice_settings(self, rules: Dict):
        """Adapt voice settings based on emotion."""
        try:
            # Adjust speech rate
            rate_multiplier = rules["voice_rate"]
            current_rate = self.audio.tts_engine.getProperty('rate')
            new_rate = int(current_rate * rate_multiplier)
            self.audio.tts_engine.setProperty('rate', new_rate)

            # Could also adjust volume, voice selection, etc.
        except Exception as e:
            logger.error(f"Voice adaptation failed: {e}")

    def provide_emotional_support(self) -> str:
        """Provide emotional support based on detected mood."""
        emotion = self.user_mood
        support_messages = {
            "happy": "I'm sensing you're in a good mood! That's wonderful. How can I enhance your day?",
            "sad": "I can tell you're feeling down. Remember that it's okay to feel this way. I'm here for you.",
            "angry": "I sense some frustration. Let's take a moment to breathe and approach this calmly.",
            "fearful": "You seem anxious. You're safe, and I'm here to help you navigate safely.",
            "surprised": "You look surprised! Life is full of unexpected moments. How can I help?",
            "neutral": "I'm here whenever you need assistance."
        }

        return support_messages.get(emotion, support_messages["neutral"])

    def learn_user_preferences(self, command: str, emotion: str):
        """Learn user preferences based on commands and emotional responses."""
        # Simple learning mechanism
        if command not in self.interaction_context:
            self.interaction_context[command] = {"count": 0, "emotions": []}

        self.interaction_context[command]["count"] += 1
        self.interaction_context[command]["emotions"].append(emotion)

        # Keep only recent interactions
        if len(self.interaction_context[command]["emotions"]) > 5:
            self.interaction_context[command]["emotions"].pop(0)

    def suggest_helpful_actions(self) -> List[str]:
        """Suggest actions based on user's emotional state and context."""
        suggestions = []

        if self.user_mood == "sad":
            suggestions.extend([
                "Would you like me to play some uplifting music?",
                "I can guide you to a favorite location for comfort.",
                "Let's try a relaxation exercise together."
            ])
        elif self.user_mood == "angry":
            suggestions.extend([
                "Let's take a walk to clear your mind.",
                "I can help you find a quiet space.",
                "Would you like to talk about what's bothering you?"
            ])
        elif self.user_mood == "fearful":
            suggestions.extend([
                "Stay close to me, I'll guide you safely.",
                "Let's move to a more familiar area.",
                "I can provide constant audio feedback for reassurance."
            ])
        elif self.user_mood == "happy":
            suggestions.extend([
                "Let's explore something new together!",
                "Would you like to visit a favorite place?",
                "I can share some interesting facts or jokes."
            ])

        # Context-based suggestions
        if "location" in str(self.interaction_context.keys()):
            suggestions.append("Since you've asked about locations before, would you like navigation help?")

        return suggestions[:3]  # Limit to 3 suggestions

    def get_mood_summary(self) -> str:
        """Provide a summary of user's current emotional state."""
        if not self.emotion_history:
            return "I haven't detected any emotions yet."

        emotion_counts = {}
        for emotion in self.emotion_history:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        total = len(self.emotion_history)
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        percentage = (emotion_counts[dominant_emotion] / total) * 100

        return f"You've been mostly {dominant_emotion} ({percentage:.0f}%) in our recent interactions."

    def emergency_emotion_detection(self) -> bool:
        """Detect if user is in emotional distress requiring immediate attention."""
        if len(self.emotion_history) < 3:
            return False

        recent_emotions = list(self.emotion_history)[-3:]
        distress_emotions = ["fearful", "angry", "sad"]

        distress_count = sum(1 for emotion in recent_emotions if emotion in distress_emotions)

        # If 3 out of last 3 emotions are distress emotions, flag as emergency
        return distress_count >= 2
