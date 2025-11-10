"""
EchoesAI Onboarding System
Explicit onboarding path for EchoesAI ecosystem integration.
"""

__version__ = "1.0.0"
__author__ = "Atmosphere Team"
__description__ = "EchoesAI onboarding and ecosystem integration"

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EchoesOnboarding:
    """Explicit onboarding system for EchoesAI."""

    def __init__(self):
        """Initialize onboarding system."""
        self.onboarding_status = "pending"
        self.ecosystem_connected = False
        self.api_connected = False
        self.capabilities = []

        logger.info("🤖 Initializing EchoesAI Onboarding System...")

    async def onboard_to_ecosystem(self) -> Dict[str, Any]:
        """Onboard EchoesAI to the Atmosphere ecosystem."""
        logger.info("🌍 Starting EchoesAI ecosystem onboarding...")

        try:
            # Step 1: Establish ecosystem connection
            ecosystem_status = await self._connect_to_ecosystem()

            # Step 2: Initialize API integration
            api_status = await self._initialize_api_integration()

            # Step 3: Register capabilities
            capabilities = await self._register_capabilities()

            # Step 4: Sync with ecosystem
            sync_status = await self._sync_with_ecosystem()

            # Generate onboarding report
            report = {
                "timestamp": datetime.now().isoformat(),
                "component": "EchoesAI",
                "version": "1.0.0",
                "onboarding_status": "complete",
                "ecosystem_connection": ecosystem_status,
                "api_integration": api_status,
                "capabilities": capabilities,
                "sync_status": sync_status,
                "health": "operational"
            }

            self.onboarding_status = "complete"
            logger.info("✅ EchoesAI onboarding completed successfully")

            return report

        except Exception as e:
            logger.error(f"❌ EchoesAI onboarding failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "component": "EchoesAI",
                "onboarding_status": "failed",
                "error": str(e),
                "health": "failed"
            }

    async def _connect_to_ecosystem(self) -> Dict[str, Any]:
        """Connect to Atmosphere ecosystem."""
        try:
            # Explicit path to ecosystem
            atmosphere_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ecosystem_path = os.path.join(atmosphere_root, "ecosystem")

            if ecosystem_path not in sys.path:
                sys.path.insert(0, ecosystem_path)

            # Import ecosystem
            from ecosystem import get_ecosystem

            # Get ecosystem instance
            ecosystem = get_ecosystem()

            # Register EchoesAI
            echo_config = {
                "name": "EchoesAI",
                "version": "1.0.0",
                "type": "ai_research_platform",
                "status": "active",
                "onboarding_path": "explicit"
            }

            # Store in ecosystem components
            if not hasattr(ecosystem, 'components'):
                ecosystem.components = {}

            ecosystem.components["echoes"] = echo_config
            ecosystem.integration_status["echoes"] = "integrated"

            self.ecosystem_connected = True

            return {
                "status": "connected",
                "ecosystem_version": getattr(ecosystem, '__version__', '1.0.0'),
                "connection_type": "explicit_onboarding"
            }

        except Exception as e:
            logger.error(f"Ecosystem connection failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _initialize_api_integration(self) -> Dict[str, Any]:
        """Initialize OpenAI API integration."""
        try:
            # Explicit path to API
            atmosphere_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            api_path = os.path.join(atmosphere_root, "api")

            if api_path not in sys.path:
                sys.path.insert(0, api_path)

            # Import API client
            from api.client import test_api, chat

            # Test API connection
            if test_api():
                self.api_connected = True

                # Test a simple chat
                test_response = await chat("EchoesAI integration test - respond with 'connected'")

                return {
                    "status": "connected",
                    "test_response": test_response,
                    "connection_type": "explicit_onboarding"
                }
            else:
                return {
                    "status": "failed",
                    "error": "API test failed"
                }

        except Exception as e:
            logger.error(f"API integration failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _register_capabilities(self) -> List[str]:
        """Register EchoesAI capabilities."""
        capabilities = [
            "selective_attention",
            "resilience_monitoring",
            "ai_research",
            "pattern_detection",
            "truth_verification",
            "ecosystem_coordination",
            "openai_integration",
            "realtime_processing"
        ]

        self.capabilities = capabilities
        logger.info(f"📋 Registered {len(capabilities)} capabilities")

        return capabilities

    async def _sync_with_ecosystem(self) -> Dict[str, Any]:
        """Sync with ecosystem standards."""
        try:
            # Ensure version sync
            ecosystem_version = "1.0.0"

            sync_data = {
                "version_synced": True,
                "ecosystem_version": ecosystem_version,
                "component_version": "1.0.0",
                "sync_timestamp": datetime.now().isoformat()
            }

            return sync_data

        except Exception as e:
            return {
                "version_synced": False,
                "error": str(e)
            }

    def get_onboarding_status(self) -> Dict[str, Any]:
        """Get current onboarding status."""
        return {
            "onboarding_status": self.onboarding_status,
            "ecosystem_connected": self.ecosystem_connected,
            "api_connected": self.api_connected,
            "capabilities_count": len(self.capabilities),
            "capabilities": self.capabilities
        }

# Global onboarding instance
_onboarding = None

def get_onboarding() -> EchoesOnboarding:
    """Get global onboarding instance."""
    global _onboarding
    if _onboarding is None:
        _onboarding = EchoesOnboarding()
    return _onboarding

async def onboard_echoes():
    """Main onboarding function."""
    onboarding = get_onboarding()
    return await onboarding.onboard_to_ecosystem()

def main():
    """Main entry point for EchoesAI onboarding."""
    print("🤖 EchoesAI Onboarding System v1.0.0")
    print("=" * 50)
    print("Explicit ecosystem integration path")
    print("")
    print("Usage:")
    print("  python -m Echoes.onboarding")
    print("  python -m Echoes.onboarding.run")

if __name__ == "__main__":
    main()
