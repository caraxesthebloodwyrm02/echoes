# Social Media Monitoring for Echoes AI

A comprehensive social media monitoring module for tracking and analyzing content from X (Twitter) and Reddit.

## Features

- **X (Twitter) Integration**:
  - Search tweets by keyword, user, or hashtag
  - Get user timelines and trending topics
  - Support for both Twitter API v2 and v1.1

- **Reddit Integration**:
  - Search posts and comments across Reddit
  - Get posts from specific subreddits
  - Retrieve user posts and comments
  - Get popular subreddits

- **Analysis Tools**:
  - Sentiment analysis using TextBlob
  - Content categorization and tagging
  - Metrics tracking (likes, retweets, upvotes, etc.)
  - Export to JSON or text format

## Installation

1. Install required dependencies:
   ```bash
   pip install tweepy praw textblob python-dotenv
   ```

2. Set up environment variables in a `.env` file:
   ```env
   # Twitter API (v2 or v1.1)
   TWITTER_BEARER_TOKEN=your_bearer_token
   # OR
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

   # Reddit API
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=your_user_agent
   REDDIT_USERNAME=your_username  # Optional
   REDDIT_PASSWORD=your_password  # Optional
   ```

## Usage

### Command Line Interface

```bash
# Search Twitter for #AI
python -m app.social_monitoring.cli twitter search "#AI" --limit 50 --output ai_tweets.json

# Get a user's timeline
python -m app.social_monitoring.cli twitter timeline elonmusk --limit 20 --output musk_tweets.json

# Search Reddit for Python posts
python -m app.social_monitoring.cli reddit search "Python" --subreddit learnpython --limit 50 --output python_posts.json

# Get posts from a subreddit
python -m app.social_monitoring.cli reddit subreddit Python --limit 25 --sort top --time week --output top_python.json
```

### Python API

```python
from app.social_monitoring import TwitterMonitor, RedditMonitor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Twitter monitor
twitter = TwitterMonitor({
    'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
})

# Search for tweets
tweets = twitter.search("#AI", limit=50)
for tweet in tweets:
    print(f"{tweet.author}: {tweet.content[:100]}...")

# Initialize Reddit monitor
reddit = RedditMonitor({
    'client_id': os.getenv('REDDIT_CLIENT_ID'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
    'user_agent': os.getenv('REDDIT_USER_AGENT')
})

# Get posts from a subreddit
posts = reddit.get_subreddit_posts("Python", limit=25, sort="top")
for post in posts:
    print(f"{post.author} - {post.metrics['score']} points")
    print(f"{post.content[:200]}...\n")
```

## Output Format

### JSON Output Example
```json
{
  "platform": "twitter",
  "post_id": "1234567890",
  "author": "example_user",
  "content": "This is an example tweet about #AI and #MachineLearning",
  "created_at": "2023-01-01T12:00:00Z",
  "url": "https://twitter.com/example_user/status/1234567890",
  "metrics": {
    "likes": 42,
    "retweets": 5,
    "replies": 3,
    "quotes": 1,
    "impressions": 1000
  },
  "sentiment": {
    "polarity": 0.8,
    "subjectivity": 0.6
  },
  "tags": ["AI", "Machine Learning"]
}
```

## Rate Limiting and Best Practices

- **Twitter API v2**: Rate limits depend on your access level (Essential, Elevated, etc.)
- **Reddit API**: 60 requests per minute for OAuth2
- **Best Practices**:
  - Use appropriate rate limiting in your code
  - Cache responses when possible
  - Respect platform-specific terms of service
  - Handle API errors gracefully

## License

This project is licensed under the terms of the Echoes AI License. See the main LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your improvements.
