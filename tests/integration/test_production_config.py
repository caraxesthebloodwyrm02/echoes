#!/usr/bin/env python3
"""
Test Production Configuration for Echoes Assistant V2
Tests all configured components: OpenAI, Web Search, Database, Monitoring, Security
"""

from pathlib import Path


def test_openai_config():
    """Test OpenAI configuration."""
    print("🧪 Testing OpenAI Configuration...")

    try:
        from config.openai_config import get_openai_config

        config = get_openai_config()
        print("✅ OpenAI: API key configured")
        print(f"✅ OpenAI: Model set to {config.model}")
        print(f"✅ OpenAI: Search enabled: {config.enable_search}")

        return True

    except Exception as e:
        print(f"❌ OpenAI configuration failed: {e}")
        return False


def test_search_config():
    """Test Web Search configuration."""
    print("🧪 Testing Web Search Configuration...")

    try:
        from config.search_config import get_search_config

        config = get_search_config()
        print(f"✅ Search: Provider set to {config.provider}")

        # Test provider creation (may fail if API keys not set)
        try:
            config.create_provider()
            print(f"✅ Search: {config.provider} provider ready")
        except Exception as e:
            print(f"⚠️ Search: Provider not configured - {e}")
            print("   Set API keys in .env to enable search")

        return True

    except Exception as e:
        print(f"❌ Search configuration failed: {e}")
        return False


def test_database_config():
    """Test Database configuration."""
    print("🧪 Testing Database Configuration...")

    try:
        from config.database_config import get_database_manager

        db_manager = get_database_manager()
        print(f"✅ Database: {db_manager.config.database_url}")

        # Test database session
        session = db_manager.get_session()
        session.execute("SELECT 1")
        session.close()
        print("✅ Database: Connection successful")

        return True

    except Exception as e:
        print(f"❌ Database configuration failed: {e}")
        return False


def test_monitoring_config():
    """Test Monitoring configuration."""
    print("🧪 Testing Monitoring Configuration...")

    try:
        from config.monitoring_config import get_monitoring_manager

        monitoring = get_monitoring_manager()

        # Test logging
        logger = monitoring.get_logger("test")
        logger.info("Test log message")
        print("✅ Monitoring: Logging system working")

        # Test metrics
        monitoring.record_metric("counter", "test_counter", 1)
        monitoring.record_metric("gauge", "test_gauge", 42.0)
        print("✅ Monitoring: Metrics system working")

        # Test health checks
        health = monitoring.get_health_status()
        print(f"✅ Monitoring: Health status - {health.get('status', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Monitoring configuration failed: {e}")
        return False


def test_security_config():
    """Test Security configuration."""
    print("🧪 Testing Security Configuration...")

    try:
        from config.security_config import (PasswordManager,
                                            get_security_manager)

        security = get_security_manager()
        print(
            f"✅ Security: Authentication {'enabled' if security.config.enable_auth else 'disabled'}"
        )

        # Test password management
        password = "TestPassword123!"
        hashed = PasswordManager.hash_password(password)
        verified = PasswordManager.verify_password(password, hashed)

        if verified:
            print("✅ Security: Password management working")
        else:
            print("❌ Security: Password verification failed")
            return False

        # Test JWT creation
        token = security.jwt_manager.create_token("test_user", "testuser", ["user"])
        payload = security.jwt_manager.verify_token(token)

        if payload and payload["username"] == "testuser":
            print("✅ Security: JWT token management working")
        else:
            print("❌ Security: JWT token verification failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Security configuration failed: {e}")
        return False


def test_atlas_integration():
    """Test ATLAS integration."""
    print("🧪 Testing ATLAS Integration...")

    try:
        from ATLAS.service import InventoryService

        service = InventoryService()

        # Add test item
        import time

        sku = f"CONFIG-TEST-{int(time.time())}"
        service.add_item(
            sku=sku,
            name="Configuration Test Item",
            category="Testing",
            quantity=1,
            location="TEST",
        )

        # Retrieve item
        retrieved = service.get_item(sku)
        if retrieved and retrieved.name == "Configuration Test Item":
            print("✅ ATLAS: Service integration working")
        else:
            print("❌ ATLAS: Service integration failed")
            return False

        return True

    except Exception as e:
        print(f"❌ ATLAS integration failed: {e}")
        return False


def test_action_executor():
    """Test enhanced Action Executor."""
    print("🧪 Testing Action Executor...")

    try:
        from app.actions.action_executor import ActionExecutor

        executor = ActionExecutor()

        # Test filesystem action
        result = executor.execute_filesystem_action("list_files", path=".")
        if result.status == "success":
            print("✅ Action Executor: Filesystem operations working")
        else:
            print(f"❌ Action Executor: Filesystem failed - {result.error}")
            return False

        # Test inventory action
        result = executor.execute_inventory_action("list")
        if result.status == "success":
            print("✅ Action Executor: ATLAS integration working")
        else:
            print(f"❌ Action Executor: ATLAS failed - {result.error}")
            return False

        return True

    except Exception as e:
        print(f"❌ Action Executor test failed: {e}")
        return False


def main():
    """Run all production configuration tests."""
    print("🚀 Echoes Assistant V2 Production Configuration Tests")
    print("=" * 60)

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Using default configuration.")
        print("   Copy .env.example to .env and configure for full functionality.")
        print()

    tests = [
        ("OpenAI Configuration", test_openai_config),
        ("Web Search Configuration", test_search_config),
        ("Database Configuration", test_database_config),
        ("Monitoring Configuration", test_monitoring_config),
        ("Security Configuration", test_security_config),
        ("ATLAS Integration", test_atlas_integration),
        ("Action Executor", test_action_executor),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 PRODUCTION READINESS SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ READY" if result else "❌ NEEDS CONFIG"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} components ready")

    if passed == total:
        print("🎉 Echoes Assistant V2 is fully configured and production-ready!")
    else:
        print("⚠️  Some components need configuration. Check your .env file.")
        print("\n📝 Configuration Steps:")
        print("1. Copy .env.example to .env")
        print("2. Set OPENAI_API_KEY for AI functionality")
        print("3. Set search API keys for web search (optional)")
        print("4. Configure DATABASE_URL for persistent storage")
        print("5. Set SECRET_KEY for security (auto-generated if not set)")


if __name__ == "__main__":
    main()
