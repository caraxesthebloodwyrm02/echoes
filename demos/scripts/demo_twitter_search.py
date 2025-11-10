# demo_twitter_search.py
import os
import time
from datetime import UTC, datetime, timedelta

from tweepy import TooManyRequests
from twitter_credentials import check_credentials, get_twitter_credentials

from app.social_monitoring import TwitterMonitor

AUTO_WAIT = os.getenv("TWITTER_WAIT_ON_RATE_LIMIT", "0").lower() in {"1", "true", "yes"}
MAX_WAIT_SECONDS = int(os.getenv("TWITTER_MAX_WAIT_SECONDS", "180"))
DEFAULT_LIMIT = max(10, min(int(os.getenv("TWITTER_SEARCH_LIMIT", "10")), 100))


def _pretty_duration(seconds: int) -> str:
    minutes, secs = divmod(max(seconds, 0), 60)
    if minutes and secs:
        return f"{minutes}m {secs}s"
    if minutes:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    return f"{secs} second{'s' if secs != 1 else ''}"


def build_monitor(creds):
    return TwitterMonitor(
        {
            "bearer_token": creds["bearer_token"],
            "consumer_key": creds["api_key"],
            "consumer_secret": creds["api_secret"],
            "access_token": creds["access_token"],
            "access_token_secret": creds["access_token_secret"],
        }
    )


def _parse_reset_time(header_value: str | None) -> int | None:
    if not header_value:
        return None
    try:
        reset_epoch = int(float(header_value))
        now = int(time.time())
        return max(reset_epoch - now, 0)
    except ValueError:
        return None


def search_tweets(monitor, query, days=7, limit=10, max_retries=3):
    end_time = datetime.now(UTC)
    start_time = (end_time - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    limit = max(10, min(limit, 100))

    for attempt in range(max_retries):
        try:
            return monitor.search(query=query, limit=limit, start_time=start_time)
        except TooManyRequests as e:
            headers = getattr(e, "response", None)
            reset_after = None
            if headers and hasattr(headers, "headers"):
                header_map = headers.headers
            else:
                header_map = getattr(e, "response_headers", {})

            reset_after = (
                _parse_reset_time(header_map.get("x-rate-limit-reset"))
                if header_map
                else None
            )
            wait_seconds = (
                reset_after
                if reset_after is not None
                else int(os.getenv("TWITTER_DEFAULT_WAIT", "60"))
            )

            pretty = _pretty_duration(wait_seconds)
            if not AUTO_WAIT or wait_seconds > MAX_WAIT_SECONDS:
                print(f"\n⚠️ Rate limit reached. Try again in about {pretty}.")
                return []

            print(f"\n⚠️ Rate limited. Waiting {pretty} before retry...")
            time.sleep(wait_seconds + 1)
        except Exception as e:
            print(f"\n⚠️ Error searching tweets: {e}")
            if attempt == max_retries - 1:  # Last attempt
                raise
            time.sleep(5)  # Wait 5 seconds before retry

    return []  # Return empty list if all retries fail


def display_tweets(tweets):
    if not tweets:
        print("\nNo tweets found matching the criteria.")
        return

    print(f"\n📊 Found {len(tweets)} tweets:")
    print("-" * 60)

    for idx, tweet in enumerate(tweets, 1):
        date = tweet.created_at.strftime("%Y-%m-%d")
        print(f"\n{idx}. @{tweet.author} ({date})")
        print(f"   {tweet.content[:120]}{'...' if len(tweet.content) > 120 else ''}")
        print(f"   🔗 {tweet.url}")

        metrics = getattr(tweet, "metrics", None)
        if metrics:
            likes = metrics.get("likes", 0)
            rts = metrics.get("retweets", 0)
            replies = metrics.get("replies", 0)
            print(f"   👍 {likes}  🔄 {rts}  💬 {replies}")


def main():
    print("🐦 Twitter Search Demo")
    print("=" * 50)

    creds = get_twitter_credentials()
    if not check_credentials(creds):
        print("❌ No valid Twitter API credentials found!")
        print("Please set up your credentials first.")
        return

    try:
        print("\n🔌 Initializing Twitter monitor...")
        monitor = build_monitor(creds)

        # Try a simpler query first
        query = os.getenv("TWITTER_SEARCH_QUERY", "Python 3.14 -is:retweet")
        print(f"\n🔍 Searching for: {query}")

        limit = DEFAULT_LIMIT
        tweets = search_tweets(
            monitor,
            query,
            days=int(os.getenv("TWITTER_SEARCH_DAYS", "7")),
            limit=limit,
            max_retries=int(os.getenv("TWITTER_SEARCH_RETRIES", "2")),
        )

        display_tweets(tweets)

    except KeyboardInterrupt:
        print("\n⏹️ Search cancelled by user.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        import traceback

        traceback.print_exc()
    finally:
        print("\n✨ Search completed.")


if __name__ == "__main__":
    main()
