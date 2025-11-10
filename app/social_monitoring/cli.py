"""
Command-line interface for Echoes Social Media Monitoring

This module provides a command-line interface to monitor and analyze
social media content from X (Twitter) and Reddit.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add parent directory to path to allow importing from app package
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.social_monitoring import RedditMonitor, TwitterMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SocialMediaCLI:
    """Command-line interface for social media monitoring."""

    def __init__(self):
        """Initialize the CLI with argument parser and commands."""
        self.parser = self._create_parser()
        self.twitter_monitor = None
        self.reddit_monitor = None

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Echoes Social Media Monitoring Tool",
            epilog='Example: python -m app.social_monitoring.cli twitter search "#AI" --limit 50 --output tweets.json',
        )

        # Global arguments
        parser.add_argument(
            "--config",
            type=str,
            default=".env",
            help="Path to configuration file (default: .env)",
        )
        parser.add_argument("--output", type=str, help="Output file path (JSON or TXT)")
        parser.add_argument(
            "--format",
            choices=["json", "txt"],
            default="json",
            help="Output format (default: json)",
        )

        # Subparsers for different commands
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")

        # Twitter commands
        twitter_parser = subparsers.add_parser("twitter", help="Twitter (X) commands")
        twitter_subparsers = twitter_parser.add_subparsers(
            dest="twitter_command", help="Twitter subcommands"
        )

        # Twitter search
        search_parser = twitter_subparsers.add_parser("search", help="Search Twitter")
        search_parser.add_argument("query", type=str, help="Search query")
        search_parser.add_argument(
            "--limit", type=int, default=100, help="Maximum number of results (1-100)"
        )
        search_parser.add_argument("--since", type=str, help="Start date (YYYY-MM-DD)")
        search_parser.add_argument("--until", type=str, help="End date (YYYY-MM-DD)")

        # Twitter user timeline
        timeline_parser = twitter_subparsers.add_parser(
            "timeline", help="Get user timeline"
        )
        timeline_parser.add_argument(
            "username", type=str, help="Twitter username (without @)"
        )
        timeline_parser.add_argument(
            "--limit", type=int, default=100, help="Maximum number of tweets (1-100)"
        )

        # Twitter trending
        trending_parser = twitter_subparsers.add_parser(
            "trending", help="Get trending topics"
        )
        trending_parser.add_argument(
            "--woeid",
            type=int,
            default=1,
            help="Yahoo! Where On Earth ID (default: 1 for worldwide)",
        )

        # Reddit commands
        reddit_parser = subparsers.add_parser("reddit", help="Reddit commands")
        reddit_subparsers = reddit_parser.add_subparsers(
            dest="reddit_command", help="Reddit subcommands"
        )

        # Reddit search
        reddit_search = reddit_subparsers.add_parser("search", help="Search Reddit")
        reddit_search.add_argument("query", type=str, help="Search query")
        reddit_search.add_argument(
            "--subreddit", type=str, help="Limit search to specific subreddit"
        )
        reddit_search.add_argument(
            "--limit", type=int, default=100, help="Maximum number of results (1-1000)"
        )
        reddit_search.add_argument(
            "--sort",
            choices=["relevance", "hot", "top", "new", "comments"],
            default="relevance",
            help="Sort method",
        )
        reddit_search.add_argument(
            "--time",
            choices=["all", "day", "hour", "month", "week", "year"],
            default="month",
            help="Time period to search",
        )

        # Reddit subreddit
        subreddit_parser = reddit_subparsers.add_parser(
            "subreddit", help="Get subreddit posts"
        )
        subreddit_parser.add_argument(
            "name", type=str, help="Subreddit name (without r/)"
        )
        subreddit_parser.add_argument(
            "--limit", type=int, default=100, help="Maximum number of posts (1-1000)"
        )
        subreddit_parser.add_argument(
            "--sort",
            choices=["hot", "new", "top", "rising", "controversial"],
            default="hot",
            help="Sort method",
        )
        subreddit_parser.add_argument(
            "--time",
            choices=["all", "day", "hour", "month", "week", "year"],
            default="month",
            help="Time period to filter",
        )

        # Reddit comments
        comments_parser = reddit_subparsers.add_parser(
            "comments", help="Get post comments"
        )
        comments_parser.add_argument("post_id", type=str, help="Reddit post ID")
        comments_parser.add_argument(
            "--limit", type=int, default=100, help="Maximum number of comments (1-1000)"
        )
        comments_parser.add_argument(
            "--sort",
            choices=["confidence", "top", "new", "controversial", "old", "q&a"],
            default="top",
            help="Sort method",
        )

        # Popular subreddits
        reddit_subparsers.add_parser("popular", help="Get popular subreddits")

        return parser

    def load_config(self, config_file: str = ".env") -> dict[str, Any]:
        """Load configuration from environment or .env file."""
        from dotenv import load_dotenv

        # Try to load from .env file
        config_path = Path(config_file)
        if config_path.exists():
            load_dotenv(config_path)
            logger.info(f"Loaded configuration from {config_path}")

        # Get Twitter API credentials
        twitter_config = {}
        if os.getenv("TWITTER_BEARER_TOKEN"):
            twitter_config["bearer_token"] = os.getenv("TWITTER_BEARER_TOKEN")
        else:
            twitter_config.update(
                {
                    "consumer_key": os.getenv("TWITTER_API_KEY", ""),
                    "consumer_secret": os.getenv("TWITTER_API_SECRET", ""),
                    "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
                    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
                }
            )

        # Get Reddit API credentials
        reddit_config = {
            "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
            "user_agent": os.getenv("REDDIT_USER_AGENT", "EchoesSocialMonitor/1.0"),
            "username": os.getenv("REDDIT_USERNAME", ""),
            "password": os.getenv("REDDIT_PASSWORD", ""),
        }

        return {"twitter": twitter_config, "reddit": reddit_config}

    def init_twitter(self, config: dict[str, str]) -> bool:
        """Initialize Twitter monitor with configuration."""
        try:
            self.twitter_monitor = TwitterMonitor(config)
            return self.twitter_monitor.authenticate()
        except Exception as e:
            logger.error(f"Failed to initialize Twitter: {e}")
            return False

    def init_reddit(self, config: dict[str, str]) -> bool:
        """Initialize Reddit monitor with configuration."""
        try:
            self.reddit_monitor = RedditMonitor(config)
            return self.reddit_monitor.authenticate()
        except Exception as e:
            logger.error(f"Failed to initialize Reddit: {e}")
            return False

    def handle_twitter_command(self, args: argparse.Namespace) -> list[dict[str, Any]]:
        """Handle Twitter subcommands."""
        if not self.twitter_monitor:
            config = self.load_config(args.config)["twitter"]
            if not self.init_twitter(config):
                logger.error("Twitter authentication failed")
                return []

        if args.twitter_command == "search":
            # Prepare search parameters
            params = {}
            if args.since:
                params["start_time"] = f"{args.since}T00:00:00Z"
            if args.until:
                end_date = datetime.strptime(args.until, "%Y-%m-%d") + timedelta(days=1)
                params["end_time"] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Execute search
            posts = self.twitter_monitor.search(
                query=args.query, limit=args.limit, **params
            )

            return [post.__dict__ for post in posts]

        elif args.twitter_command == "timeline":
            posts = self.twitter_monitor.get_user_timeline(
                username=args.username, limit=args.limit
            )
            return [post.__dict__ for post in posts]

        elif args.twitter_command == "trending":
            trends = self.twitter_monitor.get_trending_topics(woeid=args.woeid)
            return trends

        else:
            logger.error(f"Unknown Twitter command: {args.twitter_command}")
            return []

    def handle_reddit_command(self, args: argparse.Namespace) -> list[dict[str, Any]]:
        """Handle Reddit subcommands."""
        if not self.reddit_monitor:
            config = self.load_config(args.config)["reddit"]
            if not self.init_reddit(config):
                logger.error("Reddit authentication failed")
                return []

        if args.reddit_command == "search":
            posts = self.reddit_monitor.search(
                query=args.query,
                limit=args.limit,
                subreddit=args.subreddit,
                sort=args.sort,
                time_filter=args.time,
            )
            return [post.__dict__ for post in posts]

        elif args.reddit_command == "subreddit":
            posts = self.reddit_monitor.get_subreddit_posts(
                subreddit_name=args.name,
                limit=args.limit,
                sort=args.sort,
                time_filter=args.time,
            )
            return [post.__dict__ for post in posts]

        elif args.reddit_command == "comments":
            comments = self.reddit_monitor.get_comments(
                post_id=args.post_id, limit=args.limit, sort=args.sort
            )
            return [comment.__dict__ for comment in comments]

        elif args.reddit_command == "popular":
            subreddits = self.reddit_monitor.get_popular_subreddits(limit=25)
            return subreddits

        else:
            logger.error(f"Unknown Reddit command: {args.reddit_command}")
            return []

    def save_output(
        self, data: list[dict], output_path: str, format: str = "json"
    ) -> bool:
        """Save data to a file in the specified format."""
        if not data:
            logger.warning("No data to save")
            return False

        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == "txt":
                with open(output_path, "w", encoding="utf-8") as f:
                    for item in data:
                        f.write("=" * 80 + "\n")
                        if "content" in item:
                            f.write(f"{item.get('content', '')}\n\n")
                        if "author" in item:
                            f.write(f"Author: {item['author']}\n")
                        if "created_at" in item:
                            f.write(f"Date: {item['created_at']}\n")
                        if "url" in item:
                            f.write(f"URL: {item['url']}\n")
                        if "metrics" in item and item["metrics"]:
                            f.write(
                                "Metrics: "
                                + ", ".join(
                                    f"{k}={v}" for k, v in item["metrics"].items()
                                )
                                + "\n"
                            )
                        if "sentiment" in item and item["sentiment"]:
                            f.write(f"Sentiment: {item['sentiment']}\n")
                        f.write("\n")

            logger.info(f"Saved {len(data)} items to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving output: {e}")
            return False

    def run(self, args: list[str] | None = None) -> int:
        """Run the CLI with the given arguments."""
        try:
            # Parse command-line arguments
            parsed_args = self.parser.parse_args(args)

            # Check if no arguments were provided
            if not hasattr(parsed_args, "command") or parsed_args.command is None:
                self.parser.print_help()
                return 1

            # Execute the appropriate command
            result = []
            if parsed_args.command == "twitter":
                result = self.handle_twitter_command(parsed_args)
            elif parsed_args.command == "reddit":
                result = self.handle_reddit_command(parsed_args)
            else:
                logger.error(f"Unknown command: {parsed_args.command}")
                return 1

            # Save or print the result
            if parsed_args.output:
                self.save_output(result, parsed_args.output, parsed_args.format)
            else:
                print(json.dumps(result, indent=2))

            return 0

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return 1


def main():
    """Entry point for the CLI."""
    cli = SocialMediaCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
