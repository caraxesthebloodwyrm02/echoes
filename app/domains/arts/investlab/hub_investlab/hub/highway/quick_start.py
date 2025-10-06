#!/usr/bin/env python3
"""
Highway Quick Start - Easy access to the intelligent routing system
"""

import os
import sys
from highway import get_highway
from highway.router import get_highway_router
from highway.development_bridge import get_development_bridge
from highway.monitor import get_highway_monitor

def quick_start():
    """Quick start guide for the Highway system"""
    print("🛣️  Highway Intelligent Routing System")
    print("=" * 50)
    print()
    print("✅ System Status:")
    print("   - Highway: Active")
    print("   - Router: Active")
    print("   - Development Bridge: Active")
    print("   - Monitor: Active")
    print()
    print("📋 Available Commands:")
    print("   1. sync_with_development() - Sync with E:\\projects\\development")
    print("   2. route_research_to_dev(data) - Send research to development")
    print("   3. route_dev_to_research(data) - Send development insights to research")
    print("   4. start_monitoring() - Start real-time monitoring")
    print("   5. get_dashboard() - Get real-time dashboard")
    print()
    print("🚀 Quick Examples:")
    print()

    # Example 1: Sync with development
    print("📊 Example 1: Sync with development projects")
    dev_bridge = get_development_bridge()
    sync_result = dev_bridge.sync_with_external_projects()
    print(f"   Synced {sync_result['projects_found']} projects")
    print()

    # Example 2: Route data
    print("🔄 Example 2: Route research insights to development")
    router = get_highway_router()
    packet_id = router.route_research_to_development({
        'ai_model': 'new_transformer',
        'performance': 0.95,
        'use_case': 'financial_prediction'
    })
    print(f"   Routed with packet ID: {packet_id}")
    print()

    # Example 3: Get dashboard
    print("📈 Example 3: Get real-time dashboard")
    monitor = get_highway_monitor()
    dashboard = monitor.get_real_time_dashboard()
    print(f"   Modules active: {dashboard['highway_status']['modules_active']}/7")
    print()

    # Example 4: Development bridge
    print("🏗️  Example 4: Create development bridge")
    bridge_id = dev_bridge.create_development_bridge(
        'research', 'external', 
        {'project': 'ai_finance_integration', 'status': 'in_progress'}
    )
    print(f"   Bridge created: {bridge_id}")
    print()

    print("📚 Usage Guide:")
    print("   # Basic routing")
    print("   from highway import get_highway")
    print("   highway = get_highway()")
    print("   ")
    print("   # Route between modules")
    print("   from highway.router import get_highway_router")
    print("   router = get_highway_router()")
    print("   router.route_finance_to_content({'market_trend': 'bullish'})")
    print("   ")
    print("   # Development integration")
    print("   from highway.development_bridge import get_development_bridge")
    print("   bridge = get_development_bridge()")
    print("   bridge.sync_with_external_projects()")
    print("   ")
    print("   # Monitoring")
    print("   from highway.monitor import get_highway_monitor")
    print("   monitor = get_highway_monitor()")
    print("   monitor.start_monitoring()")

if __name__ == "__main__":
    quick_start()
