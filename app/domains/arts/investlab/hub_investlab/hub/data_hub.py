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
from dotenv import load_dotenv

# Import our ecosystem fetchers
from fetchers.microsoft_fetcher import MicrosoftFetcher
from fetchers.google_fetcher import GoogleFetcher
from fetchers.x_fetcher import XFetcher
from aggregator.data_aggregator import DataAggregator
from aggregator.scheduler import DataScheduler
from web.dashboard import create_dashboard
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("data_hub.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DataHub:
    """Main Data Hub class that orchestrates data fetching from multiple ecosystems"""

    def __init__(self):
        self.microsoft_fetcher = MicrosoftFetcher()
        self.google_fetcher = GoogleFetcher()
        self.x_fetcher = XFetcher()
        self.aggregator = DataAggregator()
        self.scheduler = DataScheduler(self)
        self.data_store = {}

    async def fetch_all_ecosystems(self) -> Dict[str, Any]:
        """Fetch data from all ecosystems concurrently"""
        logger.info("Starting data fetch from all ecosystems...")

        # Check which sources are enabled
        enabled_sources = []
        if Config.DATA_SOURCES["microsoft"]["enabled"]:
            enabled_sources.append(self.microsoft_fetcher.fetch_data())
        if Config.DATA_SOURCES["google"]["enabled"]:
            enabled_sources.append(self.google_fetcher.fetch_data())
        if Config.DATA_SOURCES["x"]["enabled"]:
            enabled_sources.append(self.x_fetcher.fetch_data())

        if not enabled_sources:
            logger.warning("No data sources enabled")
            return {"error": "No data sources enabled"}

        try:
            results = await asyncio.gather(*enabled_sources, return_exceptions=True)

            ecosystem_data = {}
            source_names = []

            if Config.DATA_SOURCES["microsoft"]["enabled"]:
                source_names.append("microsoft")
            if Config.DATA_SOURCES["google"]["enabled"]:
                source_names.append("google")
            if Config.DATA_SOURCES["x"]["enabled"]:
                source_names.append("x")

            for i, (source_name, result) in enumerate(zip(source_names, results)):
                ecosystem_data[source_name] = (
                    result if not isinstance(result, Exception) else {"error": str(result)}
                )

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

        save_data = {"timestamp": timestamp, "data": data}

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        with open(f"data/{filename}", "w") as f:
            json.dump(save_data, f, indent=2, default=str)

        # Also save latest data
        with open("data/latest_data.json", "w") as f:
            json.dump(save_data, f, indent=2, default=str)

    def get_latest_data(self) -> Dict[str, Any]:
        """Get the latest aggregated data"""
        try:
            with open("data/latest_data.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"error": "No data available"}

    def run_dashboard(self, port=None):
        """Run the web dashboard"""
        if port is None:
            port = Config.DASHBOARD_PORT
        create_dashboard(self, port)

    def start_scheduler(self):
        """Start the automated scheduler"""
        self.scheduler.schedule_custom_interval(Config.FETCH_INTERVAL_MINUTES)
        self.scheduler.start_scheduler()
        logger.info(f"Scheduler started with {Config.FETCH_INTERVAL_MINUTES} minute intervals")

    def stop_scheduler(self):
        """Stop the automated scheduler"""
        self.scheduler.stop_scheduler()
        logger.info("Scheduler stopped")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "scheduler_status": self.scheduler.get_scheduler_status(),
            "config_summary": Config.get_config_summary(),
            "data_summary": self.aggregator.get_data_summary(),
            "timestamp": datetime.now().isoformat(),
        }


def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    🚀 DATA HUB v1.0                          ║
    ║                                                               ║
    ║  Multi-Ecosystem Data Aggregator                            ║
    ║  Microsoft • Google • X (Twitter)                           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def main():
    """Main async function"""
    print_banner()

    # Validate configuration
    config_status = Config.validate_config()
    if not config_status["is_valid"]:
        logger.error("Configuration issues found:")
        for issue in config_status["issues"]:
            logger.error(f"  - {issue}")
        return

    if config_status["warnings"]:
        logger.warning("Configuration warnings:")
        for warning in config_status["warnings"]:
            logger.warning(f"  - {warning}")

    hub = DataHub()

    # Initial data fetch
    logger.info("Performing initial data fetch...")
    await hub.fetch_all_ecosystems()

    # Start scheduler
    hub.start_scheduler()

    # Run dashboard
    logger.info(f"Starting web dashboard on port {Config.DASHBOARD_PORT}...")
    hub.run_dashboard()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down Data Hub...")
        print("\n👋 Data Hub stopped. Thank you for using!")
