#!/usr/bin/env python3
"""
HarmonyHub - AI-Powered Emotional Intelligence Social Platform
Music as Communication, Sound-Based Social Networking
"""

import os
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

# Import InvestLab components
from highway import get_highway, DataType
from intelligence import get_intelligence_engine
from analytics import get_portfolio_analytics

logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    """Emotional states for music communication"""
    JOYFUL = "joyful"
    MELANCHOLIC = "melancholic"
    ENERGETIC = "energetic"
    CALM = "calm"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    LONELY = "lonely"
    INSPIRED = "inspired"
    FRUSTRATED = "frustrated"
    GRATEFUL = "grateful"

class CommunicationIntent(Enum):
    """Intent behind music-based communication"""
    EXPRESSION = "expression"      # Share how you feel
    CONNECTION = "connection"      # Reach out to someone
    CELEBRATION = "celebration"    # Share joy/achievement
    SUPPORT = "support"           # Offer emotional support
    UNDERSTANDING = "understanding" # Show you understand
    ENCOURAGEMENT = "encouragement" # Motivate/inspire
    REFLECTION = "reflection"     # Share thoughtful moment
    GRATITUDE = "gratitude"       # Express thanks

@dataclass
class SoundMessage:
    """A music-based message for communication"""
    id: str = field(default_factory=lambda: f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    sender_id: str
    recipient_id: Optional[str] = None  # None for broadcast/public
    emotional_state: EmotionalState
    communication_intent: CommunicationIntent
    selected_track: Dict[str, Any]  # Spotify track data
    message_text: Optional[str] = None
    context_tags: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    resonance_score: float = 0.0  # How well it resonated
    replies: List['SoundMessage'] = field(default_factory=list)

@dataclass
class EmotionalProfile:
    """User's emotional intelligence profile"""
    user_id: str
    dominant_emotions: List[EmotionalState] = field(default_factory=list)
    music_preferences: Dict[str, List[str]] = field(default_factory=dict)  # emotion -> track_ids
    communication_patterns: Dict[str, int] = field(default_factory=dict)  # intent -> frequency
    resonance_history: List[Dict[str, Any]] = field(default_factory=list)
    ai_insights: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class HarmonyCommunity:
    """Community organized around emotional states and music"""
    id: str = field(default_factory=lambda: f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    name: str
    theme_emotion: EmotionalState
    description: str
    members: List[str] = field(default_factory=list)
    featured_tracks: List[Dict[str, Any]] = field(default_factory=list)
    discussion_topics: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    activity_score: float = 0.0

class HarmonyHub:
    """AI-Powered Emotional Intelligence Social Platform"""

    def __init__(self):
        self.highway = get_highway()
        self.intelligence = get_intelligence_engine()
        self.analytics = get_portfolio_analytics()

        # Core components
        self.emotional_ai = self._initialize_emotional_ai()
        self.music_recommender = self._initialize_music_recommender()
        self.communication_engine = self._initialize_communication_engine()
        self.community_manager = self._initialize_community_manager()

        # Data stores
        self.users: Dict[str, EmotionalProfile] = {}
        self.messages: List[SoundMessage] = []
        self.communities: Dict[str, HarmonyCommunity] = {}

        logger.info("HarmonyHub initialized - Music as Communication Platform")

    def _initialize_emotional_ai(self) -> Dict[str, Any]:
        """Initialize emotional intelligence AI systems"""
        return {
            'sentiment_analyzer': {
                'model': 'emotion_bert',
                'capabilities': ['text_emotion', 'music_emotion', 'context_analysis'],
                'accuracy': 0.87
            },
            'emotional_intelligence': {
                'model': 'empathy_net',
                'capabilities': ['empathy_prediction', 'communication_intent', 'resonance_forecasting'],
                'accuracy': 0.82
            },
            'music_emotion_mapper': {
                'model': 'music_sentiment_ai',
                'capabilities': ['track_emotion_classification', 'playlist_mood_analysis'],
                'accuracy': 0.91
            }
        }

    def _initialize_music_recommender(self) -> Dict[str, Any]:
        """Initialize music recommendation systems"""
        return {
            'spotify_integration': {
                'api_version': 'v1',
                'features': ['audio_features', 'recommendations', 'user_library']
            },
            'emotion_based_recommender': {
                'algorithm': 'deep_emotion_matching',
                'features': ['valence_arousal', 'tempo_emotion', 'lyrical_sentiment']
            },
            'context_aware_system': {
                'algorithm': 'situational_music_ai',
                'features': ['time_of_day', 'user_mood', 'social_context', 'activity_type']
            }
        }

    def _initialize_communication_engine(self) -> Dict[str, Any]:
        """Initialize music-based communication systems"""
        return {
            'sound_messaging': {
                'protocol': 'harmony_protocol_v1',
                'features': ['real_time_delivery', 'emotional_context', 'resonance_tracking']
            },
            'intent_recognition': {
                'model': 'communication_ai',
                'capabilities': ['intent_classification', 'emotional_nuances', 'cultural_context']
            },
            'resonance_analyzer': {
                'algorithm': 'emotional_resonance_ai',
                'metrics': ['engagement_score', 'emotional_impact', 'connection_strength']
            }
        }

    def _initialize_community_manager(self) -> Dict[str, Any]:
        """Initialize community management systems"""
        return {
            'community_discovery': {
                'algorithm': 'emotion_based_matching',
                'features': ['similar_emotions', 'shared_interests', 'communication_patterns']
            },
            'engagement_optimizer': {
                'model': 'community_ai',
                'capabilities': ['content_recommendation', 'member_matching', 'activity_suggestions']
            },
            'moderation_system': {
                'algorithm': 'harmony_guardian',
                'features': ['emotional_safety', 'positive_communication', 'community_guidelines']
            }
        }

    def create_user_profile(self, user_id: str, initial_emotions: List[EmotionalState] = None) -> EmotionalProfile:
        """Create emotional intelligence profile for new user"""
        logger.info(f"Creating emotional profile for user {user_id}")

        if initial_emotions is None:
            initial_emotions = [EmotionalState.CALM]

        # Route profile creation through highway
        packet = {
            'type': 'emotional_profile_creation',
            'user_id': user_id,
            'initial_emotions': [e.value for e in initial_emotions],
            'creation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'harmony_hub')

        profile = EmotionalProfile(
            user_id=user_id,
            dominant_emotions=initial_emotions,
            music_preferences={emotion.value: [] for emotion in EmotionalState}
        )

        self.users[user_id] = profile

        logger.info(f"Emotional profile created for {user_id}")
        return profile

    def send_sound_message(self, sender_id: str, recipient_id: Optional[str],
                          emotion: EmotionalState, intent: CommunicationIntent,
                          context: Dict[str, Any] = None) -> SoundMessage:
        """Send a music-based communication message"""
        logger.info(f"Creating sound message from {sender_id} to {recipient_id}")

        if context is None:
            context = {}

        # Route message creation through highway
        packet = {
            'type': 'sound_message_creation',
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'emotion': emotion.value,
            'intent': intent.value,
            'context': context,
            'creation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'harmony_hub')

        # AI-powered music recommendation
        recommended_track = self._recommend_music_for_communication(emotion, intent, context)

        # Create sound message
        message = SoundMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            emotional_state=emotion,
            communication_intent=intent,
            selected_track=recommended_track,
            context_tags=context.get('tags', [])
        )

        self.messages.append(message)

        # Update user profile
        if sender_id in self.users:
            profile = self.users[sender_id]
            profile.communication_patterns[intent.value] = profile.communication_patterns.get(intent.value, 0) + 1
            profile.last_updated = datetime.now()

        logger.info(f"Sound message created: {message.id} ({emotion.value} - {intent.value})")

        return message

    def analyze_emotional_resonance(self, message_id: str, receiver_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well a sound message resonated emotionally"""
        logger.info(f"Analyzing emotional resonance for message {message_id}")

        # Find message
        message = None
        for msg in self.messages:
            if msg.id == message_id:
                message = msg
                break

        if not message:
            raise ValueError(f"Message {message_id} not found")

        # Route resonance analysis through highway
        packet = {
            'type': 'resonance_analysis',
            'message_id': message_id,
            'receiver_feedback': receiver_feedback,
            'analysis_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'harmony_hub')

        # AI-powered resonance analysis
        resonance_score = self._calculate_resonance_score(message, receiver_feedback)
        emotional_impact = self._assess_emotional_impact(message, receiver_feedback)
        connection_strength = self._measure_connection_strength(message, receiver_feedback)

        analysis = {
            'message_id': message_id,
            'resonance_score': resonance_score,
            'emotional_impact': emotional_impact,
            'connection_strength': connection_strength,
            'ai_insights': self._generate_resonance_insights(message, receiver_feedback),
            'improvement_suggestions': self._suggest_communication_improvements(message, receiver_feedback)
        }

        # Update message resonance score
        message.resonance_score = resonance_score

        # Update sender's emotional profile
        if message.sender_id in self.users:
            profile = self.users[message.sender_id]
            profile.resonance_history.append({
                'message_id': message_id,
                'resonance_score': resonance_score,
                'feedback': receiver_feedback,
                'timestamp': datetime.now()
            })

        logger.info(f"Resonance analysis completed for {message_id}: {resonance_score:.2f} score")

        return analysis

    def create_emotional_community(self, creator_id: str, name: str,
                                  theme_emotion: EmotionalState,
                                  description: str) -> HarmonyCommunity:
        """Create a community organized around emotional states"""
        logger.info(f"Creating emotional community: {name} ({theme_emotion.value})")

        # Route community creation through highway
        packet = {
            'type': 'emotional_community_creation',
            'creator_id': creator_id,
            'name': name,
            'theme_emotion': theme_emotion.value,
            'description': description,
            'creation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'harmony_hub')

        community = HarmonyCommunity(
            name=name,
            theme_emotion=theme_emotion,
            description=description,
            members=[creator_id]
        )

        self.communities[community.id] = community

        logger.info(f"Emotional community created: {community.id}")

        return community

    def recommend_music_for_emotion(self, user_id: str, target_emotion: EmotionalState,
                                  context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Recommend music tracks for emotional expression or communication"""
        logger.info(f"Recommending music for {user_id}: {target_emotion.value}")

        if context is None:
            context = {}

        # Route music recommendation through highway
        packet = {
            'type': 'music_recommendation_request',
            'user_id': user_id,
            'target_emotion': target_emotion.value,
            'context': context,
            'recommendation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'harmony_hub')

        # AI-powered music recommendation
        recommendations = self._generate_music_recommendations(user_id, target_emotion, context)

        # Update user profile
        if user_id in self.users:
            profile = self.users[user_id]
            if target_emotion.value not in profile.music_preferences:
                profile.music_preferences[target_emotion.value] = []

            # Add recommended tracks to preferences
            for rec in recommendations[:3]:  # Top 3 recommendations
                track_id = rec.get('id')
                if track_id and track_id not in profile.music_preferences[target_emotion.value]:
                    profile.music_preferences[target_emotion.value].append(track_id)

        logger.info(f"Music recommendations generated for {user_id}: {len(recommendations)} tracks")

        return recommendations

    def get_emotional_intelligence_insights(self, user_id: str) -> Dict[str, Any]:
        """Get AI-powered insights about user's emotional intelligence"""
        logger.info(f"Generating emotional intelligence insights for {user_id}")

        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")

        profile = self.users[user_id]

        # Route insights generation through highway
        packet = {
            'type': 'emotional_intelligence_analysis',
            'user_id': user_id,
            'profile_data': {
                'dominant_emotions': [e.value for e in profile.dominant_emotions],
                'communication_patterns': profile.communication_patterns,
                'resonance_history': profile.resonance_history[-10:]  # Last 10 interactions
            },
            'analysis_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'harmony_hub')

        insights = {
            'emotional_profile': self._analyze_emotional_profile(profile),
            'communication_effectiveness': self._assess_communication_effectiveness(profile),
            'music_preference_evolution': self._track_music_preference_evolution(profile),
            'social_connection_patterns': self._analyze_social_connection_patterns(profile),
            'personal_growth_opportunities': self._identify_growth_opportunities(profile),
            'ai_recommendations': self._generate_personalized_recommendations(profile)
        }

        # Update profile with new insights
        profile.ai_insights.extend(insights['ai_recommendations'])
        profile.last_updated = datetime.now()

        logger.info(f"Emotional intelligence insights generated for {user_id}")

        return insights

    def _recommend_music_for_communication(self, emotion: EmotionalState,
                                         intent: CommunicationIntent,
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered music recommendation for communication"""
        # Simulate AI recommendation (would integrate with Spotify API)
        recommendations = {
            EmotionalState.JOYFUL: {
                'id': 'joyful_track_001',
                'title': 'Happy',
                'artist': 'Pharrell Williams',
                'album': 'G I R L',
                'duration_ms': 233000,
                'preview_url': 'https://example.com/preview',
                'emotional_match': 0.95,
                'communication_effectiveness': 0.88
            },
            EmotionalState.CALM: {
                'id': 'calm_track_001',
                'title': 'Weightless',
                'artist': 'Marconi Union',
                'album': 'Weightless',
                'duration_ms': 487000,
                'preview_url': 'https://example.com/preview',
                'emotional_match': 0.92,
                'communication_effectiveness': 0.91
            },
            EmotionalState.ENERGETIC: {
                'id': 'energetic_track_001',
                'title': 'Uptown Funk',
                'artist': 'Mark Ronson ft. Bruno Mars',
                'album': 'Uptown Special',
                'duration_ms': 270000,
                'preview_url': 'https://example.com/preview',
                'emotional_match': 0.89,
                'communication_effectiveness': 0.85
            }
        }

        return recommendations.get(emotion, recommendations[EmotionalState.CALM])

    def _calculate_resonance_score(self, message: SoundMessage, feedback: Dict[str, Any]) -> float:
        """Calculate how well a message resonated"""
        # Simulate resonance calculation based on feedback
        base_score = 0.5

        # Positive feedback increases score
        if feedback.get('emotional_impact') == 'positive':
            base_score += 0.3
        elif feedback.get('emotional_impact') == 'very_positive':
            base_score += 0.4

        # Strong connection increases score
        if feedback.get('connection_strength') in ['strong', 'very_strong']:
            base_score += 0.2

        # Track quality affects score
        if message.selected_track.get('emotional_match', 0) > 0.8:
            base_score += 0.1

        return min(1.0, base_score)

    def _assess_emotional_impact(self, message: SoundMessage, feedback: Dict[str, Any]) -> str:
        """Assess emotional impact of message"""
        impact_scores = {
            'very_positive': ['uplifting', 'inspiring', 'joyful', 'peaceful'],
            'positive': ['comforting', 'understanding', 'supportive'],
            'neutral': ['acknowledged', 'noted'],
            'negative': ['confusing', 'uncomfortable']
        }

        feedback_text = feedback.get('description', '').lower()

        for impact, keywords in impact_scores.items():
            if any(keyword in feedback_text for keyword in keywords):
                return impact

        return 'neutral'

    def _measure_connection_strength(self, message: SoundMessage, feedback: Dict[str, Any]) -> str:
        """Measure strength of emotional connection"""
        strength_indicators = {
            'very_strong': ['deeply_moved', 'profound_connection', 'life_changing'],
            'strong': ['felt_understood', 'emotional_connection', 'meaningful'],
            'moderate': ['nice_gesture', 'appreciated', 'thoughtful'],
            'weak': ['confusing', 'missed_mark', 'not_quite_right']
        }

        feedback_text = feedback.get('description', '').lower()

        for strength, keywords in strength_indicators.items():
            if any(keyword in feedback_text for keyword in keywords):
                return strength

        return 'moderate'

    def _generate_resonance_insights(self, message: SoundMessage, feedback: Dict[str, Any]) -> List[str]:
        """Generate AI insights about message resonance"""
        insights = []

        if message.resonance_score > 0.8:
            insights.append("This message created a strong emotional connection")
            insights.append("Consider using similar emotional tones for future communications")
        elif message.resonance_score > 0.6:
            insights.append("The message was well-received with positive emotional impact")
        else:
            insights.append("Consider refining emotional expression techniques")
            insights.append("Music selection could be better matched to recipient's preferences")

        return insights

    def _suggest_communication_improvements(self, message: SoundMessage, feedback: Dict[str, Any]) -> List[str]:
        """Suggest improvements for future communications"""
        suggestions = []

        if message.resonance_score < 0.7:
            suggestions.append("Try tracks with more emotional intensity for stronger impact")
            suggestions.append("Consider the recipient's current emotional state when selecting music")
            suggestions.append("Add more personal context to enhance emotional connection")

        suggestions.append("Continue practicing music-based emotional communication")
        suggestions.append("Track resonance patterns to improve future interactions")

        return suggestions

    def _generate_music_recommendations(self, user_id: str, emotion: EmotionalState,
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized music recommendations"""
        # Simulate AI-powered recommendations
        base_recommendations = {
            EmotionalState.JOYFUL: [
                {'id': 'joy_001', 'title': 'Happy', 'artist': 'Pharrell Williams', 'match_score': 0.95},
                {'id': 'joy_002', 'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'match_score': 0.92},
                {'id': 'joy_003', 'title': "Don't Worry, Be Happy", 'artist': 'Bobby McFerrin', 'match_score': 0.89}
            ],
            EmotionalState.CALM: [
                {'id': 'calm_001', 'title': 'Weightless', 'artist': 'Marconi Union', 'match_score': 0.94},
                {'id': 'calm_002', 'title': 'River Flows in You', 'artist': 'Yiruma', 'match_score': 0.91},
                {'id': 'calm_003', 'title': 'The Journey', 'artist': 'Theatre Camp', 'match_score': 0.88}
            ],
            EmotionalState.ENERGETIC: [
                {'id': 'energy_001', 'title': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars', 'match_score': 0.93},
                {'id': 'energy_002', 'title': 'Happy', 'artist': 'Pharrell Williams', 'match_score': 0.90},
                {'id': 'energy_003', 'title': "Can't Stop the Feeling!", 'artist': 'Justin Timberlake', 'match_score': 0.87}
            ]
        }

        recommendations = base_recommendations.get(emotion, base_recommendations[EmotionalState.CALM])

        # Personalize based on user profile
        if user_id in self.users:
            profile = self.users[user_id]
            # Adjust recommendations based on user's music preferences
            # (Simplified - would use more sophisticated personalization)

        return recommendations

    def _analyze_emotional_profile(self, profile: EmotionalProfile) -> Dict[str, Any]:
        """Analyze user's emotional profile"""
        return {
            'dominant_emotions': [e.value for e in profile.dominant_emotions],
            'emotional_diversity': len(profile.dominant_emotions),
            'communication_style': max(profile.communication_patterns.items(), key=lambda x: x[1])[0] if profile.communication_patterns else 'balanced',
            'average_resonance': sum(r['resonance_score'] for r in profile.resonance_history) / len(profile.resonance_history) if profile.resonance_history else 0.0
        }

    def _assess_communication_effectiveness(self, profile: EmotionalProfile) -> Dict[str, Any]:
        """Assess communication effectiveness"""
        total_messages = len(profile.resonance_history)
        high_resonance = len([r for r in profile.resonance_history if r['resonance_score'] > 0.8])

        return {
            'total_communications': total_messages,
            'high_impact_communications': high_resonance,
            'effectiveness_rate': high_resonance / total_messages if total_messages > 0 else 0.0,
            'improvement_trend': 'improving' if total_messages > 5 else 'learning'
        }

    def _track_music_preference_evolution(self, profile: EmotionalProfile) -> Dict[str, Any]:
        """Track how music preferences have evolved"""
        total_preferences = sum(len(tracks) for tracks in profile.music_preferences.values())

        return {
            'total_music_preferences': total_preferences,
            'preferred_emotions': sorted(profile.music_preferences.keys(), key=lambda x: len(profile.music_preferences[x]), reverse=True),
            'music_discovery_rate': total_preferences / max(1, len(profile.resonance_history))
        }

    def _analyze_social_connection_patterns(self, profile: EmotionalProfile) -> Dict[str, Any]:
        """Analyze social connection patterns"""
        return {
            'communication_frequency': len(profile.resonance_history),
            'emotional_connection_strength': 'strong' if len([r for r in profile.resonance_history if r['resonance_score'] > 0.8]) > len(profile.resonance_history) * 0.6 else 'developing',
            'relationship_building': 'active' if profile.communication_patterns else 'exploring'
        }

    def _identify_growth_opportunities(self, profile: EmotionalProfile) -> List[str]:
        """Identify personal growth opportunities"""
        opportunities = []

        if len(profile.dominant_emotions) < 3:
            opportunities.append("Explore a wider range of emotional expressions")

        if len(profile.resonance_history) < 10:
            opportunities.append("Practice more music-based communications to improve resonance")

        low_resonance = len([r for r in profile.resonance_history if r['resonance_score'] < 0.6])
        if low_resonance > len(profile.resonance_history) * 0.3:
            opportunities.append("Refine music selection for better emotional matching")

        return opportunities

    def _generate_personalized_recommendations(self, profile: EmotionalProfile) -> List[str]:
        """Generate personalized AI recommendations"""
        recommendations = []

        # Based on communication patterns
        if profile.communication_patterns.get('expression', 0) > profile.communication_patterns.get('connection', 0):
            recommendations.append("Try using more connection-oriented communications to build deeper relationships")

        # Based on resonance history
        avg_resonance = sum(r['resonance_score'] for r in profile.resonance_history) / len(profile.resonance_history) if profile.resonance_history else 0
        if avg_resonance > 0.8:
            recommendations.append("Your emotional communication skills are excellent - consider mentoring others")
        elif avg_resonance < 0.6:
            recommendations.append("Focus on better emotional calibration in your music selections")

        return recommendations

# Global HarmonyHub instance
harmony_hub = HarmonyHub()

def get_harmony_hub() -> HarmonyHub:
    """Get the global HarmonyHub instance"""
    return harmony_hub

# Convenience functions
def create_user_profile(user_id: str, initial_emotions: List[EmotionalState] = None) -> EmotionalProfile:
    """Create emotional intelligence profile for user"""
    if initial_emotions is None:
        initial_emotions = [EmotionalState.CALM]
    return harmony_hub.create_user_profile(user_id, initial_emotions)

def send_sound_message(sender_id: str, recipient_id: Optional[str],
                      emotion: EmotionalState, intent: CommunicationIntent,
                      context: Dict[str, Any] = None) -> SoundMessage:
    """Send music-based communication"""
    if context is None:
        context = {}
    return harmony_hub.send_sound_message(sender_id, recipient_id, emotion, intent, context)

def analyze_emotional_resonance(message_id: str, receiver_feedback: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze emotional resonance of communication"""
    return harmony_hub.analyze_emotional_resonance(message_id, receiver_feedback)

def create_emotional_community(creator_id: str, name: str,
                              theme_emotion: EmotionalState,
                              description: str) -> HarmonyCommunity:
    """Create emotional intelligence community"""
    return harmony_hub.create_emotional_community(creator_id, name, theme_emotion, description)

def recommend_music_for_emotion(user_id: str, target_emotion: EmotionalState,
                              context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Get music recommendations for emotional expression"""
    if context is None:
        context = {}
    return harmony_hub.recommend_music_for_emotion(user_id, target_emotion, context)

def get_emotional_intelligence_insights(user_id: str) -> Dict[str, Any]:
    """Get emotional intelligence insights"""
    return harmony_hub.get_emotional_intelligence_insights(user_id)
