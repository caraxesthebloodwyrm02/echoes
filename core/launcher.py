"""
Glimpse - Interactive Launcher
Provides menu-driven interface to explore the system
"""

import sys
from pathlib import Path


def print_header():
    """Print system header"""
    print("=" * 70)
    print("GLIMPSE")
    print("=" * 70)
    print()
    print("A decision-support layer for visualizing creative trajectories")
    print("in real time with cause-effect mapping and predictive guidance.")
    print()


def print_menu():
    """Print main menu"""
    print("\n" + "=" * 70)
    print("MAIN MENU")
    print("=" * 70)
    print()
    print("1. Run Text Editor Demo")
    print("2. Run Code Editor Demo")
    print("3. Run Test Suite")
    print("4. Security Check")
    print("5. Interactive Playground")
    print("6. View Documentation")
    print("7. System Information")
    print("8. Live Preview (GUI - Tk + SSE)")
    print("0. Exit")
    print()


def run_text_demo():
    """Run text editor demo"""
    print("\n🚀 Launching Glimpse Text Editor Demo...\n")
    try:
        import demo_text_editor
        demo_text_editor.simulate_writing_session()
        print("\n" + "=" * 70)
        input("\nPress Enter to return to menu...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")


def run_code_demo():
    """Run code editor demo"""
    print("\n🚀 Launching Glimpse Code Editor Demo...\n")
    try:
        import demo_code_editor
        demo_code_editor.simulate_coding_session()
        print("\n" + "=" * 70)
        input("\nPress Enter to return to menu...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")


def run_gui():
    """Launch Tkinter SSE Live Preview UI"""
    print("\n🚀 Launching Glimpse Tk + SSE Live Preview UI...\n")
    try:
        import ui_tk
        ui_tk.main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to continue...")


def run_tests():
    """Run test suite"""
    print("\n🧪 Running Glimpse Test Suite...\n")
    try:
        import test_suite
        test_suite.run_all_tests()
        print("\n" + "=" * 70)
        input("\nPress Enter to return to menu...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")


def security_check():
    """Run security check"""
    print("\n🔒 Running Glimpse Security Check...\n")
    try:
        from security_integration import SecurityManager
        
        security = SecurityManager(
            base_path=Path(__file__).parent,
            enable_thon_integration=True
        )
        
        print("Assessing security context...")
        context = security.assess_security_context()
        
        print("\n" + "=" * 70)
        print("SECURITY REPORT")
        print("=" * 70)
        print(f"\nShield Factor: {context.shield_factor:.3f}")
        print(f"Risk Level: {context.risk_level.upper()}")
        print(f"Safety Status: {'✓ SAFE' if context.is_safe else '✗ UNSAFE'}")
        print(f"\nAllowed Operations:")
        for op in context.allowed_operations:
            print(f"  ✓ {op}")
        
        metrics = security.get_security_metrics()
        print(f"\nThon Integration: {'✓ Active' if metrics['thon_integrated'] else '✗ Inactive'}")
        print(f"Detector: {'✓ Active' if metrics['detector_active'] else '✗ Inactive'}")
        
        if 'thon_metrics' in metrics:
            tm = metrics['thon_metrics']
            print(f"\nThon Metrics:")
            print(f"  Attractor Strength: {tm['avg_attractor_strength']:.3f}")
            print(f"  High Aggressive Jammers: {tm['high_aggressive_jammers']}")
            print(f"  Consecutive Jam Alert: {tm['consecutive_jam_alert']}")
        
        print("\n" + "=" * 70)
        input("\nPress Enter to return to menu...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to continue...")


def interactive_playground():
    """Interactive playground for experimenting"""
    print("\n🎮 Interactive Playground")
    print("=" * 70)
    print()
    
    try:
        from realtime_preview import create_glimpse
        
        # Choose mode
        print("Select visualization mode:")
        print("1. Timeline")
        print("2. Tree")
        print("3. Flow")
        print("4. Heatmap")
        mode_choice = input("\nEnter choice (1-4): ").strip()
        
        modes = {"1": "timeline", "2": "tree", "3": "flow", "4": "heatmap"}
        mode = modes.get(mode_choice, "timeline")
        
        print(f"\n✓ Creating system with {mode} mode...")
        system = create_glimpse(mode=mode, enable_security=True)
        
        if not system.start():
            print("❌ Failed to start system")
            input("\nPress Enter to continue...")
            return
        
        print("✓ System started!")
        print("\nType text (or 'quit' to exit, 'preview' to see visualization):")
        print("-" * 70)
        
        position = 0
        while True:
            user_input = input("\n> ")
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'preview':
                preview = system.get_current_preview()
                if preview:
                    print("\nCurrent Preview:")
                    print(preview)
                else:
                    print("\nNo preview available yet")
                continue
            elif user_input.lower() == 'state':
                state = system.get_full_state()
                print(f"\nTotal Events: {state['system']['total_events']}")
                print(f"Direction: {state['trajectory']['current_direction']}")
                print(f"Health: {state['trajectory']['trajectory_health']:.2f}")
                continue
            
            # Process input
            result = system.process_input(
                action="insert",
                position=position,
                text=user_input + " "
            )
            
            if result.get("success"):
                traj = result.get("trajectory", {})
                print(f"  Direction: {traj.get('current_direction', '?')}")
                print(f"  Confidence: {traj.get('confidence', 0):.2f}")
                
                suggestions = result.get("suggestions", [])
                if suggestions:
                    print(f"  Suggestions: {', '.join(suggestions[:3])}")
                
                position += len(user_input) + 1
        
        system.stop()
        print("\n✓ Session complete!")
        input("\nPress Enter to return to menu...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to continue...")


def view_documentation():
    """View documentation"""
    print("\n📖 Documentation")
    print("=" * 70)
    print()
    
    readme_path = Path(__file__).parent / "README.md"
    
    if readme_path.exists():
        print("README.md contents:\n")
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Show first 50 lines
            lines = content.splitlines()[:50]
            for line in lines:
                print(line)
            
            if len(content.splitlines()) > 50:
                print("\n... (see README.md for full documentation)")
    else:
        print("README.md not found")
    
    print("\n" + "=" * 70)
    print("\nKey Files:")
    print("  - README.md: Full documentation")
    print("  - core_trajectory.py: Trajectory engine")
    print("  - input_adapter.py: Input handling")
    print("  - visual_renderer.py: Visualization")
    print("  - security_integration.py: Security features")
    print("  - realtime_preview.py: Glimpse orchestrator")
    
    input("\nPress Enter to return to menu...")


def system_info():
    """Display system information"""
    print("\n💡 System Information")
    print("=" * 70)
    print()
    
    print(f"Python Version: {sys.version}")
    print(f"Base Path: {Path(__file__).parent}")
    print()
    
    # Check components
    components = [
        ("Core Trajectory", "core_trajectory.py"),
        ("Input Adapter", "input_adapter.py"),
        ("Visual Renderer", "visual_renderer.py"),
        ("Security Integration", "security_integration.py"),
        ("Glimpse Orchestrator", "realtime_preview.py"),
        ("Text Demo", "demo_text_editor.py"),
        ("Code Demo", "demo_code_editor.py"),
        ("Test Suite", "test_suite.py"),
    ]
    
    print("Components:")
    for name, filename in components:
        path = Path(__file__).parent / filename
        status = "✓" if path.exists() else "✗"
        print(f"  {status} {name:<25} ({filename})")
    
    print()
    
    # Check parent thon.py
    thon_path = Path(__file__).parent.parent / "thon.py"
    print(f"Security Module (thon.py): {'✓ Found' if thon_path.exists() else '✗ Not Found'}")
    
    print("\n" + "=" * 70)
    print("\nConfiguration:")
    print("  - Pure Python (no external dependencies)")
    print("  - Modular architecture")
    print("  - Integrated security system")
    print("  - Multiple visualization modes")
    print("  - Real-time trajectory tracking")
    
    input("\nPress Enter to return to menu...")


def main():
    """Main launcher loop"""
    print_header()
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-7): ").strip()
        
        if choice == "0":
            print("\n👋 Thank you for using Glimpse!")
            print("May your trajectories be clear and your predictions accurate.\n")
            break
        elif choice == "1":
            run_text_demo()
        elif choice == "2":
            run_code_demo()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            security_check()
        elif choice == "5":
            interactive_playground()
        elif choice == "6":
            view_documentation()
        elif choice == "7":
            system_info()
        elif choice == "8":
            run_gui()
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Exiting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
