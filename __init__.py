"""
Echoes Module - Advanced AI Research Platform
Integrated component of the Atmosphere ecosystem.

Version: 1.0.0 (Ecosystem Sync)
Status: Production Ready
Ecosystem Integration: Complete
"""

__version__ = "1.0.0"
__author__ = "Atmosphere Team"
__description__ = "Advanced AI research platform with ecosystem integration"

# Import ecosystem integration
try:
    import sys
    import os
    ecosystem_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(ecosystem_root)
    
    from ecosystem import get_ecosystem
    ECOSYSTEM_AVAILABLE = True
except ImportError:
    ECOSYSTEM_AVAILABLE = False

def get_echoes_status():
    """Get comprehensive Echoes status."""
    status = {
        "version": __version__,
        "ecosystem_integration": ECOSYSTEM_AVAILABLE,
        "capabilities": [
            "ai_research",
            "advanced_processing",
            "ecosystem_coordination"
        ]
    }
    
    if ECOSYSTEM_AVAILABLE:
        try:
            ecosystem = get_ecosystem()
            status["ecosystem_status"] = "connected"
        except:
            status["ecosystem_status"] = "available"
    else:
        status["ecosystem_status"] = "disconnected"
    
    return status

def main():
    """Main entry point for Echoes module."""
    # Apply egress policy auto-patch early if enabled (default on)
    try:
        from .core_modules.network import policy as net_policy  # type: ignore
        auto = os.environ.get("EGRESS_AUTOPATCH", "1")
        if auto.strip().lower() in {"1", "true", "yes", "on"}:
            net_policy.patch_requests()
    except Exception:
        # Fail-open for app startup; tests enforce sockets disabled separately
        pass

    print("🧠 Echoes v{}".format(__version__))
    print("=" * 30)
    print("Advanced AI research platform")
    print("Ecosystem Integration: {}".format("✅ Available" if ECOSYSTEM_AVAILABLE else "❌ Not Available"))
    
    status = get_echoes_status()
    
    if status.get("ecosystem_status") == "connected":
        print("🌍 Ecosystem: Connected")
    
    print("")
    print("Usage:")
    print("  python -m Echoes")

if __name__ == "__main__":
    main()
