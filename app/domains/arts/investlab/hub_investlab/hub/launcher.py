#!/usr/bin/env python3
"""
ResearchLab Launcher - Seamless Access to All Systems
Unified entry point for the complete research ecosystem
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ensure we can import all modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description='ResearchLab Launcher - Unified Access to Research Ecosystem',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py --quickstart "John Doe"     # Interactive journey
  python launcher.py --project "AI Research"     # Create research project
  python launcher.py --workflow research         # Start research workflow
  python launcher.py --status                    # System status
  python launcher.py --music motivation          # Music nudge
  python launcher.py --exchange research insights research_data '{"query": "test"}'
        """
    )

    parser.add_argument('--quickstart', nargs='?', const='Researcher', metavar='NAME',
                       help='Start interactive research journey (default: Researcher)')

    parser.add_argument('--project', metavar='TITLE',
                       help='Create new research project')

    parser.add_argument('--workflow', choices=['research', 'collaboration'],
                       help='Start specific workflow')

    parser.add_argument('--status', action='store_true',
                       help='Show system status')

    parser.add_argument('--music', choices=['direction', 'motivation', 'reflection', 'celebration'],
                       help='Play music nudge')

    parser.add_argument('--exchange', nargs=4, metavar=('SOURCE', 'TARGET', 'TYPE', 'PAYLOAD'),
                       help='Exchange data between modules (payload as JSON string)')

    parser.add_argument('--session', metavar='SESSION_ID',
                       help='Work with specific session')

    parser.add_argument('--monitor', action='store_true',
                       help='Show real-time monitoring dashboard')

    parser.add_argument('--validate', action='store_true',
                       help='Run system validation')

    args = parser.parse_args()

    print("🧪 ResearchLab Launcher")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Handle commands
    if args.quickstart:
        handle_quickstart(args.quickstart)
    elif args.project:
        handle_project_creation(args.project)
    elif args.workflow:
        handle_workflow(args.workflow)
    elif args.status:
        handle_status()
    elif args.music:
        handle_music_nudge(args.music)
    elif args.exchange:
        handle_data_exchange(args.exchange)
    elif args.session:
        handle_session_management(args.session)
    elif args.monitor:
        handle_monitoring()
    elif args.validate:
        handle_validation()
    else:
        show_main_menu()

def handle_quickstart(user_name: str):
    """Handle interactive quickstart"""
    print(f"🚀 Starting Interactive Journey for {user_name}")
    print("-" * 40)

    try:
        from interactive_quickstart import start_interactive_journey
        result = start_interactive_journey(user_name)

        print("
✅ Journey Completed!"        print(f"Session ID: {result['session_id']}")
        print(f"Capabilities Discovered: {len(result['discovered_capabilities'])}")

    except Exception as e:
        print(f"❌ Quickstart failed: {str(e)}")
        print("💡 Try running individual components instead")

def handle_project_creation(title: str):
    """Handle research project creation"""
    print(f"📋 Creating Research Project: {title}")
    print("-" * 40)

    try:
        from researchlab import initiate_project

        # Get additional details interactively
        description = input("Project description: ").strip() or f"Research project: {title}"
        domain = input("Research domain (artificial_intelligence, data_science, etc.): ").strip() or "artificial_intelligence"
        collaborators_input = input("Collaborators (comma-separated, leave empty for solo): ").strip()
        collaborators = [c.strip() for c in collaborators_input.split(',')] if collaborators_input else None

        project = initiate_project(title, description, domain, collaborators)

        print("
✅ Project Created!"        print(f"Project ID: {project['project_id']}")
        print(f"Domain: {domain}")
        if collaborators:
            print(f"Collaborators: {', '.join(collaborators)}")

        # Offer to start research workflow
        if input("\nStart research workflow now? (y/n): ").lower().startswith('y'):
            handle_research_workflow(project['project_id'])

    except Exception as e:
        print(f"❌ Project creation failed: {str(e)}")

def handle_research_workflow(project_id: str = None):
    """Handle research workflow execution"""
    if not project_id:
        project_id = input("Project ID: ").strip()

    if not project_id:
        print("❌ Project ID required")
        return

    print(f"🧪 Starting Research Workflow for Project: {project_id}")
    print("-" * 50)

    try:
        from researchlab import conduct_research

        research_query = input("Research query: ").strip() or f"Research investigation for {project_id}"

        print("Conducting research workflow..."        results = conduct_research(project_id, research_query)

        print("
✅ Research Workflow Completed!"        print(f"Project: {project_id}")
        print(f"Query: {research_query}")
        print(f"Components Generated: {len(results.get('research_results', {}))}")

        # Show insights
        insights = results.get('publication_insights', {}).get('key_findings', [])
        if insights:
            print(f"Key Insights: {len(insights)} generated")

    except Exception as e:
        print(f"❌ Research workflow failed: {str(e)}")

def handle_workflow(workflow_type: str):
    """Handle workflow initiation"""
    print(f"⚡ Starting {workflow_type.title()} Workflow")
    print("-" * 40)

    try:
        if workflow_type == 'research':
            handle_project_creation("Interactive Research Project")
        elif workflow_type == 'collaboration':
            # Start collaboration session
            from unified_hub import create_session, start_workflow

            session = create_session()
            result = start_workflow(session.session_id, 'collaboration_session')

            if 'error' not in result:
                print("✅ Collaboration session started!"                print(f"Session ID: {session.session_id}")
            else:
                print(f"❌ Collaboration failed: {result['error']}")

    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")

def handle_status():
    """Handle system status display"""
    print("📊 ResearchLab System Status")
    print("=" * 50)

    try:
        from unified_hub import get_unified_status

        status = get_unified_status()

        # Unified Hub
        uh = status['unified_hub']
        print("🧠 Unified Hub:"        print(f"   • Active Sessions: {uh['active_sessions']}")
        print(f"   • Workflows Available: {uh['available_workflows']}")
        print(f"   • Module Connections: {uh['module_connections']}")

        # Highway System
        hw = status['highway_system']
        print("
🛣️  Highway System:"        print(f"   • Modules Active: {hw['modules_active']}/7")
        print(f"   • Packets Routed: {hw['performance_metrics']['total_packets_routed']}")
        print(f"   • Success Rate: {hw.get('success_rate', 'N/A')}")

        # Research Lab
        rl = status['research_lab']
        print("
🧪 ResearchLab:"        print(f"   • Projects: {rl['active_projects']}")
        print(f"   • Research Tools: {len(rl.get('research_capabilities', {}))}")

        print(f"\n✅ System Health: {status.get('system_health', 'unknown').title()}")
        print(f"📅 Last Updated: {status.get('timestamp', 'unknown')[:19]}")

    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")

def handle_music_nudge(nudge_type: str):
    """Handle music nudge playback"""
    print(f"🎵 Playing {nudge_type.title()} Music Nudge")
    print("-" * 40)

    try:
        from entertainment.nudges.music_nudges import nudge_direction, nudge_motivation, nudge_reflection, nudge_celebration

        nudges = {
            'direction': nudge_direction,
            'motivation': nudge_motivation,
            'reflection': nudge_reflection,
            'celebration': nudge_celebration
        }

        result = nudges[nudge_type]()

        print("✅ Music nudge played!"        print(f"Song: {result['song']['title']}")
        print(f"Artist: {result['song']['artist']}")
        print(f"Message: {result['message']}")

    except Exception as e:
        print(f"❌ Music nudge failed: {str(e)}")

def handle_data_exchange(exchange_args: List[str]):
    """Handle data exchange between modules"""
    source, target, data_type, payload_str = exchange_args

    print(f"🔄 Exchanging Data: {source} → {target}")
    print("-" * 40)

    try:
        from unified_hub import exchange_data
        import json

        # Parse payload
        try:
            payload = json.loads(payload_str)
        except:
            payload = {'raw_data': payload_str}

        packet_id = exchange_data(source, target, data_type, payload)

        print("✅ Data exchange completed!"        print(f"Packet ID: {packet_id}")
        print(f"Source: {source}")
        print(f"Target: {target}")
        print(f"Type: {data_type}")

    except Exception as e:
        print(f"❌ Data exchange failed: {str(e)}")

def handle_session_management(session_id: str):
    """Handle session management"""
    print(f"👤 Managing Session: {session_id}")
    print("-" * 40)

    try:
        from unified_hub import get_session_status

        status = get_session_status(session_id)

        if 'error' in status:
            print(f"❌ Session not found: {status['error']}")
            return

        print("✅ Session Status:"        print(f"   • User: {status['user_id']}")
        print(f"   • Active Modules: {len(status['active_modules'])}")
        print(f"   • Created: {status['created_at'][:19]}")

        if status['current_workflow']:
            wf = status['current_workflow']
            print(f"   • Current Workflow: {wf['name']}")
            print(f"   • Progress: {wf['progress']}")

        print(f"   • Achievements: {len(status['achievements'])}")
        print(f"   • Data Exchanges: {status['data_exchanges']}")

    except Exception as e:
        print(f"❌ Session management failed: {str(e)}")

def handle_monitoring():
    """Handle monitoring dashboard display"""
    print("📈 Real-Time Monitoring Dashboard")
    print("=" * 50)

    try:
        from highway.monitor import get_highway_monitor

        dashboard = get_highway_monitor().get_real_time_dashboard()

        print("🛣️  Highway Status:"        hw_status = dashboard.get('highway_status', {})
        print(f"   • Modules Active: {hw_status.get('modules_active', 0)}/7")
        print(f"   • Packets Routed: {hw_status.get('total_packets', 0)}")

        print("
🧪 Research Status:"        research = dashboard.get('research_status', {})
        print(f"   • Active Projects: {research.get('active_projects', 0)}")
        print(f"   • Research Tools: {len(research.get('research_capabilities', {}))}")

        print("
🔗 Development Bridge:"        bridge = dashboard.get('development_sync', {})
        print(f"   • External Path: {bridge.get('external_path') or 'Disabled'}")

        print(f"\n📅 Timestamp: {dashboard.get('timestamp', 'unknown')[:19]}")

        # Show any optimization suggestions
        suggestions = dashboard.get('optimization_suggestions', [])
        if suggestions:
            print("
💡 Optimization Suggestions:"            for i, suggestion in enumerate(suggestions[:3], 1):  # Show first 3
                print(f"   {i}. {suggestion}")

    except Exception as e:
        print(f"❌ Monitoring failed: {str(e)}")

def handle_validation():
    """Handle system validation"""
    print("🔍 Running System Validation")
    print("=" * 50)

    try:
        # Import validation script and run it
        exec(open('validate_researchlab.py').read())
        print("\n✅ Validation completed!")

    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        print("💡 Try running: python validate_researchlab.py")

def show_main_menu():
    """Show main launcher menu"""
    print("🎯 ResearchLab Launcher - Main Menu")
    print("=" * 50)
    print()
    print("Available Commands:")
    print("  --quickstart [NAME]    Start interactive research journey")
    print("  --project TITLE        Create new research project")
    print("  --workflow TYPE        Start research or collaboration workflow")
    print("  --status              Show system status")
    print("  --music TYPE          Play music nudge (direction/motivation/reflection/celebration)")
    print("  --exchange SRC DST TYPE PAYLOAD    Exchange data between modules")
    print("  --session ID          Manage specific session")
    print("  --monitor             Show monitoring dashboard")
    print("  --validate            Run system validation")
    print()
    print("Examples:")
    print("  python launcher.py --quickstart")
    print("  python launcher.py --project 'My Research'")
    print("  python launcher.py --status")
    print("  python launcher.py --music motivation")
    print()
    print("For help: python launcher.py --help")

if __name__ == "__main__":
    main()
