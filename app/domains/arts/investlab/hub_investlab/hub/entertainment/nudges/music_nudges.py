#!/usr/bin/env python3
"""
Music Nudges Utility - Accessible from all modules for guidance and feedback
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MusicNudges:
    """Music-based nudges system for guidance and feedback"""

    def __init__(self):
        self.spotify_account = os.getenv("SPOTIFY_ACCOUNT", "irfankabir02@gmail.com")
        self.nudges_db = self.load_nudges_database()
        self.session_history = []

    def load_nudges_database(self) -> Dict[str, Dict[str, Any]]:
        """Load the nudges database"""
        return {
            "direction": {
                "songs": [
                    {
                        "title": "Bohemian Rhapsody",
                        "artist": "Queen",
                        "spotify_uri": "spotify:track:1AhDOtG9vPSOmsWgNW0BEY",
                        "message": "Is this the real life? Is this just fantasy?",
                        "context": "When questioning the path forward",
                    },
                    {
                        "title": "Eye of the Tiger",
                        "artist": "Survivor",
                        "spotify_uri": "spotify:track:2KH16Wvcicr2C2Pq0o8fr",
                        "message": "Rising up to the challenge of our rival",
                        "context": "When facing challenges or competition",
                    },
                    {
                        "title": "Don't Stop Believin'",
                        "artist": "Journey",
                        "spotify_uri": "spotify:track:4bHsxqR3GMrXTxEPLuK3I",
                        "message": "Don't stop believin', hold on to that feelin'",
                        "context": "When perseverance is needed",
                    },
                ],
                "description": "Guidance for direction and decision making",
            },
            "motivation": {
                "songs": [
                    {
                        "title": "Stronger",
                        "artist": "Kanye West",
                        "spotify_uri": "spotify:track:4fzsfWzRhPawzqhXbQ8Ey",
                        "message": "That that don't kill me can only make me stronger",
                        "context": "When overcoming obstacles",
                    },
                    {
                        "title": "Hall of Fame",
                        "artist": "The Script ft. will.i.am",
                        "spotify_uri": "spotify:track:7wMq5n8mYSKlQIGECKUg",
                        "message": "Do it for your people, do it for your pride",
                        "context": "When striving for excellence",
                    },
                    {
                        "title": "Unstoppable",
                        "artist": "Sia",
                        "spotify_uri": "spotify:track:1yvMUkIOTeUNtNWlWRgB",
                        "message": "I'm unstoppable, I'm a Porsche with no brakes",
                        "context": "When feeling powerful and determined",
                    },
                ],
                "description": "Motivation and empowerment",
            },
            "reflection": {
                "songs": [
                    {
                        "title": "Imagine",
                        "artist": "John Lennon",
                        "spotify_uri": "spotify:track:7pKfPomDEeI4TPT6EOYjn",
                        "message": "You may say I'm a dreamer, but I'm not the only one",
                        "context": "When contemplating possibilities",
                    },
                    {
                        "title": "What a Wonderful World",
                        "artist": "Louis Armstrong",
                        "spotify_uri": "spotify:track:29U7stRjqvsYGQNp3B3",
                        "message": "I see trees of green, red roses too",
                        "context": "When appreciating the present moment",
                    },
                    {
                        "title": "Yesterday",
                        "artist": "The Beatles",
                        "spotify_uri": "spotify:track:3BQHpFgAp4l80e1XslIj",
                        "message": "Yesterday, all my troubles seemed so far away",
                        "context": "When reflecting on the past",
                    },
                ],
                "description": "Reflection and contemplation",
            },
            "celebration": {
                "songs": [
                    {
                        "title": "Happy",
                        "artist": "Pharrell Williams",
                        "spotify_uri": "spotify:track:60nZcImufyMAQnTjMI3",
                        "message": "It might seem crazy what I'm 'bout to say",
                        "context": "When celebrating achievements",
                    },
                    {
                        "title": "Good as Hell",
                        "artist": "Lizzo",
                        "spotify_uri": "spotify:track:07Oz5Wy3HfSbqZoH4",
                        "message": "I do my hair toss, check my nails",
                        "context": "When feeling confident and successful",
                    },
                    {
                        "title": "Can't Stop the Feeling!",
                        "artist": "Justin Timberlake",
                        "spotify_uri": "spotify:track:1WkMMavIMc4JZ8cfM",
                        "message": "I got this feeling inside my bones",
                        "context": "When in a positive flow state",
                    },
                ],
                "description": "Celebration and joy",
            },
        }

    def play_nudge(self, nudge_type: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Play a music nudge with optional context"""
        if nudge_type not in self.nudges_db:
            available_types = list(self.nudges_db.keys())
            return {
                "error": f"Unknown nudge type: {nudge_type}",
                "available_types": available_types,
                "timestamp": datetime.now().isoformat(),
            }

        nudge_data = self.nudges_db[nudge_type]
        song = nudge_data["songs"][0]  # For now, play the first song in the category

        # Log the nudge
        nudge_record = {
            "type": nudge_type,
            "song": song,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "spotify_account": self.spotify_account,
        }
        self.session_history.append(nudge_record)

        # Try to open Spotify if available
        try:
            # This would integrate with actual Spotify API
            # For now, we'll simulate it
            logger.info(f"Playing nudge: {song['title']} by {song['artist']}")
            logger.info(f"Message: {song['message']}")

        except Exception as e:
            logger.error(f"Could not play nudge: {e}")

        return {
            "success": True,
            "nudge_type": nudge_type,
            "song": song,
            "message": song["message"],
            "spotify_account": self.spotify_account,
            "timestamp": datetime.now().isoformat(),
        }

    def get_random_nudge(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get a random nudge, optionally from a specific category"""
        import random

        if category and category in self.nudges_db:
            nudge_data = self.nudges_db[category]
        else:
            # Random category
            category = random.choice(list(self.nudges_db.keys()))
            nudge_data = self.nudges_db[category]

        song = random.choice(nudge_data["songs"])
        return self.play_nudge(category, f"Random nudge from {category}")

    def get_nudge_history(self) -> List[Dict[str, Any]]:
        """Get the history of nudges played in this session"""
        return self.session_history

    def save_nudge_history(self, filepath: str = "data/entertainment/nudge_history.json"):
        """Save nudge history to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        history_data = {
            "spotify_account": self.spotify_account,
            "history": self.session_history,
            "total_nudges": len(self.session_history),
            "last_updated": datetime.now().isoformat(),
        }

        with open(filepath, "w") as f:
            json.dump(history_data, f, indent=2)

        return filepath

    def load_nudge_history(
        self, filepath: str = "data/entertainment/nudge_history.json"
    ) -> Dict[str, Any]:
        """Load nudge history from file"""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"history": [], "total_nudges": 0}


# Global instance for easy access from any module
music_nudges = MusicNudges()


def get_music_nudges() -> MusicNudges:
    """Get the global music nudges instance"""
    return music_nudges


# Convenience functions for quick nudges
def nudge_direction(context: str = None) -> Dict[str, Any]:
    """Quick direction nudge"""
    return music_nudges.play_nudge("direction", context)


def nudge_motivation(context: str = None) -> Dict[str, Any]:
    """Quick motivation nudge"""
    return music_nudges.play_nudge("motivation", context)


def nudge_reflection(context: str = None) -> Dict[str, Any]:
    """Quick reflection nudge"""
    return music_nudges.play_nudge("reflection", context)


def nudge_celebration(context: str = None) -> Dict[str, Any]:
    """Quick celebration nudge"""
    return music_nudges.play_nudge("celebration", context)


def random_nudge(context: str = None) -> Dict[str, Any]:
    """Quick random nudge"""
    return music_nudges.get_random_nudge()
