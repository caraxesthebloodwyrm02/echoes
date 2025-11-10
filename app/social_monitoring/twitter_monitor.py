"""
X (Twitter) Monitor for Echoes AI Assistant

This module provides functionality to monitor and analyze content from X (Twitter).
It requires Twitter API v2 access with appropriate authentication.
"""

import logging

import tweepy

from . import SocialMonitor, SocialPost

logger = logging.getLogger(__name__)


class TwitterMonitor(SocialMonitor):
    """Monitor for X (Twitter) platform."""

    def __init__(self, config: dict | None = None):
        """Initialize the Twitter monitor.

        Args:
            config: Dictionary containing Twitter API credentials:
                - consumer_key: Twitter API key
                - consumer_secret: Twitter API secret key
                - access_token: Twitter access token
                - access_token_secret: Twitter access token secret
                - bearer_token: Twitter API v2 Bearer token
        """
        super().__init__(config)
        self.client = None
        self.api = None

    def authenticate(self) -> bool:
        """Authenticate with Twitter API."""
        try:
            # Try to use Bearer token first (Twitter API v2)
            if "bearer_token" in self.config:
                self.client = tweepy.Client(
                    bearer_token=self.config["bearer_token"], wait_on_rate_limit=True
                )
                logger.info("Authenticated with Twitter API v2 using Bearer token")
                return True

            # Fall back to OAuth 1.0a if Bearer token is not available
            elif all(
                k in self.config
                for k in [
                    "consumer_key",
                    "consumer_secret",
                    "access_token",
                    "access_token_secret",
                ]
            ):
                auth = tweepy.OAuth1UserHandler(
                    self.config["consumer_key"],
                    self.config["consumer_secret"],
                    self.config["access_token"],
                    self.config["access_token_secret"],
                )
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                logger.info("Authenticated with Twitter API v1.1")
                return True

            else:
                logger.error(
                    "Insufficient Twitter API credentials provided"
                    " (need either bearer_token or OAuth 1.0a credentials)"
                )
                return False

        except Exception as e:
            logger.error(f"Twitter authentication failed: {e}")
            return False

    def search(self, query: str, limit: int = 100, **kwargs) -> list[SocialPost]:
        """Search for tweets matching the query.

        Args:
            query: Search query string
            limit: Maximum number of results to return (1-100)
            **kwargs: Additional search parameters (e.g., start_time, end_time, max_results)

        Returns:
            List of SocialPost objects containing tweet data
        """
        if not self.client and not self.api:
            if not self.authenticate():
                return []

        try:
            posts = []

            # Use Twitter API v2 if available
            if self.client:
                max_results = min(limit, 100)  # Max 100 per request for standard v2

                # Prepare query parameters
                tweet_fields = [
                    "created_at",
                    "author_id",
                    "public_metrics",
                    "context_annotations",
                ]
                user_fields = ["name", "username", "profile_image_url"]

                # Make the API request
                response = self.client.search_recent_tweets(
                    query=query,
                    max_results=max_results,
                    tweet_fields=tweet_fields,
                    user_fields=user_fields,
                    expansions=["author_id"],
                    **kwargs,
                )

                # Process the response
                if not response.data:
                    logger.info("No tweets found matching the query")
                    return []

                # Create a mapping of user IDs to user objects
                users = {user.id: user for user in response.includes.get("users", [])}

                # Convert tweets to SocialPost objects
                for tweet in response.data:
                    author = users.get(tweet.author_id, {})
                    post = SocialPost(
                        platform="twitter",
                        post_id=str(tweet.id),
                        author=author.username if author else "unknown",
                        content=tweet.text,
                        created_at=tweet.created_at,
                        url=(
                            f"https://twitter.com/{author.username}/status/{tweet.id}"
                            if author
                            else ""
                        ),
                        metrics={
                            "likes": tweet.public_metrics.get("like_count", 0),
                            "retweets": tweet.public_metrics.get("retweet_count", 0),
                            "replies": tweet.public_metrics.get("reply_count", 0),
                            "quotes": tweet.public_metrics.get("quote_count", 0),
                            "impressions": tweet.public_metrics.get(
                                "impression_count", 0
                            ),
                        },
                    )

                    # Add context annotations as tags
                    if (
                        hasattr(tweet, "context_annotations")
                        and tweet.context_annotations
                    ):
                        for annotation in tweet.context_annotations:
                            if (
                                "entity" in annotation
                                and "name" in annotation["entity"]
                            ):
                                post.tags.append(annotation["entity"]["name"])

                    # Analyze sentiment
                    post.sentiment = self.analyze_sentiment(post)
                    posts.append(post)

            # Fall back to v1.1 API if v2 is not available
            elif self.api:
                tweets = self.api.search_tweets(
                    q=query, count=min(limit, 100), **kwargs
                )

                for tweet in tweets:
                    post = SocialPost(
                        platform="twitter",
                        post_id=str(tweet.id),
                        author=tweet.user.screen_name,
                        content=tweet.text,
                        created_at=tweet.created_at,
                        url=f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                        metrics={
                            "likes": tweet.favorite_count,
                            "retweets": tweet.retweet_count,
                            "replies": 0,  # Not available in v1.1 search
                            "quotes": 0,  # Not available in v1.1 search
                            "impressions": 0,  # Not available in v1.1 search
                        },
                    )

                    # Hashtags as tags
                    post.tags = [
                        f"#{hashtag['text']}"
                        for hashtag in tweet.entities.get("hashtags", [])
                    ]

                    # Analyze sentiment
                    post.sentiment = self.analyze_sentiment(post)
                    posts.append(post)

            logger.info(f"Retrieved {len(posts)} tweets for query: {query}")
            return posts

        except Exception as e:
            logger.error(f"Error searching Twitter: {e}")
            return []

    def get_user_timeline(
        self, username: str, limit: int = 100, **kwargs
    ) -> list[SocialPost]:
        """Get recent tweets from a specific user's timeline.

        Args:
            username: Twitter username (without @)
            limit: Maximum number of tweets to return (1-100)
            **kwargs: Additional parameters (e.g., exclude_replies, include_rts)

        Returns:
            List of SocialPost objects from the user's timeline
        """
        if not self.client and not self.api:
            if not self.authenticate():
                return []

        try:
            posts = []

            if self.client:
                # Get user ID from username
                user_response = self.client.get_user(
                    username=username, user_fields=["profile_image_url"]
                )

                if not user_response.data:
                    logger.error(f"User @{username} not found")
                    return []

                user_id = user_response.data.id

                # Get user's tweets
                tweet_fields = ["created_at", "public_metrics", "context_annotations"]

                tweets = self.client.get_users_tweets(
                    id=user_id,
                    max_results=min(limit, 100),
                    tweet_fields=tweet_fields,
                    **kwargs,
                )

                if not tweets.data:
                    logger.info(f"No tweets found for user @{username}")
                    return []

                for tweet in tweets.data:
                    post = SocialPost(
                        platform="twitter",
                        post_id=str(tweet.id),
                        author=username,
                        content=tweet.text,
                        created_at=tweet.created_at,
                        url=f"https://twitter.com/{username}/status/{tweet.id}",
                        metrics={
                            "likes": tweet.public_metrics.get("like_count", 0),
                            "retweets": tweet.public_metrics.get("retweet_count", 0),
                            "replies": tweet.public_metrics.get("reply_count", 0),
                            "quotes": tweet.public_metrics.get("quote_count", 0),
                            "impressions": tweet.public_metrics.get(
                                "impression_count", 0
                            ),
                        },
                    )

                    # Add context annotations as tags
                    if (
                        hasattr(tweet, "context_annotations")
                        and tweet.context_annotations
                    ):
                        for annotation in tweet.context_annotations:
                            if (
                                "entity" in annotation
                                and "name" in annotation["entity"]
                            ):
                                post.tags.append(annotation["entity"]["name"])

                    # Analyze sentiment
                    post.sentiment = self.analyze_sentiment(post)
                    posts.append(post)

            elif self.api:
                tweets = self.api.user_timeline(
                    screen_name=username,
                    count=min(limit, 200),  # v1.1 allows up to 200
                    **kwargs,
                )

                for tweet in tweets:
                    post = SocialPost(
                        platform="twitter",
                        post_id=str(tweet.id),
                        author=tweet.user.screen_name,
                        content=tweet.text,
                        created_at=tweet.created_at,
                        url=f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                        metrics={
                            "likes": tweet.favorite_count,
                            "retweets": tweet.retweet_count,
                            "replies": 0,  # Not available in v1.1
                            "quotes": 0,  # Not available in v1.1
                            "impressions": 0,  # Not available in v1.1
                        },
                    )

                    # Hashtags as tags
                    post.tags = [
                        f"#{hashtag['text']}"
                        for hashtag in tweet.entities.get("hashtags", [])
                    ]

                    # Analyze sentiment
                    post.sentiment = self.analyze_sentiment(post)
                    posts.append(post)

            logger.info(f"Retrieved {len(posts)} tweets from @{username}")
            return posts

        except Exception as e:
            logger.error(f"Error getting user timeline: {e}")
            return []

    def get_trending_topics(self, woeid: int = 1) -> list[dict[str, str]]:
        """Get trending topics for a specific location.

        Args:
            woeid: Yahoo! Where On Earth ID (default: 1 for worldwide)

        Returns:
            List of trending topics with name and tweet volume
        """
        if not self.api:
            if not self.authenticate() or not self.api:
                return []

        try:
            trends = self.api.get_place_trends(woeid)
            return [
                {
                    "name": trend["name"],
                    "tweet_volume": trend.get("tweet_volume", 0),
                    "url": trend.get("url", ""),
                }
                for trend in trends[0]["trends"]
            ]
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []
