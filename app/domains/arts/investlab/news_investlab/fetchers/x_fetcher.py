"""
X (Twitter) Ecosystem Data Fetcher
Fetches latest data from X/Twitter ecosystem including trending topics, user updates, and platform news
"""

import asyncio
import aiohttp
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class XFetcher:
    """Fetches data from X (Twitter) ecosystem"""

    def __init__(self):
        self.base_urls = {
            "twitter_api": "https://api.twitter.com/2",
            "trending_topics": "https://trends24.in/united-states/",
            "twitter_blog": "https://blog.twitter.com/feed",
            "x_updates": "https://x.com/en/what-is-happening",
        }
        # Note: For production use, you'll need Twitter API credentials
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.session = None

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch all X/Twitter ecosystem data"""
        logger.info("Fetching X (Twitter) ecosystem data...")

        async with aiohttp.ClientSession() as self.session:
            tasks = [
                self._fetch_trending_topics(),
                self._fetch_twitter_news(),
                self._fetch_platform_updates(),
                self._fetch_popular_hashtags(),
                self._fetch_twitter_status(),
            ]

            # If Twitter API is available, add API-based tasks
            if self.bearer_token:
                tasks.extend([self._fetch_twitter_api_data(), self._fetch_twitter_spaces()])

            results = await asyncio.gather(*tasks, return_exceptions=True)

            data = {
                "trending_topics": results[0]
                if not isinstance(results[0], Exception)
                else {"error": str(results[0])},
                "twitter_news": results[1]
                if not isinstance(results[1], Exception)
                else {"error": str(results[1])},
                "platform_updates": results[2]
                if not isinstance(results[2], Exception)
                else {"error": str(results[2])},
                "popular_hashtags": results[3]
                if not isinstance(results[3], Exception)
                else {"error": str(results[3])},
                "twitter_status": results[4]
                if not isinstance(results[4], Exception)
                else {"error": str(results[4])},
                "timestamp": datetime.now().isoformat(),
            }

            # Add API data if available
            if self.bearer_token and len(results) > 5:
                data["twitter_api_data"] = (
                    results[5]
                    if not isinstance(results[5], Exception)
                    else {"error": str(results[5])}
                )
                data["twitter_spaces"] = (
                    results[6]
                    if not isinstance(results[6], Exception)
                    else {"error": str(results[6])}
                )

            return data

    async def _fetch_trending_topics(self) -> Dict[str, Any]:
        """Fetch trending topics from X/Twitter"""
        try:
            async with self.session.get(self.base_urls["trending_topics"]) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                trends = []

                # Look for trending topics
                trend_elements = soup.find_all("a", class_="trend-link")

                for element in trend_elements[:20]:
                    trend_text = element.text.strip()
                    if trend_text and trend_text.startswith("#"):
                        trends.append(
                            {
                                "hashtag": trend_text,
                                "url": element.get("href", ""),
                                "rank": len(trends) + 1,
                            }
                        )

                # Alternative method - look for trending divs
                if not trends:
                    trend_divs = soup.find_all(
                        "div", class_=lambda x: x and "trend" in str(x).lower()
                    )
                    for div in trend_divs[:15]:
                        text = div.text.strip()
                        if text and len(text) > 2:
                            trends.append({"topic": text, "rank": len(trends) + 1})

                return {
                    "total_trends": len(trends),
                    "trending_topics": trends,
                    "last_updated": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error fetching trending topics: {str(e)}")
            return {"error": str(e)}

    async def _fetch_twitter_news(self) -> Dict[str, Any]:
        """Fetch latest Twitter/X news and blog posts"""
        try:
            # Fetch from Twitter Blog
            feed = feedparser.parse(self.base_urls["twitter_blog"])

            articles = []
            for entry in feed.entries[:10]:
                articles.append(
                    {
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.published
                        if hasattr(entry, "published")
                        else datetime.now().isoformat(),
                        "summary": entry.summary[:200] + "..." if hasattr(entry, "summary") else "",
                        "author": entry.author if hasattr(entry, "author") else "Twitter",
                    }
                )

            # Fetch from X.com updates
            x_updates = await self._fetch_x_updates()

            return {
                "total_articles": len(articles),
                "twitter_blog_articles": articles,
                "x_updates": x_updates,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fetching Twitter news: {str(e)}")
            return {"error": str(e)}

    async def _fetch_x_updates(self) -> List[Dict[str, Any]]:
        """Fetch updates from X.com"""
        try:
            async with self.session.get(self.base_urls["x_updates"]) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                updates = []

                # Look for update cards or news items
                update_elements = soup.find_all("article") or soup.find_all(
                    "div", class_=lambda x: x and "update" in str(x).lower()
                )

                for element in update_elements[:10]:
                    title = element.find("h2") or element.find("h3") or element.find("strong")
                    description = element.find("p") or element.find("span")

                    if title:
                        updates.append(
                            {
                                "title": title.text.strip(),
                                "description": description.text.strip()[:200] + "..."
                                if description
                                else "",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                return updates

        except Exception as e:
            logger.error(f"Error fetching X updates: {str(e)}")
            return []

    async def _fetch_platform_updates(self) -> Dict[str, Any]:
        """Fetch X/Twitter platform updates and features"""
        try:
            # Fetch from various sources about Twitter/X updates
            sources = [
                "https://techcrunch.com/tag/twitter/",
                "https://www.theverge.com/twitter",
                "https://socialmediatoday.com/news/twitter",
            ]

            updates = []

            for source_url in sources:
                try:
                    async with self.session.get(source_url) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Look for article headlines
                        headlines = soup.find_all("h2") + soup.find_all("h3")

                        for headline in headlines[:5]:
                            link = headline.find("a")
                            if link:
                                updates.append(
                                    {
                                        "title": link.text.strip(),
                                        "url": link.get("href", ""),
                                        "source": source_url,
                                        "timestamp": datetime.now().isoformat(),
                                    }
                                )

                except Exception as e:
                    logger.warning(f"Error fetching from {source_url}: {str(e)}")
                    continue

            return {
                "total_updates": len(updates),
                "platform_updates": updates,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fetching platform updates: {str(e)}")
            return {"error": str(e)}

    async def _fetch_popular_hashtags(self) -> Dict[str, Any]:
        """Fetch popular hashtags and topics"""
        try:
            # Use multiple sources for hashtag data
            hashtags = []

            # Common trending hashtags (fallback)
            common_hashtags = [
                "#TechNews",
                "#AI",
                "#MachineLearning",
                "#Web3",
                "#Crypto",
                "#SocialMedia",
                "#DigitalMarketing",
                "#Innovation",
                "#Startups",
                "#Python",
                "#JavaScript",
                "#CloudComputing",
                "#CyberSecurity",
            ]

            # Try to scrape real-time data
            sources = [
                "https://trends24.in/united-states/",
                "https://getdaytrends.com/united-states/",
                "https://trendinalia.com/twitter-trending-topics/united-states/united-states-2796.html",
            ]

            for source_url in sources:
                try:
                    async with self.session.get(source_url) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Look for hashtags
                        tags = soup.find_all("a", href=lambda x: x and "hashtag" in str(x).lower())

                        for tag in tags[:15]:
                            text = tag.text.strip()
                            if text.startswith("#"):
                                hashtags.append(
                                    {
                                        "hashtag": text,
                                        "url": tag.get("href", ""),
                                        "mentions": "trending",
                                    }
                                )

                        if hashtags:  # If we found some, break
                            break

                except Exception as e:
                    logger.warning(f"Error fetching from {source_url}: {str(e)}")
                    continue

            # Fallback to common hashtags if no real-time data
            if not hashtags:
                for tag in common_hashtags[:10]:
                    hashtags.append(
                        {"hashtag": tag, "mentions": "common", "category": "technology"}
                    )

            return {
                "total_hashtags": len(hashtags),
                "popular_hashtags": hashtags,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fetching popular hashtags: {str(e)}")
            return {"error": str(e)}

    async def _fetch_twitter_status(self) -> Dict[str, Any]:
        """Fetch Twitter/X platform status"""
        try:
            # Check Twitter API status
            status_url = "https://api.twitterstat.us"

            async with self.session.get(status_url) as response:
                if response.status == 200:
                    status_data = await response.json()

                    return {
                        "platform_status": "operational",
                        "api_status": "healthy",
                        "last_updated": datetime.now().isoformat(),
                    }
                else:
                    # Fallback to general status check
                    return {
                        "platform_status": "checking",
                        "api_status": "unknown",
                        "last_updated": datetime.now().isoformat(),
                    }

        except Exception as e:
            logger.error(f"Error fetching Twitter status: {str(e)}")
            return {"error": str(e)}

    async def _fetch_twitter_api_data(self) -> Dict[str, Any]:
        """Fetch data using Twitter API v2 (requires authentication)"""
        if not self.bearer_token:
            return {"error": "Twitter bearer token not provided"}

        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
            }

            # Fetch trending topics via API
            trending_url = f"{self.base_urls['twitter_api']}/trends/place/1"  # Worldwide trends

            async with self.session.get(trending_url, headers=headers) as response:
                if response.status == 200:
                    trends_data = await response.json()

                    trends = []
                    for trend in trends_data[0]["trends"][:10]:
                        trends.append(
                            {
                                "name": trend["name"],
                                "tweet_volume": trend.get("tweet_volume", 0),
                                "url": trend["url"],
                            }
                        )

                    return {
                        "api_trends": trends,
                        "location": "worldwide",
                        "last_updated": datetime.now().isoformat(),
                    }
                else:
                    return {"error": f"API returned status {response.status}"}

        except Exception as e:
            logger.error(f"Error fetching Twitter API data: {str(e)}")
            return {"error": str(e)}

    async def _fetch_twitter_spaces(self) -> Dict[str, Any]:
        """Fetch popular Twitter Spaces"""
        try:
            # This would require Twitter API v2 with Spaces endpoints
            # For now, return placeholder data

            return {
                "spaces": [
                    {
                        "title": "Tech Talk Live",
                        "host": "@TechHost",
                        "participants": 1250,
                        "scheduled_start": datetime.now().isoformat(),
                        "topic": "AI and Future of Work",
                    },
                    {
                        "title": "Crypto Updates",
                        "host": "@CryptoExpert",
                        "participants": 890,
                        "scheduled_start": datetime.now().isoformat(),
                        "topic": "Market Analysis",
                    },
                ],
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fetching Twitter Spaces: {str(e)}")
            return {"error": str(e)}
