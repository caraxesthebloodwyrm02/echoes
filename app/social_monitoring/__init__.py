"""
Social Media Monitoring Module for Echoes AI Assistant

This module provides tools to monitor and analyze content from social media platforms
like X (Twitter) and Reddit. It's designed to track discussions, trends, and sentiment
around specific topics or entities.

Key Features:
- X (Twitter) API integration for tracking tweets and trends
- Reddit API integration for monitoring subreddits and discussions
- Sentiment analysis and trend detection
- Configurable data collection and filtering
- Export capabilities for further analysis

Dependencies:
    pip install tweepy praw textblob python-dotenv
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SocialPost:
    """Represents a social media post from any platform."""

    platform: str
    post_id: str
    author: str
    content: str
    created_at: datetime
    url: str
    metrics: dict[str, int] = field(default_factory=dict)
    sentiment: dict[str, float] | None = None
    tags: list[str] = field(default_factory=list)


class SocialMonitor:
    """Base class for social media monitoring."""

    def __init__(self, config: dict | None = None):
        """Initialize the social monitor with configuration.

        Args:
            config: Dictionary containing API keys and other configuration
        """
        self.config = config or {}
        self.posts: list[SocialPost] = []

    def authenticate(self) -> bool:
        """Authenticate with the social media API.

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement authenticate()")

    def search(self, query: str, limit: int = 100, **kwargs) -> list[SocialPost]:
        """Search for posts matching the given query.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            **kwargs: Platform-specific search parameters

        Returns:
            List of SocialPost objects matching the query
        """
        raise NotImplementedError("Subclasses must implement search()")

    def analyze_sentiment(self, post: SocialPost) -> dict[str, float]:
        """Analyze the sentiment of a post's content.

        Args:
            post: SocialPost to analyze

        Returns:
            Dictionary with sentiment scores (polarity, subjectivity)
        """
        try:
            from textblob import TextBlob

            analysis = TextBlob(post.content)
            return {
                "polarity": analysis.sentiment.polarity,
                "subjectivity": analysis.sentiment.subjectivity,
            }
        except ImportError:
            logger.warning("TextBlob not installed. Install with: pip install textblob")
            return {"polarity": 0.0, "subjectivity": 0.0}

    def save_to_file(
        self, posts: list[SocialPost], filename: str, format: str = "json"
    ) -> bool:
        """Save posts to a file.

        Args:
            posts: List of SocialPost objects to save
            filename: Output filename
            format: Output format ('json' or 'txt')

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            output_dir = Path("data/social_media")
            output_dir.mkdir(parents=True, exist_ok=True)

            filepath = output_dir / f"{filename}.{format}"

            if format == "json":
                import json

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(
                        [post.__dict__ for post in posts], f, indent=2, default=str
                    )
            elif format == "txt":
                with open(filepath, "w", encoding="utf-8") as f:
                    for post in posts:
                        f.write(f"--- {post.platform.upper()} POST ---\n")
                        f.write(f"Author: {post.author}\n")
                        f.write(f"Date: {post.created_at}\n")
                        f.write(f"URL: {post.url}\n")
                        f.write(f"Content: {post.content}\n\n")

            logger.info(f"Saved {len(posts)} posts to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving posts to file: {e}")
            return False


# Import platform-specific implementations
try:
    from .twitter_monitor import TwitterMonitor
except ImportError as e:
    logger.warning(f"Could not import TwitterMonitor: {e}")
    TwitterMonitor = None

try:
    from .reddit_monitor import RedditMonitor
except ImportError as e:
    logger.warning(f"Could not import RedditMonitor: {e}")
    RedditMonitor = None

__all__ = ["SocialMonitor", "SocialPost", "TwitterMonitor", "RedditMonitor"]
