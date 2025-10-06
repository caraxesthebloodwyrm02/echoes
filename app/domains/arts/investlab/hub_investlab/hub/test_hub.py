#!/usr/bin/env python3
"""
Test script for the Data Hub
"""

import sys
import os
import asyncio
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_hub import DataHub

async def test_hub():
    """Test the data hub functionality"""
    print("🧪 Testing Data Hub...")
    
    hub = DataHub()
    
    try:
        # Test data fetching
        print("📊 Fetching data from all ecosystems...")
        data = await hub.fetch_all_ecosystems()
        
        # Print summary
        summary = hub.aggregator.get_data_summary()
        print(f"✅ Data fetch completed!")
        print(f"   Total services: {summary.get('total_services', 0)}")
        print(f"   Healthy services: {summary.get('healthy_services', 0)}")
        print(f"   Total articles: {summary.get('total_articles', 0)}")
        print(f"   Total alerts: {summary.get('total_alerts', 0)}")
        
        # Save test results
        with open('test_results.json', 'w') as f:
            json.dump({
                'test_timestamp': summary.get('last_aggregation'),
                'summary': summary,
                'system_status': hub.get_system_status()
            }, f, indent=2)
        
        print("\n📄 Test results saved to test_results.json")
        print("🎉 Data Hub is working correctly!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_hub())
