#!/usr/bin/env python3
"""
Data Hub - Central aggregator for Microsoft, Google, and X ecosystem data
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from dotenv import load_dotenv

# Import our ecosystem fetchers
from fetchers.microsoft_fetcher import MicrosoftFetcher
from fetchers.google_fetcher import GoogleFetcher
from fetchers.x_fetcher import XFetcher
from aggregator.data_aggregator import DataAggregator
from web.dashboard import create_dashboard

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_hub.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataHub:
    """Main Data Hub class that orchestrates data fetching from multiple ecosystems"""
    
    def __init__(self):
        self.microsoft_fetcher = MicrosoftFetcher()
        self.google_fetcher = GoogleFetcher()
        self.x_fetcher = XFetcher()
        self.aggregator = DataAggregator()
        self.data_store = {}
        
    async def fetch_all_ecosystems(self) -> Dict[str, Any]:
        """Fetch data from all ecosystems concurrently"""
        logger.info("Starting data fetch from all ecosystems...")
        
        tasks = [
            self.microsoft_fetcher.fetch_data(),
            self.google_fetcher.fetch_data(),
            self.x_fetcher.fetch_data()
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            ecosystem_data = {
                'microsoft': results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])},
                'google': results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])},
                'x': results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])}
            }
            
            # Store raw data
            self.data_store = ecosystem_data
            
            # Aggregate and process data
            aggregated_data = self.aggregator.aggregate(ecosystem_data)
            
            # Save to file
            self._save_data(aggregated_data)
            
            logger.info("Data fetch completed successfully")
            return aggregated_data
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise
    
    def _save_data(self, data: Dict[str, Any]):
        """Save aggregated data to JSON file"""
        timestamp = datetime.now().isoformat()
        filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        save_data = {
            'timestamp': timestamp,
            'data': data
        }
        
        with open(f"data/{filename}", 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        # Also save latest data
        with open("data/latest_data.json", 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get the latest aggregated data"""
        try:
            with open("data/latest_data.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'error': 'No data available'}
    
    def run_dashboard(self, port=5000):
        """Run the web dashboard"""
        create_dashboard(self, port)

async def main():
    """Main async function"""
    hub = DataHub()
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Fetch initial data
    await hub.fetch_all_ecosystems()
    
    # Run dashboard
    hub.run_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
