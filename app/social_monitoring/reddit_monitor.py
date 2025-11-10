"""
Reddit Monitor for Echoes AI Assistant

This module provides functionality to monitor and analyze content from Reddit.
It requires Reddit API (praw) credentials for authentication.
"""

import logging
from datetime import datetime

import praw

from . import SocialMonitor, SocialPost

logger = logging.getLogger(__name__)


class RedditMonitor(SocialMonitor):
    """Monitor for Reddit platform."""

    def __init__(self, config: dict | None = None):
        """Initialize the Reddit monitor.

        Args:
            config: Dictionary containing Reddit API credentials:
                - client_id: Reddit API client ID
                - client_secret: Reddit API client secret
                - user_agent: Unique user agent for your application
                - username: (Optional) Reddit username
                - password: (Optional) Reddit password (required for certain actions)
        """
        super().__init__(config)
        self.reddit = None

    def authenticate(self) -> bool:
        """Authenticate with Reddit API using PRAW."""
        try:
            required = ["client_id", "client_secret", "user_agent"]
            if not all(k in self.config for k in required):
                logger.error("Missing required Reddit API credentials")
                return False

            self.reddit = praw.Reddit(
                client_id=self.config["client_id"],
                client_secret=self.config["client_secret"],
                user_agent=self.config["user_agent"],
                username=self.config.get("username"),
                password=self.config.get("password"),
            )

            # Verify authentication
            if not self.reddit.read_only:
                logger.info("Authenticated with Reddit API (read-write mode)")
            else:
                logger.info("Authenticated with Reddit API (read-only mode)")

            return True

        except Exception as e:
            logger.error(f"Reddit authentication failed: {e}")
            return False

    def search(
        self,
        query: str,
        limit: int = 100,
        subreddit: str | None = None,
        sort: str = "relevance",
        time_filter: str = "month",
        **kwargs,
    ) -> list[SocialPost]:
        """Search for posts on Reddit matching the query.

        Args:
            query: Search query string
            limit: Maximum number of results to return (1-1000)
            subreddit: Optional subreddit to search within
            sort: Sort method ('relevance', 'hot', 'top', 'new', 'comments')
            time_filter: Time period to search ('all', 'day', 'hour', 'month', 'week', 'year')
            **kwargs: Additional search parameters

        Returns:
            List of SocialPost objects containing Reddit post data
        """
        if not self.reddit and not self.authenticate():
            return []

        try:
            posts = []
            search_limit = min(max(1, limit), 1000)  # Reddit's max is 1000

            # Prepare search query
            search_query = query
            if subreddit:
                search_query = f"subreddit:{subreddit} {query}"

            # Execute search
            if sort == "relevance":
                results = self.reddit.subreddit("all").search(
                    search_query,
                    limit=search_limit,
                    sort=sort,
                    time_filter=time_filter,
                    **kwargs,
                )
            else:
                # For non-relevance sorts, we need to get the subreddit first
                sub = (
                    self.reddit.subreddit(subreddit) if subreddit else self.reddit.front
                )
                if sort == "hot":
                    results = sub.hot(limit=search_limit, **kwargs)
                elif sort == "new":
                    results = sub.new(limit=search_limit, **kwargs)
                elif sort == "top":
                    results = sub.top(
                        time_filter=time_filter, limit=search_limit, **kwargs
                    )
                elif sort == "rising":
                    results = sub.rising(limit=search_limit, **kwargs)
                else:
                    logger.warning(
                        f"Unsupported sort method: {sort}. Defaulting to 'relevance'"
                    )
                    return self.search(
                        query, limit, subreddit, "relevance", time_filter, **kwargs
                    )

            # Process results
            for submission in results:
                if not hasattr(submission, "title"):
                    continue

                # Get post content (selftext for text posts, URL for link posts)
                content = (
                    submission.selftext
                    if hasattr(submission, "selftext")
                    else submission.url
                )

                # Get post URL
                post_url = f"https://reddit.com{submission.permalink}"

                # Get post author
                author_name = (
                    submission.author.name if submission.author else "[deleted]"
                )

                # Create SocialPost
                post = SocialPost(
                    platform="reddit",
                    post_id=submission.id,
                    author=author_name,
                    content=f"{submission.title}\n\n{content}",
                    created_at=datetime.fromtimestamp(submission.created_utc),
                    url=post_url,
                    metrics={
                        "score": submission.score,
                        "upvotes": submission.ups,
                        "downvotes": submission.downs,
                        "comments": submission.num_comments,
                        "upvote_ratio": getattr(submission, "upvote_ratio", 1.0),
                    },
                    tags=[f"r/{submission.subreddit.display_name}"],
                )

                # Add post flair as tag if available
                if (
                    hasattr(submission, "link_flair_text")
                    and submission.link_flair_text
                ):
                    post.tags.append(f"flair:{submission.link_flair_text}")

                # Analyze sentiment
                post.sentiment = self.analyze_sentiment(post)
                posts.append(post)

                # Break if we've reached the limit
                if len(posts) >= search_limit:
                    break

            logger.info(f"Retrieved {len(posts)} Reddit posts for query: {query}")
            return posts

        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []

    def get_subreddit_posts(
        self,
        subreddit_name: str,
        limit: int = 100,
        sort: str = "hot",
        time_filter: str = "month",
        **kwargs,
    ) -> list[SocialPost]:
        """Get posts from a specific subreddit.

        Args:
            subreddit_name: Name of the subreddit (without r/)
            limit: Maximum number of posts to return (1-1000)
            sort: Sort method ('hot', 'new', 'top', 'rising', 'controversial')
            time_filter: Time period to filter by ('all', 'day', 'hour', 'month', 'week', 'year')
            **kwargs: Additional parameters

        Returns:
            List of SocialPost objects from the subreddit
        """
        return self.search(
            query="",  # Empty query to get all posts
            limit=limit,
            subreddit=subreddit_name,
            sort=sort,
            time_filter=time_filter,
            **kwargs,
        )

    def get_comments(
        self, post_id: str, limit: int = 100, sort: str = "top", **kwargs
    ) -> list[SocialPost]:
        """Get comments from a specific Reddit post.

        Args:
            post_id: ID of the Reddit post
            limit: Maximum number of comments to return (1-1000)
            sort: Sort method ('confidence', 'top', 'new', 'controversial', 'old', 'q&a')
            **kwargs: Additional parameters

        Returns:
            List of SocialPost objects representing comments
        """
        if not self.reddit and not self.authenticate():
            return []

        try:
            comments = []
            submission = self.reddit.submission(id=post_id)

            # Expand comment tree
            submission.comments.replace_more(limit=None)

            # Sort comments
            if sort == "confidence":
                submission.comment_sort = "confidence"
            elif sort == "top":
                submission.comment_sort = "top"
            elif sort == "new":
                submission.comment_sort = "new"
            elif sort == "controversial":
                submission.comment_sort = "controversial"
            elif sort == "old":
                submission.comment_sort = "old"
            elif sort == "q&a":
                submission.comment_sort = "q&a"

            # Process comments
            for i, comment in enumerate(submission.comments):
                if i >= limit:
                    break

                if not hasattr(comment, "body"):
                    continue

                # Create SocialPost for comment
                post = SocialPost(
                    platform="reddit_comment",
                    post_id=comment.id,
                    author=comment.author.name if comment.author else "[deleted]",
                    content=comment.body,
                    created_at=datetime.fromtimestamp(comment.created_utc),
                    url=f"https://reddit.com{comment.permalink}",
                    metrics={
                        "score": comment.score,
                        "upvotes": comment.ups,
                        "downvotes": comment.downs,
                        "gilded": comment.gilded,
                        "distinguished": 1 if comment.distinguished else 0,
                    },
                    tags=[f"r/{comment.subreddit.display_name}"],
                )

                # Analyze sentiment
                post.sentiment = self.analyze_sentiment(post)
                comments.append(post)

            logger.info(f"Retrieved {len(comments)} comments for post {post_id}")
            return comments

        except Exception as e:
            logger.error(f"Error getting Reddit comments: {e}")
            return []

    def get_user_posts(
        self, username: str, limit: int = 100, content_type: str = "submitted", **kwargs
    ) -> list[SocialPost]:
        """Get posts or comments from a specific Reddit user.

        Args:
            username: Reddit username
            limit: Maximum number of items to return (1-1000)
            content_type: Type of content to retrieve ('submitted', 'comments', 'saved', 'upvoted', 'downvoted')
            **kwargs: Additional parameters

        Returns:
            List of SocialPost objects from the user
        """
        if not self.reddit and not self.authenticate():
            return []

        try:
            redditor = self.reddit.redditor(username)
            items = []

            # Get user content based on type
            if content_type == "submitted":
                content = redditor.submissions.new(limit=limit, **kwargs)
            elif content_type == "comments":
                content = redditor.comments.new(limit=limit, **kwargs)
            elif content_type == "saved" and hasattr(redditor, "saved"):
                content = redditor.saved(limit=limit, **kwargs)
            elif content_type == "upvoted" and hasattr(redditor, "upvoted"):
                content = redditor.upvoted(limit=limit, **kwargs)
            elif content_type == "downvoted" and hasattr(redditor, "downvoted"):
                content = redditor.downvoted(limit=limit, **kwargs)
            else:
                logger.error(f"Unsupported content type: {content_type}")
                return []

            # Process items
            for item in content:
                if hasattr(item, "title"):  # Submission
                    post = SocialPost(
                        platform="reddit",
                        post_id=item.id,
                        author=item.author.name if item.author else "[deleted]",
                        content=f"{item.title}\n\n{item.selftext}"
                        if hasattr(item, "selftext")
                        else item.url,
                        created_at=datetime.fromtimestamp(item.created_utc),
                        url=f"https://reddit.com{item.permalink}",
                        metrics={
                            "score": item.score,
                            "upvotes": item.ups,
                            "downvotes": item.downs,
                            "comments": item.num_comments,
                            "upvote_ratio": getattr(item, "upvote_ratio", 1.0),
                        },
                        tags=[f"r/{item.subreddit.display_name}"],
                    )
                else:  # Comment
                    post = SocialPost(
                        platform="reddit_comment",
                        post_id=item.id,
                        author=item.author.name if item.author else "[deleted]",
                        content=item.body,
                        created_at=datetime.fromtimestamp(item.created_utc),
                        url=f"https://reddit.com{item.permalink}",
                        metrics={
                            "score": item.score,
                            "upvotes": item.ups,
                            "downvotes": item.downs,
                            "gilded": item.gilded,
                            "distinguished": 1 if item.distinguished else 0,
                        },
                        tags=[f"r/{item.subreddit.display_name}"],
                    )

                # Analyze sentiment
                post.sentiment = self.analyze_sentiment(post)
                items.append(post)

                # Break if we've reached the limit
                if len(items) >= limit:
                    break

            logger.info(
                f"Retrieved {len(items)} {content_type} items for user {username}"
            )
            return items

        except Exception as e:
            logger.error(f"Error getting user {content_type}: {e}")
            return []

    def get_popular_subreddits(self, limit: int = 25) -> list[dict[str, str]]:
        """Get a list of popular subreddits.

        Args:
            limit: Maximum number of subreddits to return (1-100)

        Returns:
            List of dictionaries containing subreddit information
        """
        if not self.reddit and not self.authenticate():
            return []

        try:
            subreddits = []
            for subreddit in self.reddit.subreddits.popular(limit=min(limit, 100)):
                subreddits.append(
                    {
                        "name": subreddit.display_name,
                        "title": subreddit.title,
                        "subscribers": subreddit.subscribers,
                        "active_users": getattr(subreddit, "active_user_count", 0),
                        "description": subreddit.public_description,
                        "url": f"https://reddit.com/r/{subreddit.display_name}",
                    }
                )

            logger.info(f"Retrieved {len(subreddits)} popular subreddits")
            return subreddits

        except Exception as e:
            logger.error(f"Error getting popular subreddits: {e}")
            return []
