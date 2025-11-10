"""
EchoesAI - Direct Connection Version
Zero middleware interference for authentic I/O properties.

Version: 1.0.0-Direct
Status: Middleware Removed
Connection: Direct OpenAI API
"""

__version__ = "1.0.0-Direct"
__author__ = "Atmosphere Team"
__description__ = "EchoesAI with direct OpenAI connection - zero middleware"

# Direct connection import - bypasses all middleware
try:
    from .direct import get_direct_connection, EchoesDirectConnection
    DIRECT_CONNECTION_AVAILABLE = True
except ImportError:
    DIRECT_CONNECTION_AVAILABLE = False

# Legacy components - non-middleware
try:
    from .echoes import __version__ as core_version
except ImportError:
    core_version = "unknown"

def get_echoes_status():
    """Get EchoesAI direct connection status."""
    status = {
        "version": __version__,
        "core_version": core_version,
        "direct_connection": DIRECT_CONNECTION_AVAILABLE,
        "middleware_bypassed": True,
        "connection_type": "direct_openai",
        "interference_level": "zero"
    }
    
    if DIRECT_CONNECTION_AVAILABLE:
        try:
            connection = get_direct_connection()
            conn_status = connection.get_connection_status()
            status.update(conn_status)
        except Exception as e:
            status["connection_error"] = str(e)
    
    return status

async def initialize_echoes_direct():
    """Initialize EchoesAI with direct connection."""
    if DIRECT_CONNECTION_AVAILABLE:
        from .direct import test_direct_connection
        
        print("EchoesAI Direct Connection Initializing...")
        success = await test_direct_connection()
        
        if success:
            print("EchoesAI Direct Connection: Operational")
            return True
        else:
            print("EchoesAI Direct Connection: Failed")
            return False
    
    print("EchoesAI Direct Connection: Not Available")
    return False

def main():
    """Main entry point for EchoesAI Direct."""
    print("EchoesAI v{} (Direct Connection)".format(__version__))
    print("=" * 50)
    print("Zero Middleware - Authentic I/O Properties")
    
    status = get_echoes_status()
    
    print("Status:")
    for key, value in status.items():
        if key != "api_key":
            print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    print("")
    print("Direct Connection Features:")
    print("   • Zero middleware interference")
    print("   • Authentic input-output properties")
    print("   • Direct OpenAI API connection")
    
    if DIRECT_CONNECTION_AVAILABLE:
        print("   • Direct connection system available")
    else:
        print("   • Direct connection system unavailable")
    
    print("")
    print("Usage:")
    print("  python -m Echoes.direct")
    print("  python -m Echoes.direct.test")

if __name__ == "__main__":
    main()
