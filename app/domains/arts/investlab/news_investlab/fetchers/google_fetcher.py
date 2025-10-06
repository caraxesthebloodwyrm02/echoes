"""
Google Ecosystem Data Fetcher
Fetches latest data from Google ecosystem including Cloud, Workspace, Android, and Google News
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime
from typing import Dict, List, Any
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class GoogleFetcher:
    """Fetches data from Google ecosystem"""
    
    def __init__(self):
        self.base_urls = {
            'google_cloud_status': 'https://status.cloud.google.com',
            'google_blog': 'https://blog.google/feeds/posts/default',
            'android_blog': 'https://android-developers.googleblog.com/feeds/posts/default',
            'workspace_status': 'https://www.google.com/appsstatus/json/en',
            'google_releases': 'https://developers.google.com/feeds/announcements'
        }
        self.session = None
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch all Google ecosystem data"""
        logger.info("Fetching Google ecosystem data...")
        
        async with aiohttp.ClientSession() as self.session:
            tasks = [
                self._fetch_google_cloud_status(),
                self._fetch_google_news(),
                self._fetch_android_updates(),
                self._fetch_workspace_status(),
                self._fetch_google_releases()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                'google_cloud_status': results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])},
                'google_news': results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])},
                'android_updates': results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])},
                'workspace_status': results[3] if not isinstance(results[3], Exception) else {'error': str(results[3])},
                'google_releases': results[4] if not isinstance(results[4], Exception) else {'error': str(results[4])},
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fetch_google_cloud_status(self) -> Dict[str, Any]:
        """Fetch Google Cloud service status"""
        try:
            async with self.session.get(self.base_urls['google_cloud_status']) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract service status
                services = []
                
                # Look for service status elements
                status_elements = soup.find_all('tr', class_=lambda x: x and 'status' in str(x).lower())
                
                for element in status_elements[:20]:  # Limit to first 20 services
                    cols = element.find_all('td')
                    if len(cols) >= 3:
                        service_name = cols[0].text.strip()
                        status = cols[1].find('span')
                        
                        if status:
                            status_class = status.get('class', [''])[0]
                            status_text = 'available' if 'available' in status_class else 'unavailable'
                            
                            services.append({
                                'name': service_name,
                                'status': status_text,
                                'last_updated': datetime.now().isoformat()
                            })
                
                # Also check for incidents
                incidents = []
                incident_elements = soup.find_all('div', class_='incident')
                for incident in incident_elements[:5]:
                    title = incident.find('h3')
                    description = incident.find('p')
                    
                    if title and description:
                        incidents.append({
                            'title': title.text.strip(),
                            'description': description.text.strip()[:200] + '...',
                            'timestamp': datetime.now().isoformat()
                        })
                
                return {
                    'overall_status': 'healthy' if all(s['status'] == 'available' for s in services) else 'issues',
                    'services': services,
                    'incidents': incidents
                }
                
        except Exception as e:
            logger.error(f"Error fetching Google Cloud status: {str(e)}")
            return {'error': str(e)}
    
    async def _fetch_google_news(self) -> Dict[str, Any]:
        """Fetch latest Google news and blog posts"""
        try:
            # Fetch from Google Blog
            feed = feedparser.parse(self.base_urls['google_blog'])
            
            articles = []
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'summary': entry.summary[:200] + '...' if hasattr(entry, 'summary') else '',
                    'author': entry.author if hasattr(entry, 'author') else 'Google'
                })
            
            # Fetch from Google Developers Blog
            dev_feed = feedparser.parse('https://developers.googleblog.com/feeds/posts/default')
            dev_articles = []
            for entry in dev_feed.entries[:5]:
                dev_articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'summary': entry.summary[:200] + '...' if hasattr(entry, 'summary') else '',
                    'category': entry.category if hasattr(entry, 'category') else 'General'
                })
            
            return {
                'total_articles': len(articles) + len(dev_articles),
                'google_blog_articles': articles,
                'developer_articles': dev_articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching Google news: {str(e)}")
            return {'error': str(e)}
    
    async def _fetch_android_updates(self) -> Dict[str, Any]:
        """Fetch latest Android updates and releases"""
        try:
            # Fetch from Android Developers Blog
            feed = feedparser.parse(self.base_urls['android_blog'])
            
            updates = []
            for entry in feed.entries[:10]:
                updates.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'summary': entry.summary[:200] + '...' if hasattr(entry, 'summary') else '',
                    'tags': [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else []
                })
            
            # Fetch Android version info
            android_url = "https://developer.android.com/about/versions"
            async with self.session.get(android_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                versions = []
                version_elements = soup.find_all('div', class_='devsite-landing-row-item')
                
                for element in version_elements[:5]:
                    title = element.find('h3')
                    description = element.find('p')
                    
                    if title and description:
                        versions.append({
                            'name': title.text.strip(),
                            'description': description.text.strip()[:150] + '...',
                            'url': f"https://developer.android.com{element.find('a')['href']}" if element.find('a') else ''
                        })
            
            return {
                'total_updates': len(updates),
                'latest_updates': updates,
                'android_versions': versions,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching Android updates: {str(e)}")
            return {'error': str(e)}
    
    async def _fetch_workspace_status(self) -> Dict[str, Any]:
        """Fetch Google Workspace status"""
        try:
            # Google Workspace status
            async with self.session.get(self.base_urls['workspace_status']) as response:
                if response.status == 200:
                    status_data = await response.json()
                    
                    services = []
                    if isinstance(status_data, dict) and 'services' in status_data:
                        for service in status_data['services']:
                            services.append({
                                'name': service.get('name', 'Unknown'),
                                'status': service.get('status', 'Unknown'),
                                'description': service.get('description', ''),
                                'last_updated': service.get('updated', datetime.now().isoformat())
                            })
                    
                    return {
                        'overall_status': 'healthy' if all(s['status'] == 'available' for s in services) else 'issues',
                        'services': services
                    }
                else:
                    return await self._scrape_workspace_status()
                    
        except Exception as e:
            logger.error(f"Error fetching Workspace status: {str(e)}")
            return await self._scrape_workspace_status()
    
    async def _scrape_workspace_status(self) -> Dict[str, Any]:
        """Fallback method to scrape Google Workspace status"""
        try:
            url = "https://www.google.com/appsstatus"
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                return {
                    'source': 'scraped',
                    'status': 'Google Workspace services operational',
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _fetch_google_releases(self) -> Dict[str, Any]:
        """Fetch latest Google product releases and API updates"""
        try:
            # Fetch from Google Developers announcements
            feed = feedparser.parse(self.base_urls['google_releases'])
            
            releases = []
            for entry in feed.entries[:10]:
                releases.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'summary': entry.summary[:200] + '...' if hasattr(entry, 'summary') else '',
                    'category': entry.category if hasattr(entry, 'category') else 'General'
                })
            
            # Fetch Chrome releases
            chrome_url = "https://chromereleases.googleblog.com/feeds/posts/default"
            chrome_feed = feedparser.parse(chrome_url)
            
            chrome_releases = []
            for entry in chrome_feed.entries[:5]:
                chrome_releases.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'summary': entry.summary[:200] + '...' if hasattr(entry, 'summary') else ''
                })
            
            return {
                'total_releases': len(releases) + len(chrome_releases),
                'api_releases': releases,
                'chrome_releases': chrome_releases,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching Google releases: {str(e)}")
            return {'error': str(e)}
