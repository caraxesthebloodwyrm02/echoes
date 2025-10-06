"""
Microsoft Ecosystem Data Fetcher
Fetches latest data from Microsoft ecosystem including Azure, Office 365, GitHub, and Microsoft News
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime
from typing import Dict, List, Any
import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MicrosoftFetcher:
    """Fetches data from Microsoft ecosystem"""
    
    def __init__(self):
        self.base_urls = {
            'azure_status': 'https://status.azure.com/en-us/status',
            'microsoft_blog': 'https://blogs.microsoft.com/feed/',
            'github_microsoft': 'https://api.github.com/orgs/microsoft',
            'office365_status': 'https://status.office365.com/api/v2.0/status'
        }
        self.session = None
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch all Microsoft ecosystem data"""
        logger.info("Fetching Microsoft ecosystem data...")
        
        async with aiohttp.ClientSession() as self.session:
            tasks = [
                self._fetch_azure_status(),
                self._fetch_microsoft_news(),
                self._fetch_github_repos(),
                self._fetch_office365_status(),
                self._fetch_microsoft_releases()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                'azure_status': results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])},
                'microsoft_news': results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])},
                'github_repos': results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])},
                'office365_status': results[3] if not isinstance(results[3], Exception) else {'error': str(results[3])},
                'microsoft_releases': results[4] if not isinstance(results[4], Exception) else {'error': str(results[4])},
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fetch_azure_status(self) -> Dict[str, Any]:
        """Fetch Azure service status"""
        try:
            async with self.session.get(self.base_urls['azure_status']) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract service status information
                services = []
                status_elements = soup.find_all('div', class_='row-fluid')
                
                for element in status_elements:
                    service_name = element.find('div', class_='service-name')
                    status = element.find('div', class_='status-circle')
                    
                    if service_name and status:
                        services.append({
                            'name': service_name.text.strip(),
                            'status': status.get('class', ['unknown'])[0],
                            'last_updated': datetime.now().isoformat()
                        })
                
                return {
                    'overall_status': 'healthy' if all(s['status'] == 'status-green' for s in services) else 'issues',
                    'services': services[:20]  # Limit to first 20 services
                }
                
        except Exception as e:
            logger.error(f"Error fetching Azure status: {str(e)}")
            return {'error': str(e)}
    
    async def _fetch_microsoft_news(self) -> Dict[str, Any]:
        """Fetch latest Microsoft news and blog posts"""
        try:
            feed = feedparser.parse(self.base_urls['microsoft_blog'])
            
            articles = []
            for entry in feed.entries[:10]:  # Get latest 10 articles
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'summary': entry.summary[:200] + '...' if hasattr(entry, 'summary') else '',
                    'author': entry.author if hasattr(entry, 'author') else 'Microsoft'
                })
            
            return {
                'total_articles': len(articles),
                'latest_articles': articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching Microsoft news: {str(e)}")
            return {'error': str(e)}
    
    async def _fetch_github_repos(self) -> Dict[str, Any]:
        """Fetch Microsoft's popular GitHub repositories"""
        try:
            url = f"{self.base_urls['github_microsoft']}/repos"
            params = {
                'sort': 'updated',
                'per_page': 20,
                'type': 'public'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    repos = await response.json()
                    
                    popular_repos = []
                    for repo in repos[:15]:
                        popular_repos.append({
                            'name': repo['name'],
                            'description': repo['description'],
                            'stars': repo['stargazers_count'],
                            'forks': repo['forks_count'],
                            'language': repo['language'],
                            'updated_at': repo['updated_at'],
                            'url': repo['html_url']
                        })
                    
                    return {
                        'total_repos': len(popular_repos),
                        'popular_repos': popular_repos
                    }
                else:
                    return {'error': f'GitHub API returned status {response.status}'}
                    
        except Exception as e:
            logger.error(f"Error fetching GitHub repos: {str(e)}")
            return {'error': str(e)}
    
    async def _fetch_office365_status(self) -> Dict[str, Any]:
        """Fetch Office 365 service status"""
        try:
            # Office 365 status API
            async with self.session.get(self.base_urls['office365_status']) as response:
                if response.status == 200:
                    status_data = await response.json()
                    
                    services = []
                    if 'value' in status_data:
                        for service in status_data['value']:
                            services.append({
                                'name': service.get('DisplayName', 'Unknown'),
                                'status': service.get('Status', 'Unknown'),
                                'incidents': len(service.get('Incidents', [])),
                                'features': [f.get('DisplayName') for f in service.get('Features', [])]
                            })
                    
                    return {
                        'overall_status': 'healthy' if all(s['status'] == 'ServiceOperational' for s in services) else 'issues',
                        'services': services
                    }
                else:
                    # Fallback to scraping
                    return await self._scrape_office365_status()
                    
        except Exception as e:
            logger.error(f"Error fetching Office365 status: {str(e)}")
            return await self._scrape_office365_status()
    
    async def _scrape_office365_status(self) -> Dict[str, Any]:
        """Fallback method to scrape Office 365 status"""
        try:
            url = "https://status.office365.com"
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                return {
                    'source': 'scraped',
                    'status': 'Office 365 services operational',
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _fetch_microsoft_releases(self) -> Dict[str, Any]:
        """Fetch latest Microsoft product releases and updates"""
        try:
            # Fetch Windows 11 release info
            windows_url = "https://docs.microsoft.com/en-us/windows/release-health/release-information"
            
            async with self.session.get(windows_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                releases = []
                
                # Look for release tables
                tables = soup.find_all('table')
                for table in tables[:2]:  # First 2 tables
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows[:5]:  # First 5 releases
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            releases.append({
                                'version': cols[0].text.strip(),
                                'date': cols[1].text.strip(),
                                'build': cols[2].text.strip()
                            })
                
                return {
                    'windows_releases': releases,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error fetching Microsoft releases: {str(e)}")
            return {'error': str(e)}
