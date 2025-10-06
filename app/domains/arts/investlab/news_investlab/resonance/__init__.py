#!/usr/bin/env python3
"""
Resonance - AI-Powered Tailored News & Emotional Updates
Category-based content delivery with emotional intelligence and personalization
"""

import os
import json
import feedparser
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

# Import InvestLab components
from highway import get_highway, DataType

logger = logging.getLogger(__name__)

class ContentCategory(Enum):
    """Content categories for tailored delivery"""
    FINANCIAL_NEWS = "financial_news"
    MARKET_ANALYSIS = "market_analysis"
    ECONOMIC_INDICATORS = "economic_indicators"
    INVESTMENT_STRATEGIES = "investment_strategies"
    PERSONAL_FINANCE = "personal_finance"
    CRYPTOCURRENCY = "cryptocurrency"
    REAL_ESTATE = "real_estate"
    STARTUP_ECOSYSTEM = "startup_ecosystem"
    REGULATORY_UPDATES = "regulatory_updates"
    SUSTAINABLE_INVESTING = "sustainable_investing"

class EmotionalTone(Enum):
    """Emotional tone for content delivery"""
    OPTIMISTIC = "optimistic"
    CAUTIOUS = "cautious"
    NEUTRAL = "neutral"
    CONCERNED = "concerned"
    ENTHUSIASTIC = "enthusiastic"
    THOUGHTFUL = "thoughtful"
    URGENT = "urgent"
    REFLECTIVE = "reflective"

class ResonanceLevel(Enum):
    """Level of emotional resonance for content"""
    HIGH = "high"         # Strong emotional connection
    MEDIUM = "medium"     # Moderate connection
    LOW = "low"          # Weak connection
    NONE = "none"        # No emotional connection

@dataclass
class TailoredContent:
    """AI-tailored content item"""
    id: str = field(default_factory=lambda: f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    title: str
    summary: str
    full_content: str
    source_url: str
    category: ContentCategory
    emotional_tone: EmotionalTone
    resonance_score: float
    target_audience: List[str]  # User segments
    key_insights: List[str] = field(default_factory=list)
    related_symbols: List[str] = field(default_factory=list)
    published_at: datetime = field(default_factory=datetime.now)
    sentiment_score: float = 0.0
    urgency_level: str = "normal"

@dataclass
class PersonalizedFeed:
    """Personalized content feed for individual users"""
    user_id: str
    feed_name: str
    preferred_categories: List[ContentCategory] = field(default_factory=list)
    emotional_preferences: List[EmotionalTone] = field(default_factory=list)
    content_history: List[str] = field(default_factory=list)  # Content IDs
    resonance_patterns: Dict[str, float] = field(default_factory=dict)  # Category -> resonance score
    delivery_schedule: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ContentResonance:
    """Content resonance analysis"""
    content_id: str
    user_id: str
    resonance_level: ResonanceLevel
    emotional_impact: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    behavioral_response: Dict[str, Any]
    analyzed_at: datetime = field(default_factory=datetime.now)

class ResonanceEngine:
    """AI-Powered Content Resonance & Personalization Engine"""

    def __init__(self):
        self.highway = get_highway()

        # Core resonance systems
        self.content_aggregation = self._initialize_content_aggregation()
        self.emotional_analysis = self._initialize_emotional_analysis()
        self.personalization_engine = self._initialize_personalization_engine()
        self.resonance_tracking = self._initialize_resonance_tracking()

        # Data stores
        self.content_library: Dict[str, TailoredContent] = {}
        self.user_feeds: Dict[str, PersonalizedFeed] = {}
        self.resonance_data: List[ContentResonance] = []
        self.content_sources = self._initialize_content_sources()

        logger.info("ResonanceEngine initialized - AI-Powered Content Personalization")

    def _initialize_content_aggregation(self) -> Dict[str, Any]:
        """Initialize content aggregation systems"""
        return {
            'news_apis': {
                'financial_news': ['bloomberg_api', 'reuters_api', 'cnbc_api'],
                'market_data': ['yahoo_finance', 'alpha_vantage', 'polygon_api'],
                'economic_indicators': ['federal_reserve_api', 'bea_api', 'bls_api']
            },
            'rss_feeds': {
                'premium_sources': ['wsj.com', 'ft.com', 'economist.com'],
                'market_intelligence': ['seekingalpha.com', 'marketwatch.com'],
                'regulatory_updates': ['sec.gov', 'federalreserve.gov']
            },
            'social_signals': {
                'twitter_sentiment': ['stocktwits_api', 'twitter_api'],
                'influencer_tracking': ['linkedin_api', 'youtube_api'],
                'community_insights': ['reddit_api', 'discord_api']
            }
        }

    def _initialize_emotional_analysis(self) -> Dict[str, Any]:
        """Initialize emotional analysis systems"""
        return {
            'sentiment_analysis': {
                'models': ['vader', 'textblob', 'finbert'],
                'financial_lexicon': 'custom_finance_sentiment',
                'real_time_processing': True
            },
            'emotional_tone_detection': {
                'tone_categories': [tone.value for tone in EmotionalTone],
                'context_awareness': True,
                'cultural_adaptation': 'multi_lingual'
            },
            'resonance_prediction': {
                'user_modeling': 'deep_learning',
                'behavioral_patterns': 'reinforcement_learning',
                'real_time_adaptation': True
            }
        }

    def _initialize_personalization_engine(self) -> Dict[str, Any]:
        """Initialize personalization systems"""
        return {
            'user_profiling': {
                'behavioral_analysis': 'clickstream_analysis',
                'preference_learning': 'collaborative_filtering',
                'context_awareness': 'situational_adaptation'
            },
            'content_recommendation': {
                'algorithms': ['content_based', 'collaborative', 'hybrid'],
                'real_time_personalization': True,
                'a_b_testing': 'continuous_optimization'
            },
            'delivery_optimization': {
                'timing_optimization': 'predictive_delivery',
                'channel_selection': 'multi_platform',
                'engagement_maximization': 'attention_economy'
            }
        }

    def _initialize_resonance_tracking(self) -> Dict[str, Any]:
        """Initialize resonance tracking systems"""
        return {
            'engagement_metrics': {
                'attention_duration': 'eye_tracking_simulation',
                'emotional_response': 'physiological_monitoring',
                'behavioral_intent': 'click_prediction'
            },
            'resonance_measurement': {
                'emotional_connection': 'sentiment_correlation',
                'cognitive_engagement': 'attention_modeling',
                'behavioral_impact': 'action_prediction'
            },
            'feedback_integration': {
                'explicit_feedback': 'rating_system',
                'implicit_feedback': 'behavioral_signals',
                'continuous_learning': 'reinforcement_updates'
            }
        }

    def _initialize_content_sources(self) -> Dict[str, Any]:
        """Initialize content source configurations"""
        return {
            'financial_news': {
                'bloomberg': {'api_key': 'configured', 'rate_limit': 100, 'priority': 'high'},
                'reuters': {'api_key': 'configured', 'rate_limit': 200, 'priority': 'high'},
                'cnbc': {'api_key': 'configured', 'rate_limit': 150, 'priority': 'medium'}
            },
            'market_data': {
                'yahoo_finance': {'api_key': 'configured', 'rate_limit': 2000, 'priority': 'high'},
                'alpha_vantage': {'api_key': 'configured', 'rate_limit': 500, 'priority': 'medium'}
            },
            'social_media': {
                'twitter': {'api_key': 'configured', 'rate_limit': 300, 'priority': 'medium'},
                'stocktwits': {'api_key': 'configured', 'rate_limit': 1000, 'priority': 'high'}
            }
        }

    def aggregate_financial_content(self, categories: List[ContentCategory] = None,
                                  hours_back: int = 24) -> List[TailoredContent]:
        """Aggregate and process financial content from multiple sources"""
        if categories is None:
            categories = [ContentCategory.FINANCIAL_NEWS, ContentCategory.MARKET_ANALYSIS]

        logger.info(f"Aggregating financial content for categories: {[c.value for c in categories]}")

        # Route content aggregation through highway
        packet = {
            'type': 'financial_content_aggregation',
            'categories': [c.value for c in categories],
            'hours_back': hours_back,
            'aggregation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'resonance_engine')

        # Aggregate content from various sources
        raw_content = self._fetch_raw_content(categories, hours_back)

        # Process and tailor content
        processed_content = []
        for raw_item in raw_content:
            tailored_content = self._process_and_tailor_content(raw_item)
            if tailored_content:
                self.content_library[tailored_content.id] = tailored_content
                processed_content.append(tailored_content)

        logger.info(f"Financial content aggregated: {len(processed_content)} items processed")

        return processed_content

    def create_personalized_feed(self, user_id: str, feed_name: str,
                               preferred_categories: List[ContentCategory],
                               emotional_preferences: List[EmotionalTone]) -> PersonalizedFeed:
        """Create personalized content feed for user"""
        logger.info(f"Creating personalized feed for {user_id}: {feed_name}")

        # Route feed creation through highway
        packet = {
            'type': 'personalized_feed_creation',
            'user_id': user_id,
            'feed_name': feed_name,
            'preferred_categories': [c.value for c in preferred_categories],
            'emotional_preferences': [e.value for e in emotional_preferences],
            'creation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'resonance_engine')

        feed = PersonalizedFeed(
            user_id=user_id,
            feed_name=feed_name,
            preferred_categories=preferred_categories,
            emotional_preferences=emotional_preferences
        )

        self.user_feeds[user_id] = feed

        logger.info(f"Personalized feed created for {user_id}")

        return feed

    def deliver_tailored_content(self, user_id: str, feed_id: Optional[str] = None,
                               content_limit: int = 10) -> List[TailoredContent]:
        """Deliver AI-tailored content to user based on resonance patterns"""
        logger.info(f"Delivering tailored content to {user_id}")

        if user_id not in self.user_feeds:
            # Create default feed
            self.create_personalized_feed(user_id, "Default Feed",
                                        [ContentCategory.FINANCIAL_NEWS],
                                        [EmotionalTone.NEUTRAL])

        user_feed = self.user_feeds[user_id]

        # Route content delivery through highway
        packet = {
            'type': 'tailored_content_delivery',
            'user_id': user_id,
            'feed_id': feed_id,
            'content_limit': content_limit,
            'delivery_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'resonance_engine')

        # Select and rank content based on user preferences and resonance history
        candidate_content = self._select_candidate_content(user_feed)
        ranked_content = self._rank_content_by_resonance(candidate_content, user_feed)

        # Deliver top content
        delivered_content = ranked_content[:content_limit]

        # Update user content history
        for content in delivered_content:
            user_feed.content_history.append(content.id)

        user_feed.last_updated = datetime.now()

        logger.info(f"Tailored content delivered to {user_id}: {len(delivered_content)} items")

        return delivered_content

    def analyze_content_resonance(self, content_id: str, user_id: str,
                                engagement_data: Dict[str, Any]) -> ContentResonance:
        """Analyze how content resonated with user"""
        logger.info(f"Analyzing content resonance: {content_id} for {user_id}")

        # Route resonance analysis through highway
        packet = {
            'type': 'content_resonance_analysis',
            'content_id': content_id,
            'user_id': user_id,
            'engagement_data': engagement_data,
            'analysis_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'resonance_engine')

        # AI-powered resonance analysis
        resonance_level = self._calculate_resonance_level(content_id, user_id, engagement_data)
        emotional_impact = self._assess_emotional_impact(engagement_data)
        engagement_metrics = self._calculate_engagement_metrics(engagement_data)
        behavioral_response = self._analyze_behavioral_response(engagement_data)

        resonance = ContentResonance(
            content_id=content_id,
            user_id=user_id,
            resonance_level=resonance_level,
            emotional_impact=emotional_impact,
            engagement_metrics=engagement_metrics,
            behavioral_response=behavioral_response
        )

        self.resonance_data.append(resonance)

        # Update user resonance patterns
        if user_id in self.user_feeds:
            user_feed = self.user_feeds[user_id]
            content_category = self.content_library.get(content_id)
            if content_category and hasattr(content_category, 'category'):
                category_key = content_category.category.value
                current_score = user_feed.resonance_patterns.get(category_key, 0.5)
                new_score = (current_score + (1.0 if resonance_level in [ResonanceLevel.HIGH, ResonanceLevel.MEDIUM] else 0.0)) / 2
                user_feed.resonance_patterns[category_key] = new_score

        logger.info(f"Content resonance analyzed: {content_id} - {resonance_level.value}")

        return resonance

    def generate_content_insights(self, category: ContentCategory,
                                time_period: str = "24h") -> Dict[str, Any]:
        """Generate AI-powered insights from content analysis"""
        logger.info(f"Generating content insights for {category.value}")

        # Route insights generation through highway
        packet = {
            'type': 'content_insights_generation',
            'category': category.value,
            'time_period': time_period,
            'generation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'resonance_engine')

        # Analyze content in category
        category_content = [c for c in self.content_library.values() if c.category == category]

        if time_period == "24h":
            cutoff_time = datetime.now() - timedelta(hours=24)
            category_content = [c for c in category_content if c.published_at > cutoff_time]

        insights = {
            'content_volume': len(category_content),
            'sentiment_distribution': self._analyze_sentiment_distribution(category_content),
            'key_themes': self._extract_key_themes(category_content),
            'market_impact': self._assess_market_impact(category_content),
            'resonance_patterns': self._analyze_resonance_patterns(category),
            'trend_predictions': self._generate_trend_predictions(category_content),
            'recommendations': self._generate_content_recommendations(category)
        }

        logger.info(f"Content insights generated for {category.value}: {insights['content_volume']} items analyzed")

        return insights

    def _fetch_raw_content(self, categories: List[ContentCategory], hours_back: int) -> List[Dict[str, Any]]:
        """Fetch raw content from various sources"""
        # Simulate content fetching (would integrate with real APIs)
        raw_content = []

        # Sample content for demonstration
        sample_content = [
            {
                'title': 'Federal Reserve Signals Potential Rate Cuts',
                'summary': 'Fed Chair indicates possible interest rate reductions in upcoming meetings.',
                'content': 'Full article content here...',
                'source_url': 'https://bloomberg.com/fed-rate-signal',
                'category': ContentCategory.ECONOMIC_INDICATORS,
                'published_at': datetime.now() - timedelta(hours=2)
            },
            {
                'title': 'Tech Stocks Rally on AI Optimism',
                'summary': 'Major technology companies show strong performance amid AI developments.',
                'content': 'Full article content here...',
                'source_url': 'https://reuters.com/tech-rally',
                'category': ContentCategory.MARKET_ANALYSIS,
                'published_at': datetime.now() - timedelta(hours=4)
            },
            {
                'title': 'Cryptocurrency Market Shows Resilience',
                'summary': 'Digital assets maintain value despite market volatility.',
                'content': 'Full article content here...',
                'source_url': 'https://coindesk.com/crypto-resilience',
                'category': ContentCategory.CRYPTOCURRENCY,
                'published_at': datetime.now() - timedelta(hours=6)
            }
        ]

        # Filter by categories and time
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        filtered_content = [
            item for item in sample_content
            if item['category'] in categories and item['published_at'] > cutoff_time
        ]

        raw_content.extend(filtered_content)

        return raw_content

    def _process_and_tailor_content(self, raw_item: Dict[str, Any]) -> Optional[TailoredContent]:
        """Process raw content and create tailored version"""
        try:
            # AI-powered content processing
            emotional_tone = self._analyze_emotional_tone(raw_item['title'] + " " + raw_item['summary'])
            sentiment_score = self._calculate_sentiment_score(raw_item['content'])
            key_insights = self._extract_key_insights(raw_item['content'])
            related_symbols = self._identify_related_symbols(raw_item['content'])
            resonance_score = self._calculate_base_resonance_score(raw_item)

            tailored_content = TailoredContent(
                title=raw_item['title'],
                summary=raw_item['summary'],
                full_content=raw_item['content'],
                source_url=raw_item['source_url'],
                category=raw_item['category'],
                emotional_tone=emotional_tone,
                resonance_score=resonance_score,
                target_audience=self._determine_target_audience(raw_item['category'], emotional_tone),
                key_insights=key_insights,
                related_symbols=related_symbols,
                published_at=raw_item['published_at'],
                sentiment_score=sentiment_score,
                urgency_level=self._assess_urgency_level(raw_item)
            )

            return tailored_content

        except Exception as e:
            logger.error(f"Failed to process content: {str(e)}")
            return None

    def _analyze_emotional_tone(self, text: str) -> EmotionalTone:
        """Analyze emotional tone of content"""
        # Simulate emotional tone analysis
        text_lower = text.lower()

        if any(word in text_lower for word in ['bullish', 'rally', 'gains', 'optimism']):
            return EmotionalTone.OPTIMISTIC
        elif any(word in text_lower for word in ['caution', 'risk', 'decline', 'concern']):
            return EmotionalTone.CAUTIOUS
        elif any(word in text_lower for word in ['breakthrough', 'exciting', 'major']):
            return EmotionalTone.ENTHUSIASTIC
        elif any(word in text_lower for word in ['crisis', 'urgent', 'critical']):
            return EmotionalTone.URGENT
        else:
            return EmotionalTone.NEUTRAL

    def _calculate_sentiment_score(self, content: str) -> float:
        """Calculate sentiment score of content"""
        # Simulate sentiment analysis
        positive_words = ['growth', 'increase', 'positive', 'strong', 'bullish', 'optimism']
        negative_words = ['decline', 'fall', 'negative', 'weak', 'bearish', 'concern']

        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        total_words = positive_count + negative_count
        if total_words == 0:
            return 0.0

        return (positive_count - negative_count) / total_words

    def _extract_key_insights(self, content: str) -> List[str]:
        """Extract key insights from content"""
        # Simulate insight extraction
        insights = []

        if 'fed' in content.lower():
            insights.append("Federal Reserve policy impacts market sentiment")

        if 'growth' in content.lower():
            insights.append("Economic growth indicators show positive trends")

        if 'volatility' in content.lower():
            insights.append("Market volatility requires careful risk management")

        return insights if insights else ["Content analysis in progress"]

    def _identify_related_symbols(self, content: str) -> List[str]:
        """Identify related financial symbols"""
        # Simulate symbol extraction
        symbols = []

        if 'apple' in content.lower() or 'aapl' in content.lower():
            symbols.append('AAPL')
        if 'microsoft' in content.lower() or 'msft' in content.lower():
            symbols.append('MSFT')
        if 'tesla' in content.lower() or 'tsla' in content.lower():
            symbols.append('TSLA')
        if 'bitcoin' in content.lower() or 'btc' in content.lower():
            symbols.append('BTC')
        if 'sp500' in content.lower() or 's&p' in content.lower():
            symbols.append('SPY')

        return symbols

    def _calculate_base_resonance_score(self, content_item: Dict[str, Any]) -> float:
        """Calculate base resonance score for content"""
        # Simulate resonance scoring
        base_score = 0.5

        # Category popularity
        category_multipliers = {
            ContentCategory.MARKET_ANALYSIS: 1.2,
            ContentCategory.FINANCIAL_NEWS: 1.1,
            ContentCategory.CRYPTOCURRENCY: 1.3,
            ContentCategory.ECONOMIC_INDICATORS: 1.0
        }

        category = content_item['category']
        base_score *= category_multipliers.get(category, 1.0)

        # Recency bonus
        hours_old = (datetime.now() - content_item['published_at']).total_seconds() / 3600
        recency_multiplier = max(0.5, 1.0 - (hours_old / 24))  # Decay over 24 hours
        base_score *= recency_multiplier

        return round(base_score, 2)

    def _determine_target_audience(self, category: ContentCategory, tone: EmotionalTone) -> List[str]:
        """Determine target audience segments"""
        audience_mapping = {
            ContentCategory.FINANCIAL_NEWS: ['retail_investors', 'financial_professionals'],
            ContentCategory.MARKET_ANALYSIS: ['active_traders', 'portfolio_managers'],
            ContentCategory.CRYPTOCURRENCY: ['crypto_enthusiasts', 'tech_investors'],
            ContentCategory.ECONOMIC_INDICATORS: ['economists', 'policy_makers'],
            ContentCategory.PERSONAL_FINANCE: ['individuals', 'families'],
            ContentCategory.STARTUP_ECOSYSTEM: ['entrepreneurs', 'venture_capitalists']
        }

        base_audience = audience_mapping.get(category, ['general_investors'])

        # Adjust based on emotional tone
        if tone == EmotionalTone.OPTIMISTIC:
            base_audience.extend(['growth_investors', 'bullish_traders'])
        elif tone == EmotionalTone.CAUTIOUS:
            base_audience.extend(['risk_averse_investors', 'conservative_traders'])

        return list(set(base_audience))

    def _assess_urgency_level(self, content_item: Dict[str, Any]) -> str:
        """Assess urgency level of content"""
        title_lower = content_item['title'].lower()

        if any(word in title_lower for word in ['breaking', 'urgent', 'crisis', 'emergency']):
            return 'high'
        elif any(word in title_lower for word in ['alert', 'warning', 'important']):
            return 'medium'
        else:
            return 'normal'

    def _select_candidate_content(self, user_feed: PersonalizedFeed) -> List[TailoredContent]:
        """Select candidate content for user feed"""
        candidate_content = []

        # Get content from preferred categories
        for category in user_feed.preferred_categories:
            category_content = [c for c in self.content_library.values() if c.category == category]
            candidate_content.extend(category_content)

        # Remove already seen content
        unseen_content = [c for c in candidate_content if c.id not in user_feed.content_history]

        return unseen_content

    def _rank_content_by_resonance(self, content_list: List[TailoredContent],
                                 user_feed: PersonalizedFeed) -> List[TailoredContent]:
        """Rank content by predicted resonance"""
        scored_content = []

        for content in content_list:
            # Base resonance score
            score = content.resonance_score

            # Category preference bonus
            if content.category in user_feed.preferred_categories:
                category_resonance = user_feed.resonance_patterns.get(content.category.value, 0.5)
                score *= (1 + category_resonance)

            # Emotional tone preference bonus
            if content.emotional_tone in user_feed.emotional_preferences:
                score *= 1.2

            # Recency bonus
            hours_old = (datetime.now() - content.published_at).total_seconds() / 3600
            recency_bonus = max(0, 1.0 - (hours_old / 24))
            score *= (1 + recency_bonus * 0.5)

            scored_content.append((content, score))

        # Sort by score (descending)
        scored_content.sort(key=lambda x: x[1], reverse=True)

        return [content for content, score in scored_content]

    def _calculate_resonance_level(self, content_id: str, user_id: str,
                                 engagement_data: Dict[str, Any]) -> ResonanceLevel:
        """Calculate resonance level from engagement data"""
        engagement_score = 0

        # Reading time (minutes)
        reading_time = engagement_data.get('reading_time_minutes', 0)
        if reading_time > 10:
            engagement_score += 3
        elif reading_time > 5:
            engagement_score += 2
        elif reading_time > 2:
            engagement_score += 1

        # Interactions
        if engagement_data.get('shared', False):
            engagement_score += 2
        if engagement_data.get('saved', False):
            engagement_score += 1
        if engagement_data.get('comments', False):
            engagement_score += 1

        # Emotional response
        emotional_response = engagement_data.get('emotional_response', 'neutral')
        if emotional_response in ['very_positive', 'inspiring']:
            engagement_score += 2
        elif emotional_response == 'positive':
            engagement_score += 1

        # Determine resonance level
        if engagement_score >= 5:
            return ResonanceLevel.HIGH
        elif engagement_score >= 3:
            return ResonanceLevel.MEDIUM
        elif engagement_score >= 1:
            return ResonanceLevel.LOW
        else:
            return ResonanceLevel.NONE

    def _assess_emotional_impact(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess emotional impact of content"""
        return {
            'immediate_emotion': engagement_data.get('emotional_response', 'neutral'),
            'lasting_impact': engagement_data.get('lasting_impression', 'minimal'),
            'behavioral_change': engagement_data.get('inspired_action', False),
            'social_sharing': engagement_data.get('shared', False)
        }

    def _calculate_engagement_metrics(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        return {
            'reading_time': engagement_data.get('reading_time_minutes', 0),
            'completion_rate': engagement_data.get('completion_rate', 0.0),
            'interaction_depth': engagement_data.get('interaction_count', 0),
            'return_visits': engagement_data.get('return_visits', 0)
        }

    def _analyze_behavioral_response(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavioral response to content"""
        return {
            'content_saved': engagement_data.get('saved', False),
            'further_research': engagement_data.get('searched_related', False),
            'investment_action': engagement_data.get('investment_decision', False),
            'social_discussion': engagement_data.get('discussed', False)
        }

    def _analyze_sentiment_distribution(self, content_list: List[TailoredContent]) -> Dict[str, float]:
        """Analyze sentiment distribution in content"""
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}

        for content in content_list:
            if content.sentiment_score > 0.1:
                sentiments['positive'] += 1
            elif content.sentiment_score < -0.1:
                sentiments['negative'] += 1
            else:
                sentiments['neutral'] += 1

        total = len(content_list)
        return {k: v/total for k, v in sentiments.items()}

    def _extract_key_themes(self, content_list: List[TailoredContent]) -> List[str]:
        """Extract key themes from content"""
        # Simulate theme extraction
        themes = []

        all_titles = ' '.join([c.title for c in content_list]).lower()

        if 'fed' in all_titles or 'federal reserve' in all_titles:
            themes.append('monetary_policy')
        if 'growth' in all_titles or 'earnings' in all_titles:
            themes.append('economic_growth')
        if 'volatility' in all_titles or 'risk' in all_titles:
            themes.append('market_volatility')
        if 'crypto' in all_titles or 'bitcoin' in all_titles:
            themes.append('cryptocurrency')

        return themes if themes else ['general_market_news']

    def _assess_market_impact(self, content_list: List[TailoredContent]) -> Dict[str, Any]:
        """Assess market impact of content"""
        # Simulate market impact assessment
        return {
            'overall_sentiment': 'mixed',
            'volatility_expectation': 'moderate',
            'key_drivers': ['economic_data', 'corporate_earnings'],
            'risk_level': 'medium',
            'investment_opportunities': ['defensive_sectors', 'growth_stocks']
        }

    def _analyze_resonance_patterns(self, category: ContentCategory) -> Dict[str, Any]:
        """Analyze resonance patterns for category"""
        # Simulate resonance pattern analysis
        return {
            'average_resonance': 0.65,
            'peak_resonance_times': ['morning', 'market_open'],
            'preferred_tones': ['optimistic', 'neutral'],
            'engagement_drivers': ['market_analysis', 'investment_opportunities']
        }

    def _generate_trend_predictions(self, content_list: List[TailoredContent]) -> List[str]:
        """Generate trend predictions from content analysis"""
        predictions = [
            "Continued focus on AI-driven investment strategies",
            "Growing interest in sustainable and ESG investments",
            "Increased volatility in cryptocurrency markets",
            "Shift toward personalized investment approaches"
        ]

        return predictions

    def _generate_content_recommendations(self, category: ContentCategory) -> List[str]:
        """Generate content recommendations for category"""
        recommendations = [
            "Increase coverage of AI and machine learning applications",
            "Provide more personalized investment insights",
            "Focus on sustainable and ethical investment opportunities",
            "Enhance real-time market analysis and alerts"
        ]

        return recommendations

# Global ResonanceEngine instance
resonance_engine = ResonanceEngine()

def get_resonance_engine() -> ResonanceEngine:
    """Get the global ResonanceEngine instance"""
    return resonance_engine

# Convenience functions
def aggregate_financial_content(categories: List[ContentCategory] = None,
                              hours_back: int = 24) -> List[TailoredContent]:
    """Aggregate financial content from multiple sources"""
    return resonance_engine.aggregate_financial_content(categories, hours_back)

def create_personalized_feed(user_id: str, feed_name: str,
                           preferred_categories: List[ContentCategory],
                           emotional_preferences: List[EmotionalTone]) -> PersonalizedFeed:
    """Create personalized content feed"""
    return resonance_engine.create_personalized_feed(user_id, feed_name, preferred_categories, emotional_preferences)

def deliver_tailored_content(user_id: str, feed_id: Optional[str] = None,
                           content_limit: int = 10) -> List[TailoredContent]:
    """Deliver AI-tailored content"""
    return resonance_engine.deliver_tailored_content(user_id, feed_id, content_limit)

def analyze_content_resonance(content_id: str, user_id: str,
                            engagement_data: Dict[str, Any]) -> ContentResonance:
    """Analyze content resonance"""
    return resonance_engine.analyze_content_resonance(content_id, user_id, engagement_data)

def generate_content_insights(category: ContentCategory, time_period: str = "24h") -> Dict[str, Any]:
    """Generate content insights"""
    return resonance_engine.generate_content_insights(category, time_period)
