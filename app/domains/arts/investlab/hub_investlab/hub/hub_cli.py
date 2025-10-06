#!/usr/bin/env python3
"""
Unified Hub CLI - Streamlined access to all sectors
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_research():
    """Run the research module"""
    print("🔬 Running Research Module...")
    try:
        from research.ai_service import AIService

        ai = AIService()
        data = ai.get_ai_dashboard()
        print(f"✅ AI Services: {len(data['local_ai']['ollama']['models'])} models active")
        return True
    except ImportError as e:
        print(f"❌ Research module not available: {e}")
        return False


def run_entertainment():
    """Run the entertainment module"""
    print("🎵 Running Entertainment Module...")
    try:
        from entertainment.media_service import MediaService
        from entertainment.nudges.music_nudges import MusicNudges

        media = MediaService()
        nudges = MusicNudges()

        data = media.get_media_dashboard()
        nudge = nudges.play_nudge("motivation")

        print(f"✅ Media Services: ${data['total_monetization']['monthly_total']} revenue")
        print(f"✅ Music Nudge: {nudge['song']['title']} by {nudge['song']['artist']}")
        return True
    except ImportError as e:
        print(f"❌ Entertainment module not available: {e}")
        return False


def run_finance():
    """Run the finance module"""
    print("💰 Running Finance Module...")
    try:
        from finance.finance_service import FinanceService

        finance = FinanceService()
        data = finance.get_finance_dashboard()
        print(f"✅ Finance: ${data['personal_finance']['total_assets']:,.0f} total assets")
        return True
    except ImportError as e:
        print(f"❌ Finance module not available: {e}")
        return False


def run_insights():
    """Run the insights module"""
    print("📊 Running Insights Module...")
    try:
        from insights.social_service import SocialService

        social = SocialService()
        data = social.get_social_dashboard()
        print(
            f"✅ Social Insights: {data['engagement_summary']['total_interactions']:,} interactions"
        )
        return True
    except ImportError as e:
        print(f"❌ Insights module not available: {e}")
        return False


def run_master():
    """Run the master hub"""
    print("🚀 Running Master Hub...")
    try:
        from master_hub import MasterHub

        hub = MasterHub()
        data = hub.fetch_all_services()
        print("✅ All services integrated successfully")
        print(f"   AI: {len(data['ai']['local_ai']['ollama']['models'])} models")
        print(f"   Finance: ${data['finance']['personal_finance']['total_assets']:,.0f}")
        print(f"   Media: ${data['media']['total_monetization']['monthly_total']}")
        print(
            f"   Social: {data['social']['engagement_summary']['total_interactions']:,} interactions"
        )
        return True
    except ImportError as e:
        print(f"❌ Master hub not available: {e}")
        return False


def run_weather():
    """Get weather information (placeholder for taskbar integration)"""
    print("🌤️ Getting Weather Information...")
    # This would integrate with a weather API
    weather_data = {
        "temperature": 22,
        "condition": "Partly Cloudy",
        "location": "Your Location",
        "humidity": 65,
        "wind_speed": 10,
    }
    print(f"✅ Weather: {weather_data['temperature']}°C, {weather_data['condition']}")
    return weather_data


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Unified Hub CLI")
    parser.add_argument(
        "command",
        choices=["research", "entertainment", "finance", "insights", "master", "weather", "all"],
        help="Module to run",
    )
    parser.add_argument(
        "--nudge",
        choices=["direction", "motivation", "reflection", "celebration"],
        help="Play a music nudge",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("    UNIFIED HUB CLI")
    print("    Streamlined Access to All Sectors")
    print("=" * 60)

    success = False

    if args.command == "all":
        # Run all modules
        modules = [run_research, run_entertainment, run_finance, run_insights]
        for module in modules:
            if not module():
                break
        else:
            success = True
    elif args.command == "research":
        success = run_research()
    elif args.command == "entertainment":
        success = run_entertainment()
    elif args.command == "finance":
        success = run_finance()
    elif args.command == "insights":
        success = run_insights()
    elif args.command == "master":
        success = run_master()
    elif args.command == "weather":
        success = run_weather()

    # Handle music nudge if specified
    if args.nudge and success:
        try:
            from entertainment.nudges.music_nudges import MusicNudges

            nudges = MusicNudges()
            nudge_result = nudges.play_nudge(args.nudge)
            print(
                f"🎵 Music Nudge: {nudge_result['song']['title']} by {nudge_result['song']['artist']}"
            )
            print(f"   Message: {nudge_result['message']}")
        except ImportError:
            print("❌ Music nudges not available")

    print("\n" + "=" * 60)
    if success:
        print("✅ Operation completed successfully!")
    else:
        print("❌ Some operations failed - check imports and file structure")
    print("=" * 60)


if __name__ == "__main__":
    main()
