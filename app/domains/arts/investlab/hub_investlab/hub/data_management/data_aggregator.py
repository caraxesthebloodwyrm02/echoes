"""
Data Aggregator - Unifies and processes data from all ecosystems
"""

import json
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import schedule
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

class DataAggregator:
    """Aggregates and processes data from all ecosystem fetchers"""
    
    def __init__(self):
        self.aggregated_data = {}
        self.processed_data = {}
        self.alerts = []
        
    def aggregate(self, ecosystem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data from all ecosystems"""
        logger.info("Aggregating data from all ecosystems...")
        
        # Store raw data
        self.aggregated_data = ecosystem_data
        
        # Process and enrich data
        processed_data = {
            'summary': self._create_summary(ecosystem_data),
            'health_status': self._check_health_status(ecosystem_data),
            'trending_topics': self._extract_trending_topics(ecosystem_data),
            'recent_articles': self._extract_recent_articles(ecosystem_data),
            'service_status': self._extract_service_status(ecosystem_data),
            'alerts': self._generate_alerts(ecosystem_data),
            'statistics': self._calculate_statistics(ecosystem_data),
            'timestamp': datetime.now().isoformat()
        }
        
        self.processed_data = processed_data
        return processed_data
    
    def _create_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a high-level summary of all data"""
        summary = {
            'total_services': 0,
            'healthy_services': 0,
            'total_articles': 0,
            'total_trending_topics': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        # Count Microsoft services
        if 'microsoft' in data and 'azure_status' in data['microsoft']:
            azure_status = data['microsoft']['azure_status']
            if 'services' in azure_status:
                summary['total_services'] += len(azure_status['services'])
                summary['healthy_services'] += sum(1 for s in azure_status['services'] 
                                                 if 'status' in s and 'green' in str(s['status']).lower())
        
        # Count Google services
        if 'google' in data and 'google_cloud_status' in data['google']:
            gcp_status = data['google']['google_cloud_status']
            if 'services' in gcp_status:
                summary['total_services'] += len(gcp_status['services'])
                summary['healthy_services'] += sum(1 for s in gcp_status['services'] 
                                                 if 'status' in s and 'available' in str(s['status']).lower())
        
        # Count articles
        article_counts = [
            data.get('microsoft', {}).get('microsoft_news', {}).get('total_articles', 0),
            data.get('google', {}).get('google_news', {}).get('total_articles', 0),
            data.get('x', {}).get('twitter_news', {}).get('total_articles', 0)
        ]
        summary['total_articles'] = sum(article_counts)
        
        # Count trending topics
        if 'x' in data and 'trending_topics' in data['x']:
            summary['total_trending_topics'] = data['x']['trending_topics'].get('total_trends', 0)
        
        return summary
    
    def _check_health_status(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Check the health status of each ecosystem"""
        health_status = {}
        
        # Microsoft health
        if 'microsoft' in data:
            azure_status = data['microsoft'].get('azure_status', {})
            if 'overall_status' in azure_status:
                health_status['microsoft'] = azure_status['overall_status']
            else:
                health_status['microsoft'] = 'unknown'
        
        # Google health
        if 'google' in data:
            gcp_status = data['google'].get('google_cloud_status', {})
            if 'overall_status' in gcp_status:
                health_status['google'] = gcp_status['overall_status']
            else:
                health_status['google'] = 'unknown'
        
        # X/Twitter health
        if 'x' in data:
            twitter_status = data['x'].get('twitter_status', {})
            if 'platform_status' in twitter_status:
                health_status['x'] = twitter_status['platform_status']
            else:
                health_status['x'] = 'unknown'
        
        return health_status
    
    def _extract_trending_topics(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract trending topics from all ecosystems"""
        trending_topics = []
        
        # From X/Twitter
        if 'x' in data and 'trending_topics' in data['x']:
            topics = data['x']['trending_topics'].get('trending_topics', [])
            for topic in topics[:10]:
                trending_topics.append({
                    'topic': topic.get('hashtag', topic.get('topic', 'Unknown')),
                    'source': 'x',
                    'rank': topic.get('rank', 0),
                    'timestamp': datetime.now().isoformat()
                })
        
        return trending_topics
    
    def _extract_recent_articles(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract recent articles from all ecosystems"""
        articles = []
        
        # Microsoft articles
        if 'microsoft' in data and 'microsoft_news' in data['microsoft']:
            ms_articles = data['microsoft']['microsoft_news'].get('latest_articles', [])
            for article in ms_articles[:5]:
                articles.append({
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'source': 'microsoft',
                    'published': article.get('published', datetime.now().isoformat()),
                    'summary': article.get('summary', '')
                })
        
        # Google articles
        if 'google' in data and 'google_news' in data['google']:
            google_articles = data['google']['google_news'].get('google_blog_articles', [])
            for article in google_articles[:5]:
                articles.append({
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'source': 'google',
                    'published': article.get('published', datetime.now().isoformat()),
                    'summary': article.get('summary', '')
                })
        
        # X/Twitter articles
        if 'x' in data and 'twitter_news' in data['x']:
            twitter_articles = data['x']['twitter_news'].get('twitter_blog_articles', [])
            for article in twitter_articles[:5]:
                articles.append({
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'source': 'x',
                    'published': article.get('published', datetime.now().isoformat()),
                    'summary': article.get('summary', '')
                })
        
        # Sort by published date (newest first)
        articles.sort(key=lambda x: x['published'], reverse=True)
        return articles[:15]  # Return top 15 recent articles
    
    def _extract_service_status(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract service status information"""
        service_status = {
            'microsoft': [],
            'google': [],
            'x': []
        }
        
        # Microsoft services
        if 'microsoft' in data and 'azure_status' in data['microsoft']:
            services = data['microsoft']['azure_status'].get('services', [])
            for service in services[:10]:
                service_status['microsoft'].append({
                    'name': service.get('name', 'Unknown'),
                    'status': service.get('status', 'unknown'),
                    'last_updated': service.get('last_updated', datetime.now().isoformat())
                })
        
        # Google services
        if 'google' in data and 'google_cloud_status' in data['google']:
            services = data['google']['google_cloud_status'].get('services', [])
            for service in services[:10]:
                service_status['google'].append({
                    'name': service.get('name', 'Unknown'),
                    'status': service.get('status', 'unknown'),
                    'last_updated': service.get('last_updated', datetime.now().isoformat())
                })
        
        # X/Twitter status
        if 'x' in data and 'twitter_status' in data['x']:
            status = data['x']['twitter_status']
            service_status['x'].append({
                'name': 'Twitter Platform',
                'status': status.get('platform_status', 'unknown'),
                'last_updated': status.get('last_updated', datetime.now().isoformat())
            })
        
        return service_status
    
    def _generate_alerts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on data anomalies or issues"""
        alerts = []
        
        # Check for service outages
        health_status = self._check_health_status(data)
        for ecosystem, status in health_status.items():
            if status not in ['healthy', 'operational', 'available']:
                alerts.append({
                    'type': 'service_outage',
                    'ecosystem': ecosystem,
                    'message': f"{ecosystem.title()} ecosystem showing issues",
                    'severity': 'high',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check for error responses
        for ecosystem, eco_data in data.items():
            if isinstance(eco_data, dict):
                for key, value in eco_data.items():
                    if isinstance(value, dict) and 'error' in value:
                        alerts.append({
                            'type': 'fetch_error',
                            'ecosystem': ecosystem,
                            'service': key,
                            'message': value['error'],
                            'severity': 'medium',
                            'timestamp': datetime.now().isoformat()
                        })
        
        return alerts
    
    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various statistics from the data"""
        stats = {
            'total_api_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'data_freshness': {},
            'response_times': {}
        }
        
        # Count successful vs failed calls
        for ecosystem, eco_data in data.items():
            if isinstance(eco_data, dict):
                stats['total_api_calls'] += 1
                has_errors = any(isinstance(v, dict) and 'error' in v for v in eco_data.values())
                if has_errors:
                    stats['failed_calls'] += 1
                else:
                    stats['successful_calls'] += 1
        
        # Calculate success rate
        if stats['total_api_calls'] > 0:
            stats['success_rate'] = (stats['successful_calls'] / stats['total_api_calls']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of the processed data"""
        return {
            'last_aggregation': self.processed_data.get('timestamp', 'Never'),
            'total_services': self.processed_data.get('summary', {}).get('total_services', 0),
            'healthy_services': self.processed_data.get('summary', {}).get('healthy_services', 0),
            'total_alerts': len(self.processed_data.get('alerts', [])),
            'data_quality': 'good' if self.processed_data.get('statistics', {}).get('success_rate', 0) > 80 else 'poor'
        }
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export aggregated data to CSV"""
        if not filename:
            filename = f"aggregated_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            # Convert to DataFrame and save
            df = pd.json_normalize(self.processed_data)
            df.to_csv(filename, index=False)
            logger.info(f"Data exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return None
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get a summary of current alerts"""
        alerts = self.processed_data.get('alerts', [])
        
        return {
            'total_alerts': len(alerts),
            'high_severity': len([a for a in alerts if a.get('severity') == 'high']),
            'medium_severity': len([a for a in alerts if a.get('severity') == 'medium']),
            'low_severity': len([a for a in alerts if a.get('severity') == 'low']),
            'latest_alerts': alerts[:5]  # Latest 5 alerts
        }
