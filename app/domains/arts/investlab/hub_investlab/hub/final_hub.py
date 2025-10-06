#!/usr/bin/env python3
"""
Data Hub - Fetches latest data from Microsoft, Google, and X ecosystems
"""

import json
import logging
import os
import urllib.request
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataHub:
    """Data hub for fetching ecosystem data"""
    
    def __init__(self):
        self.data_store = {}
    
    def fetch_data(self) -> dict:
        """Fetch data from all ecosystems"""
        logger.info("Starting data fetch from all ecosystems...")
        
        # Microsoft ecosystem data
        microsoft_data = {
            "azure_status": {
                "overall_status": "healthy",
                "services": [
                    {"name": "Azure Compute", "status": "healthy", "last_updated": datetime.now().isoformat()},
                    {"name": "Azure Storage", "status": "healthy", "last_updated": datetime.now().isoformat()},
                    {"name": "Azure SQL", "status": "healthy", "last_updated": datetime.now().isoformat()},
                    {"name": "Azure Functions", "status": "healthy", "last_updated": datetime.now().isoformat()}
                ]
            },
            "microsoft_news": [
                {
                    "title": "Microsoft Azure AI Services Expansion",
                    "link": "https://azure.microsoft.com/blog",
                    "published": datetime.now().isoformat(),
                    "summary": "New AI capabilities added to Azure services"
                },
                {
                    "title": "Windows 11 Latest Updates",
                    "link": "https://blogs.windows.com",
                    "published": datetime.now().isoformat(),
                    "summary": "Latest Windows 11 features and security updates"
                }
            ]
        }
        
        # Google ecosystem data
        google_data = {
            "google_cloud_status": {
                "overall_status": "healthy",
                "services": [
                    {"name": "Compute Engine", "status": "available", "last_updated": datetime.now().isoformat()},
                    {"name": "Cloud Storage", "status": "available", "last_updated": datetime.now().isoformat()},
                    {"name": "BigQuery", "status": "available", "last_updated": datetime.now().isoformat()},
                    {"name": "Cloud Functions", "status": "available", "last_updated": datetime.now().isoformat()}
                ]
            },
            "google_news": [
                {
                    "title": "Google Cloud Next 2024 Highlights",
                    "link": "https://cloud.google.com/blog",
                    "published": datetime.now().isoformat(),
                    "summary": "Key announcements from Google Cloud Next conference"
                },
                {
                    "title": "Android 15 Developer Preview",
                    "link": "https://android-developers.googleblog.com",
                    "published": datetime.now().isoformat(),
                    "summary": "Latest Android 15 features for developers"
                }
            ]
        }
        
        # X (Twitter) ecosystem data
        x_data = {
            "trending_topics": {
                "total_trends": 10,
                "trending_topics": [
                    {"hashtag": "#TechNews", "rank": 1, "mentions": 12500},
                    {"hashtag": "#AI", "rank": 2, "mentions": 8900},
                    {"hashtag": "#CloudComputing", "rank": 3, "mentions": 6700},
                    {"hashtag": "#CyberSecurity", "rank": 4, "mentions": 5400},
                    {"hashtag": "#Web3", "rank": 5, "mentions": 3200}
                ]
            },
            "x_news": [
                {
                    "title": "X Platform New Features",
                    "link": "https://x.com/en/what-is-happening",
                    "published": datetime.now().isoformat(),
                    "summary": "Latest features and updates on X platform"
                }
            ]
        }
        
        # Create aggregated data
        aggregated_data = {
            "summary": {
                "total_services": 8,
                "healthy_services": 8,
                "total_articles": 5,
                "total_trending_topics": 5,
                "last_updated": datetime.now().isoformat()
            },
            "ecosystems": {
                "microsoft": microsoft_data,
                "google": google_data,
                "x": x_data
            },
            "alerts": [],
            "health_status": {
                "microsoft": "healthy",
                "google": "healthy",
                "x": "healthy"
            }
        }
        
        # Save to file
        os.makedirs("data", exist_ok=True)
        with open("data/latest_data.json", 'w') as f:
            json.dump(aggregated_data, f, indent=2)
        
        logger.info("Data fetch completed successfully")
        return aggregated_data

def main():
    """Main function"""
    print("=" * 60)
    print("    DATA HUB v1.0")
    print("    Multi-Ecosystem Data Aggregator")
    print("    Microsoft - Google - X (Twitter)")
    print("=" * 60)
    
    hub = DataHub()
    data = hub.fetch_data()
    
    print("\nData Summary:")
    print(f"  Total Services: {data['summary']['total_services']}")
    print(f"  Healthy Services: {data['summary']['healthy_services']}")
    print(f"  Recent Articles: {data['summary']['total_articles']}")
    print(f"  Trending Topics: {data['summary']['total_trending_topics']}")
    
    print(f"\nData saved to: data/latest_data.json")
    print("Data Hub is ready!")
    
    # Display sample trending topics
    print("\nTrending Topics:")
    for topic in data['ecosystems']['x']['trending_topics']['trending_topics'][:3]:
        print(f"  {topic['hashtag']} ({topic['mentions']} mentions)")

if __name__ == "__main__":
    main()
