#!/usr/bin/env python3
"""
EchoesAI Onboarding Main Entry Point
Run with: python -m Echoes.onboarding
"""

import asyncio
from . import onboard_echoes, get_onboarding

async def main():
    """Main onboarding execution."""
    print("🚀 Starting EchoesAI Explicit Onboarding...")
    print("=" * 60)
    
    try:
        # Execute onboarding
        result = await onboard_echoes()
        
        # Display results
        print(f"\n📊 Onboarding Status: {result['onboarding_status'].upper()}")
        
        if result['onboarding_status'] == 'complete':
            print("✅ EchoesAI successfully onboarded to ecosystem")
            
            # Show ecosystem connection
            if result.get('ecosystem_connection', {}).get('status') == 'connected':
                print("🌍 Ecosystem Connection: Established")
                print(f"   • Ecosystem Version: {result['ecosystem_connection']['ecosystem_version']}")
                print(f"   • Connection Type: {result['ecosystem_connection']['connection_type']}")
            
            # Show API integration
            if result.get('api_integration', {}).get('status') == 'connected':
                print("🔌 API Integration: Active")
                print(f"   • Test Response: {result['api_integration']['test_response']}")
            
            # Show capabilities
            capabilities = result.get('capabilities', [])
            print(f"📋 Capabilities Registered: {len(capabilities)}")
            for capability in capabilities:
                print(f"   • {capability}")
            
            # Show sync status
            if result.get('sync_status', {}).get('version_synced'):
                print("🔄 Version Sync: Complete")
            
            print("\n🎉 EchoesAI is now fully integrated into the Atmosphere ecosystem!")
            
        else:
            print(f"❌ Onboarding failed: {result.get('error', 'Unknown error')}")
        
        # Show current status
        onboarding = get_onboarding()
        status = onboarding.get_onboarding_status()
        print(f"\n📈 Current Status:")
        print(f"   • Onboarding: {status['onboarding_status']}")
        print(f"   • Ecosystem: {'Connected' if status['ecosystem_connected'] else 'Disconnected'}")
        print(f"   • API: {'Connected' if status['api_connected'] else 'Disconnected'}")
        print(f"   • Capabilities: {status['capabilities_count']}")
        
    except Exception as e:
        print(f"❌ Onboarding execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
