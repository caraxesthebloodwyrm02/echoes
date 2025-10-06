#!/usr/bin/env python3
"""
ResearchLab Dashboard Launcher
Starts the unified dashboard with proper environment configuration
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'plotly', 'altair', 'pandas', 'numpy'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n📦 Installing missing packages...")

        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', *missing_packages
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False

    return True

def setup_environment():
    """Setup environment variables and paths"""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Set environment variables
    os.environ['PYTHONPATH'] = f"{current_dir};{os.environ.get('PYTHONPATH', '')}"

    # Create data directory if it doesn't exist
    data_dir = os.path.join(current_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    return True

def start_dashboard(port: int = 8501, headless: bool = False):
    """Start the ResearchLab dashboard"""
    print("🚀 Starting ResearchLab Unified Dashboard...")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        return False

    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return False

    # Dashboard command
    dashboard_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'researchlab_dashboard.py')

    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        return False

    cmd = [
        sys.executable, '-m', 'streamlit', 'run', dashboard_file,
        '--server.port', str(port),
        '--server.address', 'localhost'
    ]

    if headless:
        cmd.extend(['--server.headless', 'true'])

    print(f"📊 Starting dashboard on http://localhost:{port}")
    print("🌟 Opening ResearchLab Unified Dashboard...")
    print("💡 Use Ctrl+C to stop the dashboard")
    print("=" * 60)

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Dashboard failed to start: {e}")
        return False

    return True

def show_quick_guide():
    """Show quick usage guide"""
    guide = """
🧪 ResearchLab Dashboard Quick Guide
=====================================

🎯 Getting Started:
1. Initialize System: Click "Initialize ResearchLab System" in Overview tab
2. Explore Features: Use navigation tabs to discover capabilities
3. Create Projects: Start new research projects in Research Workspace
4. Collaborate: Join or create collaboration sessions
5. Get Insights: Use AI Assistant for research guidance

🚀 Key Features:
• 🤖 AI-Powered Research: Generate hypotheses, analyze data, design experiments
• 👥 Real-Time Collaboration: Multi-user research sessions and peer review
• 📊 Advanced Analytics: Interactive visualizations and statistical analysis
• 🎵 Emotional Intelligence: Music-guided productivity and motivation
• 🔄 Intelligent Routing: Seamless data exchange between all modules

📋 Dashboard Tabs:
• 🏠 Overview: System status, metrics, and real-time activity
• 🔬 Research: Project management, AI assistant, workflow execution
• 🤖 AI Insights: Model performance, usage analytics, insight history
• 👥 Collaboration: Session management, team coordination, analytics
• 🎵 Music Guidance: Emotional state analysis, nudge controls, history

🎮 Interactive Elements:
• Real-time metrics and performance indicators
• Interactive charts and data visualizations
• Collaborative session management
• AI assistant with multiple model support
• Music nudge system for productivity enhancement

🔧 Advanced Configuration:
• Supports multiple AI models (GPT-4, Claude-3, Gemini Pro, Local Ollama)
• Customizable collaboration workflows
• Extensible plugin architecture
• Real-time system monitoring and optimization

For more information, visit the ResearchLab documentation or contact support.
    """
    print(guide)

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description='ResearchLab Unified Dashboard Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dashboard_launcher.py              # Start dashboard on default port
  python dashboard_launcher.py --port 8080  # Start on custom port
  python dashboard_launcher.py --headless   # Run without browser
  python dashboard_launcher.py --guide      # Show usage guide
        """
    )

    parser.add_argument('--port', type=int, default=8501,
                       help='Port to run the dashboard on (default: 8501)')

    parser.add_argument('--headless', action='store_true',
                       help='Run in headless mode (no browser auto-open)')

    parser.add_argument('--guide', action='store_true',
                       help='Show quick usage guide and exit')

    parser.add_argument('--check-deps', action='store_true',
                       help='Check dependencies and exit')

    args = parser.parse_args()

    if args.guide:
        show_quick_guide()
        return

    if args.check_deps:
        print("🔍 Checking dependencies...")
        if check_dependencies():
            print("✅ All dependencies are installed!")
        else:
            print("❌ Some dependencies are missing")
        return

    # Start the dashboard
    success = start_dashboard(args.port, args.headless)

    if not success:
        print("\n❌ Dashboard failed to start properly")
        print("💡 Try running with --check-deps to verify dependencies")
        print("💡 Or use --guide for usage instructions")
        sys.exit(1)

if __name__ == "__main__":
    main()
