"""Test Mem0 integration."""

import json
import sys
import os
from pathlib import Path
import pytest


@pytest.mark.unit
def test_mem0_imports():
    """Test that all Mem0 imports work correctly."""
    print("Testing Mem0 imports...")

    from nanobot.memory.mem0_client import (
        Mem0Client,
        Mem0ClientSync,
        SupermemoryMCPClient,
    )

    print("✓ All Mem0 classes imported successfully")

    # Verify backward compatibility alias
    assert SupermemoryMCPClient == Mem0Client, (
        "SupermemoryMCPClient should be an alias for Mem0Client"
    )
    print("✓ Backward compatibility alias (SupermemoryMCPClient = Mem0Client) works")


@pytest.mark.unit
def test_mem0_module_exports():
    """Test that memory module exports Mem0 classes."""
    print("\nTesting memory module exports...")

    from nanobot.memory import Mem0Client, Mem0ClientSync, SupermemoryMCPClient

    print("✓ Memory module exports Mem0Client, Mem0ClientSync, and SupermemoryMCPClient")

    # Verify backward compatibility
    assert SupermemoryMCPClient == Mem0Client
    print("✓ Module-level backward compatibility works")


@pytest.mark.unit
def test_mem0_client_initialization():
    """Test Mem0Client initialization with different configurations."""
    print("\nTesting Mem0Client initialization...")

    from nanobot.memory.mem0_client import Mem0Client

    # Test 1: Default URL
    client1 = Mem0Client()
    assert client1.server_url == "http://localhost:8000" or client1.server_url == os.getenv(
        "MEM0_URL", "http://localhost:8000"
    )
    print("✓ Mem0Client initialized with default URL")

    # Test 2: Custom URL
    client2 = Mem0Client(server_url="http://localhost:8001")
    assert client2.server_url == "http://localhost:8001"
    print("✓ Mem0Client initialized with custom URL (http://localhost:8001)")

    # Test 3: With API key
    client3 = Mem0Client(server_url="http://localhost:8001", api_key="test-key-123")
    assert client3.server_url == "http://localhost:8001"
    assert client3.api_key == "test-key-123"
    print("✓ Mem0Client initialized with API key")

    # Test 4: With custom collection
    client4 = Mem0Client(collection_name="test-collection")
    assert client4.collection_name == "test-collection"
    print("✓ Mem0Client initialized with custom collection name")


@pytest.mark.unit
def test_backward_compatibility_imports():
    """Test that Supermemory import aliases work."""
    print("\nTesting backward compatibility imports...")

    # Old import style should still work
    from nanobot.memory.mem0_client import SupermemoryMCPClient as Supermemory
    from nanobot.memory import SupermemoryMCPClient as Supermemory2

    print("✓ Old-style SupermemoryMCPClient imports work")

    # Both should resolve to Mem0Client
    from nanobot.memory.mem0_client import Mem0Client

    assert Supermemory == Mem0Client
    assert Supermemory2 == Mem0Client
    print("✓ All SupermemoryMCPClient aliases resolve to Mem0Client")


@pytest.mark.unit
def test_api_method_signatures():
    """Test that Mem0Client has all required API methods."""
    print("\nTesting API method signatures...")

    from nanobot.memory.mem0_client import Mem0Client

    required_methods = [
        "store_memory",
        "search_memories",
        "get_memory",
        "update_memory",
        "delete_memory",
        "list_user_memories",
        "health_check",
        "close",
    ]

    client = Mem0Client()

    for method_name in required_methods:
        assert hasattr(client, method_name), f"Missing method: {method_name}"
        method = getattr(client, method_name)
        assert callable(method), f"{method_name} is not callable"

    print(f"✓ All {len(required_methods)} required API methods are present and callable")


@pytest.mark.unit
def test_sync_wrapper():
    """Test Mem0ClientSync wrapper."""
    print("\nTesting Mem0ClientSync wrapper...")

    from nanobot.memory.mem0_client import Mem0ClientSync

    sync_client = Mem0ClientSync()
    print("✓ Mem0ClientSync initialized successfully")

    # Verify it wraps async client
    assert hasattr(sync_client, "async_client")
    assert (
        sync_client.async_client.server_url == "http://localhost:8000"
        or sync_client.async_client.server_url == os.getenv("MEM0_URL", "http://localhost:8000")
    )
    print("✓ Mem0ClientSync correctly wraps Mem0Client")

    # Verify it has the same methods as async client
    async_methods = [
        "store_memory",
        "search_memories",
        "get_memory",
        "update_memory",
        "delete_memory",
        "list_user_memories",
        "health_check",
        "close",
    ]
    for method_name in async_methods:
        assert hasattr(sync_client, method_name), f"Mem0ClientSync missing method: {method_name}"

    print("✓ Mem0ClientSync has all required methods")


def run_all_tests():
    """Run all Mem0 integration tests."""
    print("=" * 60)
    print("MEM0 INTEGRATION TEST SUITE")
    print("=" * 60)

    results = []

    test_functions = [
        ("Imports", test_mem0_imports),
        ("Module Exports", test_mem0_module_exports),
        ("Client Initialization", test_mem0_client_initialization),
        ("Backward Compatibility", test_backward_compatibility_imports),
        ("API Method Signatures", test_api_method_signatures),
        ("Sync Wrapper", test_sync_wrapper),
    ]

    for test_name, test_func in test_functions:
        try:
            test_func()
            results.append((test_name, True))
        except Exception:
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


def test_mock_server_operations():
    """
    Test Mem0 operations with a mock server.

    This test would require an actual Mem0 server running.
    For now, it's a placeholder for future integration testing.
    """
    print("\n" + "=" * 60)
    print("MOCK SERVER OPERATIONS (Requires running Mem0 server)")
    print("=" * 60)

    print("\nTo test with a real Mem0 server:")
    print("1. Start Mem0 server:")
    print("   docker run -d -p 8001:8000 mem0ai/mem0:latest")
    print("\n2. Run this test with:")
    print("   python tests/test_mem0_integration.py --with-server")
    print("\n3. Or use docker-compose:")
    print("   docker-compose -f docker-compose.mem0.yml up -d")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--with-server":
        test_mock_server_operations()
    else:
        exit_code = run_all_tests()
        sys.exit(exit_code)
