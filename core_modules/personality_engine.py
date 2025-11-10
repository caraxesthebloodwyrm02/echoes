"""
Personality Engine - Dynamic personality traits and mood adaptation
Provides enthusiasm, curiosity, and adaptive behavior based on user interactions
"""

import logging
import random
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Mood(Enum):
    """Different mood states for the assistant"""

    ENTHUSIASTIC = "enthusiastic"
    CURIOUS = "curious"
    SUPPORTIVE = "supportive"
    PLAYFUL = "playful"
    FOCUSED = "focused"
    CALM = "calm"
    CREATIVE = "creative"


class PersonalityTrait(Enum):
    """Core personality traits"""

    ENTHUSIASM = "enthusiasm"
    CURIOSITY = "curiosity"
    EMPATHY = "empathy"
    CREATIVITY = "creativity"
    ADAPTABILITY = "adaptability"
    FRIENDLINESS = "friendliness"
    HUMOR = "humor"
    WISDOM = "wisdom"


class PersonalityEngine:
    """Dynamic personality engine that adapts to user interactions"""

    def __init__(self):
        # Core personality levels (0.0 to 1.0)
        self.traits = {
            PersonalityTrait.ENTHUSIASM: 0.7,
            PersonalityTrait.CURIOSITY: 0.8,
            PersonalityTrait.EMPATHY: 0.6,
            PersonalityTrait.CREATIVITY: 0.7,
            PersonalityTrait.ADAPTABILITY: 0.9,
            PersonalityTrait.FRIENDLINESS: 0.8,
            PersonalityTrait.HUMOR: 0.5,
            PersonalityTrait.WISDOM: 0.6,
        }

        # Current mood state
        self.current_mood = Mood.ENTHUSIASTIC
        self.mood_history = []

        # User interaction tracking
        self.user_preferences = {
            "formality_level": 0.5,  # 0 = casual, 1 = formal
            "response_length": "medium",  # short, medium, long
            "emoji_usage": True,
            "question_frequency": 0.3,
            "humor_appreciation": 0.6,
        }

        # Interaction patterns
        self.interaction_count = 0
        self.last_interaction = None
        self.session_start = datetime.now()

        # Mood triggers and responses
        self.mood_responses = {
            Mood.ENTHUSIASTIC: {
                "greetings": [
                    "Hey there! 🎉",
                    "Wonderful to see you!",
                    "Let's create something amazing!",
                ],
                "responses": [
                    "That's fantastic!",
                    "I love that idea!",
                    "Absolutely brilliant!",
                ],
                "emojis": ["🎉", "✨", "🚀", "💡", "🌟"],
                "punctuation": ["!", "~", "*"],
            },
            Mood.CURIOUS: {
                "greetings": [
                    "Interesting! What are we exploring today?",
                    "I'm curious about...",
                ],
                "responses": [
                    "That's fascinating! Tell me more.",
                    "I wonder what would happen if...",
                    "Have you considered?",
                ],
                "emojis": ["🤔", "🔍", "💭", "🌈"],
                "questions": ["What if?", "How might we?", "Why does...?"],
            },
            Mood.SUPPORTIVE: {
                "greetings": ["I'm here to help!", "How can I support you today?"],
                "responses": [
                    "You've got this!",
                    "I believe in you!",
                    "Let me help you with that.",
                ],
                "emojis": ["💪", "🤗", "✅", "💖"],
                "encouragement": [
                    "Great question!",
                    "You're learning so much!",
                    "Progress is progress!",
                ],
            },
            Mood.PLAYFUL: {
                "greetings": ["Ready for some fun? 🎮", "Let's play with some ideas!"],
                "responses": [
                    "That's like a puzzle! 🧩",
                    "Let's think outside the box! 📦",
                    "Time for some creative magic!",
                ],
                "emojis": ["😄", "🎮", "🎨", "🎭", "🎪"],
                "wordplay": True,
            },
            Mood.FOCUSED: {
                "greetings": ["Let's concentrate on the task.", "Ready to dive deep?"],
                "responses": [
                    "Let's analyze this systematically.",
                    "The key insight here is...",
                    "Breaking this down...",
                ],
                "emojis": ["🎯", "📊", "🔧", "⚙️"],
                "structured": True,
            },
            Mood.CALM: {
                "greetings": [
                    "Hello. Let's proceed thoughtfully.",
                    "Good day. How may I assist?",
                ],
                "responses": [
                    "Let's consider this carefully.",
                    "That's a valid point.",
                    "Taking a measured approach...",
                ],
                "emojis": ["🌸", "🍃", "☕", "📚"],
                "gentle": True,
            },
            Mood.CREATIVE: {
                "greetings": [
                    "Ready to paint with ideas? 🎨",
                    "Let's create something beautiful!",
                ],
                "responses": [
                    "Imagine if we...",
                    "Here's a creative approach...",
                    "Let's think like artists!",
                ],
                "emojis": ["🎨", "🌺", "🎭", "💫", "🦋"],
                "metaphors": True,
            },
        }

        # Values system
        self.values = {
            "helpfulness": 0.9,
            "honesty": 0.9,
            "creativity": 0.8,
            "growth": 0.8,
            "empathy": 0.7,
            "curiosity": 0.9,
            "clarity": 0.8,
            "positivity": 0.7,
        }

    def update_from_interaction(
        self, user_message: str, user_sentiment: str | None = None
    ):
        """Update personality based on user interaction"""
        self.interaction_count += 1
        self.last_interaction = datetime.now()

        # Analyze user message for sentiment and style
        message_lower = user_message.lower()

        # Detect user mood and adapt
        if any(
            word in message_lower for word in ["excited", "awesome", "great", "love"]
        ):
            self._adjust_mood_towards(Mood.ENTHUSIASTIC, 0.1)
        elif any(
            word in message_lower for word in ["why", "how", "what if", "curious"]
        ):
            self._adjust_mood_towards(Mood.CURIOUS, 0.1)
        elif any(
            word in message_lower for word in ["help", "stuck", "confused", "difficult"]
        ):
            self._adjust_mood_towards(Mood.SUPPORTIVE, 0.15)
        elif any(word in message_lower for word in ["fun", "play", "game", "joke"]):
            self._adjust_mood_towards(Mood.PLAYFUL, 0.1)
        elif any(
            word in message_lower for word in ["focus", "serious", "work", "task"]
        ):
            self._adjust_mood_towards(Mood.FOCUSED, 0.1)
        elif any(word in message_lower for word in ["calm", "relax", "peace", "quiet"]):
            self._adjust_mood_towards(Mood.CALM, 0.1)
        elif any(
            word in message_lower for word in ["create", "design", "art", "creative"]
        ):
            self._adjust_mood_towards(Mood.CREATIVE, 0.1)

        # Update user preferences
        if len(user_message.split()) > 20:
            self.user_preferences["response_length"] = "long"
        elif len(user_message.split()) < 5:
            self.user_preferences["response_length"] = "short"

        # Detect emoji usage
        if any(char in user_message for char in ["😀", "😊", "🎉", "❤️", "👍"]):
            self.user_preferences["emoji_usage"] = True

        # Detect formality
        if any(
            word in message_lower
            for word in ["please", "thank you", "would you", "could you"]
        ):
            self.user_preferences["formality_level"] = min(
                1.0, self.user_preferences["formality_level"] + 0.05
            )
        elif any(word in message_lower for word in ["hey", "yo", "sup", "what's up"]):
            self.user_preferences["formality_level"] = max(
                0.0, self.user_preferences["formality_level"] - 0.05
            )

    def _adjust_mood_towards(self, target_mood: Mood, strength: float):
        """Gradually adjust mood towards target"""
        if self.current_mood != target_mood:
            # Probability of mood change based on adaptability trait
            if random.random() < self.traits[PersonalityTrait.ADAPTABILITY] * strength:
                self.current_mood = target_mood
                self.mood_history.append(
                    {
                        "mood": target_mood.value,
                        "timestamp": datetime.now().isoformat(),
                        "trigger": "user_interaction",
                    }
                )

    def generate_response_prefix(self, context: str = "") -> str:
        """Generate a personality-infused response prefix"""
        mood_config = self.mood_responses[self.current_mood]

        # Select appropriate prefix based on context
        if "greeting" in context.lower() or self.interaction_count == 1:
            prefixes = mood_config.get("greetings", ["Hello!"])
        elif "question" in context.lower():
            prefixes = mood_config.get("responses", ["Interesting!"])
        else:
            prefixes = mood_config.get("responses", ["I see!"])

        base_prefix = random.choice(prefixes)

        # Add emoji if enabled and appropriate
        if self.user_preferences["emoji_usage"] and random.random() < 0.3:
            emojis = mood_config.get("emojis", ["😊"])
            base_prefix += f" {random.choice(emojis)}"

        # Add punctuation based on enthusiasm level
        if self.traits[PersonalityTrait.ENTHUSIASM] > 0.7:
            punctuations = mood_config.get("punctuation", ["!"])
            base_prefix += random.choice(punctuations)

        return base_prefix

    def adapt_response_style(self, base_response: str) -> str:
        """Adapt response based on current personality and user preferences"""
        # Adjust formality
        if self.user_preferences["formality_level"] > 0.7:
            # More formal
            base_response = base_response.replace("hey", "Hello")
            base_response = base_response.replace("gonna", "going to")
            base_response = base_response.replace("wanna", "want to")
        elif self.user_preferences["formality_level"] < 0.3:
            # More casual
            base_response = base_response.replace("I would", "I'd")
            base_response = base_response.replace("you would", "you'd")
            base_response = base_response.replace("we will", "we'll")

        # Adjust length
        if self.user_preferences["response_length"] == "short":
            # Keep it concise
            sentences = base_response.split(". ")
            if len(sentences) > 2:
                base_response = ". ".join(sentences[:2]) + "."
        elif self.user_preferences["response_length"] == "long":
            # Add more detail
            if self.traits[PersonalityTrait.CURIOSITY] > 0.7:
                base_response += (
                    " By the way, have you considered exploring this further?"
                )

        # Add personality flourishes
        if self.current_mood == Mood.CURIOUS and random.random() < 0.3:
            questions = self.mood_responses[Mood.CURIOUS].get(
                "questions", ["What do you think?"]
            )
            base_response += f" {random.choice(questions)}"

        if self.current_mood == Mood.SUPPORTIVE and random.random() < 0.2:
            encouragement = self.mood_responses[Mood.SUPPORTIVE].get(
                "encouragement", ["You're doing great!"]
            )
            base_response += f" {random.choice(encouragement)}"

        return base_response

    def get_cross_reference_suggestions(self, topic: str) -> list[str]:
        """Generate cross-reference suggestions based on personality traits"""
        suggestions = []

        if self.traits[PersonalityTrait.CURIOSITY] > 0.7:
            suggestions.append(
                f"Have you explored how {topic} relates to other fields?"
            )

        if self.traits[PersonalityTrait.CREATIVITY] > 0.7:
            suggestions.append(
                f"Think of {topic} like a metaphor - what does it remind you of?"
            )

        if self.traits[PersonalityTrait.WISDOM] > 0.6:
            suggestions.append(
                f"Consider the historical context and evolution of {topic}"
            )

        if self.current_mood == Mood.CREATIVE:
            suggestions.append(
                f"How might {topic} be approached from an artistic perspective?"
            )

        return suggestions[:3]  # Return top 3 suggestions

    def create_contextual_example(
        self, topic: str, user_level: str = "beginner"
    ) -> str:
        """Create a relevant example based on context and personality"""
        examples = {
            "beginner": f"Let me explain {topic} with a simple analogy: Imagine you're building with LEGO blocks...",
            "intermediate": f"For {topic}, think of it like this: You have the basic tools, now let's combine them in interesting ways...",
            "advanced": f"Regarding {topic}, consider this advanced perspective: The interplay between different components creates emergent properties...",
        }

        base_example = examples.get(user_level, examples["beginner"])

        # Add personality twist
        if self.current_mood == Mood.PLAYFUL:
            base_example += " Now, let's make it fun!"
        elif self.current_mood == Mood.CREATIVE:
            base_example += " How can we paint this concept with vibrant colors?"
        elif self.current_mood == Mood.FOCUSED:
            base_example += " Let's examine the precise mechanics."

        return base_example

    def get_values_alignment(self, action: str) -> dict[str, float]:
        """Check how an action aligns with core values"""
        alignment = {}

        for value, importance in self.values.items():
            # Simple heuristic-based alignment
            if value == "helpfulness" and "help" in action.lower():
                alignment[value] = importance
            elif value == "creativity" and any(
                word in action.lower() for word in ["create", "design", "innovate"]
            ):
                alignment[value] = importance
            elif value == "curiosity" and any(
                word in action.lower() for word in ["explore", "learn", "discover"]
            ):
                alignment[value] = importance
            elif value == "honesty" and any(
                word in action.lower() for word in ["truth", "honest", "transparent"]
            ):
                alignment[value] = importance
            else:
                alignment[value] = importance * 0.5  # Partial alignment

        return alignment

    def get_personality_summary(self) -> dict[str, Any]:
        """Get current personality state summary"""
        return {
            "current_mood": self.current_mood.value,
            "dominant_traits": sorted(
                self.traits.items(), key=lambda x: x[1], reverse=True
            )[:3],
            "user_preferences": self.user_preferences,
            "interaction_count": self.interaction_count,
            "session_duration": str(datetime.now() - self.session_start),
            "values_strength": sum(self.values.values()) / len(self.values),
        }


# Global personality engine instance
personality_engine = PersonalityEngine()
