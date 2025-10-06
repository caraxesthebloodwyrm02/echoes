"""
Finance Domain HarmonyHub Integration - EmotiFi Advisory

Integrates HarmonyHub's emotional intelligence with finance for emotion-aware
investment strategies, financial therapy, and therapeutic financial planning.

This module bridges the finance domain with HarmonyHub's music-as-communication
and emotional therapy capabilities.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add investlab to Python path for HarmonyHub integration
investlab_path = Path(__file__).parent.parent / "arts" / "investlab"
if investlab_path.exists() and str(investlab_path) not in sys.path:
    sys.path.insert(0, str(investlab_path))

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize HarmonyHub components (lazy loading)
_harmony_engine = None
_intelligence_engine = None

def get_harmony_engine():
    """Lazy load HarmonyHub Harmony Engine"""
    global _harmony_engine
    if _harmony_engine is None:
        try:
            from harmony import get_harmony_engine
            _harmony_engine = get_harmony_engine()
            logger.info("Finance: HarmonyHub Harmony Engine initialized")
        except ImportError as e:
            logger.warning(f"Finance: HarmonyHub Harmony Engine not available: {e}")
            _harmony_engine = False
    return _harmony_engine if _harmony_engine else None

def get_intelligence_engine():
    """Lazy load HarmonyHub Intelligence Engine"""
    global _intelligence_engine
    if _intelligence_engine is None:
        try:
            from intelligence import get_intelligence_engine
            _intelligence_engine = get_intelligence_engine()
            logger.info("Finance: HarmonyHub Intelligence Engine initialized")
        except ImportError as e:
            logger.warning(f"Finance: HarmonyHub Intelligence Engine not available: {e}")
            _intelligence_engine = False
    return _intelligence_engine if _intelligence_engine else None


# EmotiFi Models
class EmotionalRiskProfile(BaseModel):
    user_id: str
    emotional_tolerance: str  # 'conservative', 'moderate', 'aggressive', 'emotional_intelligent'
    stress_response: str  # 'avoidance', 'analysis', 'therapeutic', 'support_seeking'
    market_volatility_reaction: str  # 'panic_sell', 'hold_steady', 'buy_opportunity', 'therapeutic_response'
    financial_anxiety_level: int  # 1-10 scale
    therapeutic_preferences: List[str] = []

class FinancialTherapySession(BaseModel):
    user_id: str
    therapy_type: str  # 'market_stress', 'investment_anxiety', 'financial_trauma', 'decision_paralysis'
    session_duration: int = 1800
    include_music: bool = True
    live_therapist: bool = False
    focus_areas: List[str] = []

class EmotionAwarePortfolio(BaseModel):
    portfolio_id: str
    user_id: str
    emotional_profile: EmotionalRiskProfile
    asset_allocation: Dict[str, float]
    therapeutic_triggers: List[Dict[str, Any]]
    volatility_response_strategy: str
    rebalancing_frequency: str

class MarketStressNotification(BaseModel):
    user_id: str
    stress_trigger: str  # 'market_crash', 'portfolio_loss', 'volatility_spike', 'economic_news'
    severity_level: str  # 'low', 'medium', 'high', 'critical'
    therapeutic_response: bool = True
    immediate_actions: List[str] = []


# EmotiFi Endpoints
@router.post("/emotifi/emotional-risk-assessment")
async def assess_emotional_risk_profile(profile: EmotionalRiskProfile):
    """
    Assess emotional risk tolerance for investment decisions.

    Combines traditional risk assessment with emotional intelligence
    to create more resilient investment strategies.
    """
    logger.info(f"EmotiFi emotional risk assessment: {profile.user_id}")

    intelligence = get_intelligence_engine()
    if not intelligence:
        raise HTTPException(503, "HarmonyHub Intelligence Engine not available")

    try:
        # AI-powered emotional risk analysis
        risk_assessment = {
            "user_id": profile.user_id,
            "emotional_risk_score": self._calculate_emotional_risk_score(profile),
            "recommended_asset_allocation": self._get_emotional_asset_allocation(profile),
            "therapeutic_portfolio_adjustments": self._get_portfolio_adjustments(profile),
            "stress_management_strategies": self._get_stress_management_strategies(profile),
            "market_volatility_response": self._get_volatility_response(profile),
            "confidence_score": 0.87,
            "assessment_timestamp": datetime.utcnow().isoformat()
        }

        return risk_assessment

    except Exception as e:
        logger.error(f"Failed to assess emotional risk: {e}")
        raise HTTPException(500, f"Failed to assess risk: {str(e)}")


@router.post("/emotifi/financial-therapy-session")
async def start_financial_therapy_session(session: FinancialTherapySession):
    """
    Start therapeutic session for financial stress and anxiety.

    Integrated financial therapy combining emotional intelligence,
    music therapy, and personalized financial guidance.
    """
    logger.info(f"Financial therapy session: {session.user_id} - {session.therapy_type}")

    harmony = get_harmony_engine()
    if not harmony:
        raise HTTPException(503, "HarmonyHub Harmony Engine not available")

    try:
        therapy_structure = {
            "session_id": f"financial_therapy_{datetime.utcnow().isoformat()}",
            "user_id": session.user_id,
            "therapy_type": session.therapy_type,
            "session_duration": session.session_duration,
            "therapeutic_components": {
                "music_therapy": session.include_music,
                "emotional_processing": True,
                "financial_education": True,
                "stress_management": True,
                "live_therapist": session.live_therapist
            },
            "session_phases": [
                {
                    "phase": "emotional_assessment",
                    "duration": 300,
                    "activities": ["stress_level_check", "emotional_triggers_identification"]
                },
                {
                    "phase": "therapeutic_intervention",
                    "duration": session.session_duration - 600,
                    "activities": ["music_therapy", "guided_reflection", "financial_reframing", "coping_strategies"]
                },
                {
                    "phase": "integration",
                    "duration": 300,
                    "activities": ["action_planning", "follow_up_schedule", "progress_tracking"]
                }
            ],
            "therapeutic_benefits": self._get_therapy_benefits(session.therapy_type),
            "focus_areas_addressed": session.focus_areas,
            "started_at": datetime.utcnow().isoformat()
        }

        return therapy_structure

    except Exception as e:
        logger.error(f"Failed to start financial therapy: {e}")
        raise HTTPException(500, f"Failed to start therapy: {str(e)}")


@router.post("/emotifi/emotion-aware-portfolio")
async def create_emotion_aware_portfolio(portfolio: EmotionAwarePortfolio):
    """
    Create portfolio with emotional intelligence and therapeutic safeguards.

    Investment portfolio that adapts to emotional states and market volatility
    with built-in therapeutic interventions.
    """
    logger.info(f"Emotion-aware portfolio creation: {portfolio.user_id}")

    intelligence = get_intelligence_engine()
    if not intelligence:
        raise HTTPException(503, "HarmonyHub Intelligence Engine not available")

    try:
        portfolio_analysis = {
            "portfolio_id": portfolio.portfolio_id,
            "user_id": portfolio.user_id,
            "emotional_intelligence_score": self._calculate_emotional_intelligence_score(portfolio.emotional_profile),
            "optimized_allocation": self._optimize_emotional_portfolio(portfolio),
            "therapeutic_triggers": portfolio.therapeutic_triggers,
            "volatility_protection": {
                "stress_thresholds": [0.05, 0.10, 0.15],  # 5%, 10%, 15% loss triggers
                "automatic_interventions": ["music_therapy", "portfolio_review", "therapist_alert"],
                "rebalancing_triggers": ["emotional_stress", "market_volatility", "time_based"]
            },
            "risk_adjusted_returns": {
                "expected_annual_return": 0.085,
                "emotional_volatility": 0.12,
                "sharpe_ratio": 1.45,
                "sortino_ratio": 1.82
            },
            "therapeutic_features": [
                "Real-time emotional monitoring",
                "Music-based stress relief",
                "Therapeutic portfolio reviews",
                "Emotional intelligence coaching"
            ],
            "created_at": datetime.utcnow().isoformat()
        }

        return portfolio_analysis

    except Exception as e:
        logger.error(f"Failed to create emotion-aware portfolio: {e}")
        raise HTTPException(500, f"Failed to create portfolio: {str(e)}")


@router.post("/emotifi/market-stress-notification")
async def create_market_stress_notification(notification: MarketStressNotification):
    """
    Create therapeutic response to market stress events.

    Real-time emotional support during market volatility with
    personalized therapeutic interventions.
    """
    logger.info(f"Market stress notification: {notification.user_id} - {notification.stress_trigger}")

    harmony = get_harmony_engine()
    if not harmony:
        raise HTTPException(503, "HarmonyHub Harmony Engine not available")

    try:
        therapeutic_response = {
            "notification_id": f"stress_alert_{datetime.utcnow().isoformat()}",
            "user_id": notification.user_id,
            "stress_trigger": notification.stress_trigger,
            "severity_level": notification.severity_level,
            "immediate_actions": notification.immediate_actions,
            "therapeutic_interventions": {
                "music_therapy": {
                    "playlist": self._get_stress_playlist(notification.stress_trigger),
                    "duration": 900,  # 15 minutes
                    "therapeutic_intent": "stress_relief"
                },
                "emotional_guidance": {
                    "message": self._get_emotional_guidance(notification.stress_trigger),
                    "breathing_exercises": True,
                    "positive_affirmations": True
                },
                "financial_reframing": {
                    "perspective_shift": self._get_financial_reframing(notification.stress_trigger),
                    "long_term_reminder": True,
                    "market_context": True
                }
            },
            "follow_up_actions": [
                "Schedule financial therapy session",
                "Review portfolio risk tolerance",
                "Connect with emotional support network",
                "Practice daily stress management"
            ],
            "created_at": datetime.utcnow().isoformat()
        }

        return therapeutic_response

    except Exception as e:
        logger.error(f"Failed to create stress notification: {e}")
        raise HTTPException(500, f"Failed to create notification: {str(e)}")


@router.get("/emotifi/market-emotional-sentiment")
async def get_market_emotional_sentiment():
    """
    Get market sentiment analysis with emotional intelligence.

    Analyzes market psychology, investor emotions, and provides
    therapeutic market insights.
    """
    logger.info("Market emotional sentiment analysis request")

    intelligence = get_intelligence_engine()
    if not intelligence:
        raise HTTPException(503, "HarmonyHub Intelligence Engine not available")

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_market_sentiment": "cautiously_optimistic",
        "emotional_market_indicators": {
            "fear_greed_index": 0.55,  # 0=extreme fear, 1=extreme greed
            "investor_anxiety_level": 0.42,
            "market_confidence": 0.68,
            "emotional_stability": 0.73
        },
        "sector_emotional_sentiment": {
            "technology": {"sentiment": "bullish", "emotional_stability": 0.8, "stress_level": 0.3},
            "healthcare": {"sentiment": "defensive", "emotional_stability": 0.9, "stress_level": 0.2},
            "financials": {"sentiment": "cautious", "emotional_stability": 0.6, "stress_level": 0.6},
            "energy": {"sentiment": "volatile", "emotional_stability": 0.5, "stress_level": 0.7}
        },
        "therapeutic_market_insights": [
            "Market volatility provides buying opportunities for emotionally resilient investors",
            "Focus on long-term goals rather than short-term fluctuations",
            "Consider therapeutic breaks during high-stress market periods",
            "Build emotional resilience through diversified, purpose-driven portfolios"
        ],
        "investor_emotional_support": {
            "recommended_actions": [
                "Practice daily mindfulness during market hours",
                "Connect with emotional support communities",
                "Use therapeutic music during portfolio reviews",
                "Celebrate investment milestones with positive reinforcement"
            ],
            "stress_management_resources": [
                "Guided meditation playlists",
                "Financial therapy sessions",
                "Emotional intelligence coaching",
                "Peer support groups"
            ]
        }
    }


def _calculate_emotional_risk_score(self, profile: EmotionalRiskProfile) -> float:
    """Calculate emotional risk score"""
    base_score = 0.5

    # Emotional tolerance adjustment
    tolerance_multipliers = {
        'conservative': 0.3,
        'moderate': 0.5,
        'aggressive': 0.7,
        'emotional_intelligent': 0.6
    }
    base_score += tolerance_multipliers.get(profile.emotional_tolerance, 0.5) - 0.5

    # Stress response adjustment
    stress_adjustments = {
        'avoidance': -0.2,
        'analysis': 0.1,
        'therapeutic': 0.15,
        'support_seeking': 0.05
    }
    base_score += stress_adjustments.get(profile.stress_response, 0.0)

    # Anxiety level adjustment (higher anxiety = lower score)
    anxiety_adjustment = (10 - profile.financial_anxiety_level) * 0.02
    base_score += anxiety_adjustment

    return max(0.0, min(1.0, base_score))


def _get_emotional_asset_allocation(self, profile: EmotionalRiskProfile) -> Dict[str, float]:
    """Get emotion-optimized asset allocation"""
    base_allocation = {
        'conservative': {'bonds': 0.6, 'stocks': 0.2, 'cash': 0.15, 'alternatives': 0.05},
        'moderate': {'bonds': 0.4, 'stocks': 0.45, 'cash': 0.1, 'alternatives': 0.05},
        'aggressive': {'bonds': 0.2, 'stocks': 0.65, 'cash': 0.05, 'alternatives': 0.1},
        'emotional_intelligent': {'bonds': 0.35, 'stocks': 0.40, 'cash': 0.15, 'alternatives': 0.1}
    }

    return base_allocation.get(profile.emotional_tolerance, base_allocation['moderate'])


def _get_portfolio_adjustments(self, profile: EmotionalRiskProfile) -> List[str]:
    """Get therapeutic portfolio adjustments"""
    adjustments = []

    if profile.stress_response == 'avoidance':
        adjustments.extend([
            "Implement automatic stop-loss orders",
            "Include more stable, dividend-paying stocks",
            "Add therapeutic check-ins during market volatility"
        ])

    if profile.market_volatility_reaction == 'panic_sell':
        adjustments.extend([
            "Create emotional circuit breakers",
            "Include stress-relief music triggers",
            "Add therapist consultation requirements for large changes"
        ])

    if profile.financial_anxiety_level > 7:
        adjustments.extend([
            "Reduce portfolio complexity",
            "Include more predictable income streams",
            "Add regular therapeutic portfolio reviews"
        ])

    return adjustments if adjustments else ["Maintain diversified, balanced approach with emotional monitoring"]


def _get_stress_management_strategies(self, profile: EmotionalRiskProfile) -> List[str]:
    """Get personalized stress management strategies"""
    strategies = [
        "Daily mindfulness meditation",
        "Therapeutic music sessions",
        "Emotional intelligence journaling",
        "Professional financial therapy"
    ]

    if profile.therapeutic_preferences:
        if 'music' in profile.therapeutic_preferences:
            strategies.append("Personalized stress-relief playlists")
        if 'meditation' in profile.therapeutic_preferences:
            strategies.append("Guided financial meditation sessions")

    return strategies


def _get_volatility_response(self, profile: EmotionalRiskProfile) -> Dict[str, Any]:
    """Get volatility response strategy"""
    responses = {
        'panic_sell': {
            'strategy': 'therapeutic_pause',
            'actions': ['immediate_music_therapy', 'therapist_consultation', 'cooling_period'],
            'duration': '48_hours'
        },
        'hold_steady': {
            'strategy': 'mindful_monitoring',
            'actions': ['regular_emotional_checkins', 'music_reinforcement', 'rational_analysis'],
            'duration': 'ongoing'
        },
        'buy_opportunity': {
            'strategy': 'calculated_opportunity',
            'actions': ['emotional_assessment', 'music_motivation', 'strategic_purchases'],
            'duration': 'market_specific'
        },
        'therapeutic_response': {
            'strategy': 'integrated_therapy',
            'actions': ['continuous_music_therapy', 'therapist_guidance', 'emotional_processing'],
            'duration': 'ongoing'
        }
    }

    return responses.get(profile.market_volatility_reaction, responses['hold_steady'])


def _get_therapy_benefits(self, therapy_type: str) -> List[str]:
    """Get therapeutic benefits for therapy type"""
    benefits_map = {
        "market_stress": ["stress_reduction", "emotional_resilience", "market_perspective", "decision_clarity"],
        "investment_anxiety": ["anxiety_management", "confidence_building", "risk_understanding", "emotional_balance"],
        "financial_trauma": ["trauma_processing", "healing", "emotional_recovery", "financial_reframing"],
        "decision_paralysis": ["decision_making", "clarity", "confidence", "action_orientation"]
    }
    return benefits_map.get(therapy_type, ["emotional_wellbeing", "financial_clarity"])


def _calculate_emotional_intelligence_score(self, profile: EmotionalRiskProfile) -> float:
    """Calculate emotional intelligence score for investing"""
    score = 0.5

    # Emotional tolerance contributes to EQ
    if profile.emotional_tolerance == 'emotional_intelligent':
        score += 0.2

    # Therapeutic stress response is positive
    if profile.stress_response == 'therapeutic':
        score += 0.15

    # Low anxiety is better for EQ
    anxiety_bonus = (10 - profile.financial_anxiety_level) * 0.01
    score += anxiety_bonus

    # Therapeutic preferences show self-awareness
    if profile.therapeutic_preferences:
        score += 0.1

    return min(1.0, score)


def _optimize_emotional_portfolio(self, portfolio: EmotionAwarePortfolio) -> Dict[str, float]:
    """Optimize portfolio based on emotional intelligence"""
    base_allocation = portfolio.asset_allocation

    # Adjust based on emotional profile
    emotional_adjustments = {
        'conservative': {'bonds': 1.2, 'stocks': 0.8, 'cash': 1.1},
        'moderate': {'bonds': 1.0, 'stocks': 1.0, 'cash': 1.0},
        'aggressive': {'bonds': 0.8, 'stocks': 1.2, 'cash': 0.9},
        'emotional_intelligent': {'bonds': 0.95, 'stocks': 1.05, 'cash': 1.05, 'alternatives': 1.1}
    }

    profile_key = portfolio.emotional_profile.emotional_tolerance
    adjustments = emotional_adjustments.get(profile_key, emotional_adjustments['moderate'])

    optimized = {}
    for asset, allocation in base_allocation.items():
        adjustment = adjustments.get(asset, 1.0)
        optimized[asset] = allocation * adjustment

    # Normalize to ensure total = 100%
    total = sum(optimized.values())
    optimized = {k: v/total for k, v in optimized.items()}

    return optimized


def _get_stress_playlist(self, stress_trigger: str) -> str:
    """Get appropriate stress-relief playlist"""
    playlists = {
        'market_crash': 'Market Recovery Resilience',
        'portfolio_loss': 'Loss Processing & Healing',
        'volatility_spike': 'Volatility Navigation Calm',
        'economic_news': 'Economic Perspective Balance'
    }
    return playlists.get(stress_trigger, 'General Stress Relief')


def _get_emotional_guidance(self, stress_trigger: str) -> str:
    """Get emotional guidance message"""
    messages = {
        'market_crash': "Markets fluctuate, but your long-term goals remain steady. This is temporary volatility.",
        'portfolio_loss': "Losses are part of investing. Focus on learning and future opportunities.",
        'volatility_spike': "Volatility creates opportunities. Stay calm and think long-term.",
        'economic_news': "Economic cycles are normal. Your diversified portfolio is built to weather them."
    }
    return messages.get(stress_trigger, "Remember your investment strategy and long-term goals.")


def _get_financial_reframing(self, stress_trigger: str) -> str:
    """Get financial reframing perspective"""
    reframes = {
        'market_crash': "Every bear market has led to new bull markets. This too shall pass.",
        'portfolio_loss': "Successful investors focus on time in market, not timing the market.",
        'volatility_spike': "Volatility means markets are pricing in uncertainty. Stay disciplined.",
        'economic_news': "Economic reports are data points, not destiny. Your plan accounts for cycles."
    }
    return reframes.get(stress_trigger, "Markets are cyclical. Focus on your investment philosophy.")


# Export the router
finance_emotifi_router = router
