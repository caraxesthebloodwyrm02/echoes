#!/usr/bin/env python3
"""Python 3.14 search utility using the Echoes TwitterMonitor."""

import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from tweepy import TooManyRequests

# Ensure the project root is on the import path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from twitter_credentials import check_credentials, get_twitter_credentials

from app.social_monitoring import TwitterMonitor

DEFAULT_QUERY = os.getenv(
    "PYTHON_SEARCH_QUERY",
    "python 3.14 (update OR release OR community OR forum OR review OR beta OR alpha) -is:retweet",
)
DEFAULT_DAYS = int(os.getenv("PYTHON_SEARCH_DAYS", "30"))
DEFAULT_LIMIT = max(10, min(int(os.getenv("PYTHON_SEARCH_LIMIT", "50")), 100))
OUTPUT_DIR = Path(os.getenv("PYTHON_SEARCH_OUTPUT_DIR", ".")).resolve()


def _build_monitor() -> TwitterMonitor | None:
    creds = get_twitter_credentials()
    if not check_credentials(creds):
        print("❌ No valid Twitter credentials found in environment variables.")
        print("   Run `python twitter_credentials.py` to verify your setup.")
        return None

    config: dict[str, str] = {
        key: value
        for key, value in {
            "bearer_token": creds.get("bearer_token"),
            "consumer_key": creds.get("api_key"),
            "consumer_secret": creds.get("api_secret"),
            "access_token": creds.get("access_token"),
            "access_token_secret": creds.get("access_token_secret"),
        }.items()
        if value
    }

    try:
        monitor = TwitterMonitor(config)
        print("✅ Twitter monitor initialized successfully")
        return monitor
    except Exception as exc:  # pragma: no cover - initialization failures
        print(f"❌ Failed to initialize Twitter monitor: {exc}")
        print("   Ensure your credentials grant Twitter API v2 read access.")
        return None


def _format_iso(dt: datetime) -> str:
    return dt.replace(tzinfo=UTC).isoformat()


def _save_results(tweets, query: str, start_time: str) -> None:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"python_3_14_search_{timestamp}.json"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tweet_data = [
        {
            "platform": tweet.platform,
            "post_id": tweet.post_id,
            "author": tweet.author,
            "content": tweet.content,
            "created_at": _format_iso(tweet.created_at),
            "url": tweet.url,
            "metrics": tweet.metrics,
            "sentiment": tweet.sentiment,
            "tags": tweet.tags,
        }
        for tweet in tweets
    ]

    payload = {
        "search_query": query,
        "search_timestamp": datetime.now(UTC).isoformat(),
        "total_tweets": len(tweets),
        "date_range": {"start": start_time, "end": datetime.now(UTC).isoformat()},
        "tweets": tweet_data,
    }

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    print(f"💾 Results saved to: {output_path}")


def main():
    """Search for Python 3.14 related tweets."""
    print("🔍 Searching for Python 3.14 updates, community discussions, and reviews...")
    print("=" * 80)

    monitor = _build_monitor()
    if not monitor:
        return

    query = DEFAULT_QUERY
    days = DEFAULT_DAYS
    limit = DEFAULT_LIMIT

    end_time = datetime.now(UTC)
    start_time_dt = end_time - timedelta(days=days)
    start_time = start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"📅 Searching from: {start_time_dt.date()} to {end_time.date()}")
    print(f"🔎 Query: {query}")
    print(f"🎯 Limit per request: {limit}")
    print()

    try:
        tweets = monitor.search(
            query=query, limit=limit, start_time=start_time, sort_order="relevancy"
        )

        if not tweets:
            print("📭 No tweets returned. This can happen when:")
            print(
                "   • The API quota for the Free plan (100 tweets/month) is exhausted"
            )
            print(
                "   • The query is too restrictive or outside the recent 7-day window"
            )
            print(
                "   • Twitter temporarily throttled the request (check logs for details)"
            )
            return

        print(f"📊 Found {len(tweets)} tweets about Python 3.14:")
        print("-" * 80)

        # Track sentiment distribution
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        total_engagement = 0

        for i, tweet in enumerate(tweets, 1):
            # Calculate engagement score
            metrics = tweet.metrics
            engagement = (
                metrics.get("likes", 0)
                + metrics.get("retweets", 0) * 2
                + metrics.get("replies", 0) * 3
            )
            total_engagement += engagement

            # Categorize sentiment
            if tweet.sentiment:
                polarity = tweet.sentiment["polarity"]
                if polarity > 0.1:
                    sentiment_counts["positive"] += 1
                    sentiment_emoji = "😊"
                elif polarity < -0.1:
                    sentiment_counts["negative"] += 1
                    sentiment_emoji = "😞"
                else:
                    sentiment_counts["neutral"] += 1
                    sentiment_emoji = "😐"
            else:
                sentiment_emoji = "🤔"

            # Print tweet details
            print(
                f"\n{i}. @{tweet.author} ({tweet.created_at.strftime('%Y-%m-%d %H:%M')})"
            )
            print(f"   {tweet.content}")
            print(f"   🔗 {tweet.url}")
            print(
                f"   👍 {metrics.get('likes', 0)}  🔄 {metrics.get('retweets', 0)}  💬 {metrics.get('replies', 0)}  📊 {engagement} pts"
            )

            # Show sentiment
            if tweet.sentiment:
                print(
                    f"   {sentiment_emoji} Sentiment: {tweet.sentiment['polarity']:.2f} (subj: {tweet.sentiment['subjectivity']:.2f})"
                )

            # Show tags if available
            if tweet.tags:
                print(
                    f"   🏷️  Tags: {', '.join(tag[:25] for tag in tweet.tags[:3])}{'...' if len(tweet.tags) > 3 else ''}"
                )

            print("-" * 80)

        # Summary statistics
        print("\n📈 SUMMARY STATISTICS:")
        print(f"   Total Tweets: {len(tweets)}")
        print(
            f"   Average Engagement: {total_engagement / len(tweets):.1f} points per tweet"
        )
        print("   Sentiment Distribution:")
        print(
            f"     😊 Positive: {sentiment_counts['positive']} ({sentiment_counts['positive']/len(tweets)*100:.1f}%)"
        )
        print(
            f"     😐 Neutral: {sentiment_counts['neutral']} ({sentiment_counts['neutral']/len(tweets)*100:.1f}%)"
        )
        print(
            f"     😞 Negative: {sentiment_counts['negative']} ({sentiment_counts['negative']/len(tweets)*100:.1f}%)"
        )

        # Save results to file
        try:
            _save_results(tweets, query, start_time)
        except Exception as exc:
            print(f"⚠️  Could not save results to file: {exc}")

    except TooManyRequests:
        print(
            "⚠️ Rate limit encountered. The Free tier allows only 100 tweet reads/month."
        )
        print("   Wait for the quota to reset or upgrade your Twitter API plan.")
    except Exception as exc:  # pragma: no cover - unexpected failures
        print(f"❌ Search failed: {exc}")
        print(
            "   This might be due to API rate limits, authentication issues, or network problems."
        )


if __name__ == "__main__":
    main()
