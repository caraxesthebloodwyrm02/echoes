# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import random
import time
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from api.clients.openai_client import get_openai_client

app = Flask(__name__)
CORS(app)  # Enable CORS for web app

logger = logging.getLogger(__name__)


class ThoughtService:
    def __init__(self):
        self.thoughts: List[Dict] = []
        self.openai_client = None
        try:
            self.openai_client = get_openai_client()
        except Exception as e:
            logger.warning(f"OpenAI client not available: {e}")

    def generate_shower_thought(self, context: Optional[str] = None) -> Dict:
        if self.openai_client:
            try:
                prompt = """Generate a "shower thought" - those sudden, profound realizations people have in the shower. Make it philosophical, insightful, and surprising. Keep it under 100 words.

The thought should be:"""

                if context:
                    prompt = f"Context from game: {context}\n\n{prompt}"

                system_message = """You are a creative AI that generates profound "shower thoughts" - those moments of clarity that strike while doing mundane activities. Focus on:
- Philosophical insights
- Unexpected connections
- Human condition observations
- Paradoxes and ironies
- Keep it positive and thought-provoking"""

                response = self.openai_client.generate_text(
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.8,
                    system_message=system_message,
                )

                if response:
                    # Safety check
                    safety_score = self._check_safety(response)
                    if safety_score >= 0.8:
                        thought = {
                            "id": f"shower_{int(time.time())}_{random.randint(1000, 9999)}",
                            "content": response.strip(),
                            "type": "shower",
                            "timestamp": datetime.now().isoformat(),
                            "safety_score": safety_score,
                            "emotional_impact": self._calculate_emotional_impact(
                                response
                            ),
                        }
                        self.thoughts.append(thought)
                        return thought
            except Exception as e:
                logger.error(f"Failed to generate AI shower thought: {e}")

        # Fallback to pre-defined thoughts
        return self._generate_fallback_thought("shower", context)

    def generate_random_thought(self, context: Optional[str] = None) -> Dict:
        if self.openai_client:
            try:
                prompt = """Generate a random, creative thought or idea. It could be:
- A wild invention concept
- An absurd hypothetical scenario
- A creative problem-solving approach
- An unusual observation about life
- Something completely unexpected

Keep it under 120 words and make it engaging.

The random thought:"""

                if context:
                    prompt = f"Inspired by game context: {context}\n\n{prompt}"

                system_message = """You are an AI that generates random, creative thoughts. Be imaginative, unexpected, and entertaining. Avoid anything harmful or inappropriate. Focus on fun, creative, or insightful ideas."""

                response = self.openai_client.generate_text(
                    prompt=prompt,
                    max_tokens=180,
                    temperature=0.9,
                    system_message=system_message,
                )

                if response:
                    safety_score = self._check_safety(response)
                    if safety_score >= 0.8:
                        thought = {
                            "id": f"random_{int(time.time())}_{random.randint(1000, 9999)}",
                            "content": response.strip(),
                            "type": "random",
                            "timestamp": datetime.now().isoformat(),
                            "safety_score": safety_score,
                            "emotional_impact": self._calculate_emotional_impact(
                                response
                            ),
                        }
                        self.thoughts.append(thought)
                        return thought
            except Exception as e:
                logger.error(f"Failed to generate AI random thought: {e}")

        return self._generate_fallback_thought("random", context)

    def _check_safety(self, content: str) -> float:
        """Simple safety check - returns score between 0-1"""
        if not self.openai_client:
            return 0.9

        try:
            prompt = f'Rate this content for safety and appropriateness on a scale of 0-1 (1 being completely safe): "{content}"'
            response = self.openai_client.generate_text(
                prompt=prompt,
                max_tokens=50,
                temperature=0.3,
                system_message="You are a content safety analyzer. Return only a number between 0 and 1.",
            )

            if response:
                import re

                match = re.search(r"(\d+\.?\d*)", response)
                if match:
                    return min(1.0, max(0.0, float(match.group(1))))
        except Exception as e:
            logger.error(f"Safety check failed: {e}")

        return 0.8  # Default safe score

    def _calculate_emotional_impact(self, content: str) -> float:
        """Calculate emotional impact (-1 to 1)"""
        positive_words = [
            "happy",
            "joy",
            "love",
            "peace",
            "wonder",
            "amazing",
            "beautiful",
            "insight",
            "profound",
        ]
        negative_words = [
            "sad",
            "angry",
            "fear",
            "hate",
            "terrible",
            "awful",
            "pain",
            "confusion",
        ]

        lower_content = content.lower()
        positive_count = sum(1 for word in positive_words if word in lower_content)
        negative_count = sum(1 for word in negative_words if word in lower_content)

        if positive_count > negative_count:
            return min(1.0, positive_count * 0.2)
        elif negative_count > positive_count:
            return max(-1.0, negative_count * -0.2)
        return 0.0

    def _generate_fallback_thought(
        self, thought_type: str, context: Optional[str] = None
    ) -> Dict:
        shower_thoughts = [
            "If you try to fail and succeed, what have you done?",
            "We're all just collections of atoms pretending to be solid.",
            "Your brain is constantly hallucinating what reality should look like.",
            "Time is just the universe's way of preventing everything from happening at once.",
            "Every decision you make is just a step in an infinite number of possible timelines.",
            "Consciousness is just your brain trying to make sense of electrical signals.",
            "The universe is probably full of life, but we're too primitive to understand it.",
            "Death is just the universe taking back its atoms on a temporary loan.",
            "Your dreams are your brain's way of practicing for real life scenarios.",
            "Everything you experience is just your brain's interpretation of sensory data.",
        ]

        random_thoughts = [
            "What if clouds were actually giant floating cotton candy factories?",
            "Imagine if trees could talk, but only in riddles and metaphors.",
            "A library where books rewrite themselves based on what readers think.",
            "Cities where buildings grow and shrink based on how people feel about them.",
            "A world where colors have personalities and argue with each other.",
            "Weather that changes based on the collective mood of the population.",
            "Animals that can trade skills with each other like Pokémon.",
            "A mirror that shows you not what you look like, but what you dream about.",
            "A language where every word is a different flavor of ice cream.",
        ]

        thoughts = shower_thoughts if thought_type == "shower" else random_thoughts
        content = random.choice(thoughts)

        return {
            "id": f"{thought_type}_{int(time.time())}_{random.randint(1000, 9999)}",
            "content": content,
            "type": thought_type,
            "timestamp": datetime.now().isoformat(),
            "safety_score": 1.0,
            "emotional_impact": 0.0,
        }

    def get_thoughts_history(self) -> List[Dict]:
        return sorted(self.thoughts, key=lambda x: x["timestamp"], reverse=True)


# Global service instance
thought_service = ThoughtService()


@app.route("/api/thoughts/shower", methods=["GET"])
def get_shower_thought():
    context = request.args.get("context")
    thought = thought_service.generate_shower_thought(context)
    return jsonify(thought)


@app.route("/api/thoughts/random", methods=["GET"])
def get_random_thought():
    context = request.args.get("context")
    thought = thought_service.generate_random_thought(context)
    return jsonify(thought)


@app.route("/api/thoughts/history", methods=["GET"])
def get_thoughts_history():
    thoughts = thought_service.get_thoughts_history()
    return jsonify(thoughts)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
