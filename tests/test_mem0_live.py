#!/usr/bin/env python3
"""
Live integration test for Mem0 client.

This script tests the Mem0Client against a running Mem0 server.
Requires: Mem0 server running on http://localhost:8000 (or MEM0_URL env var)

To run Mem0 server:
  docker run -d -p 8000:8000 mem0ai/mem0:latest

Then run this script:
  python tests/test_mem0_live.py
"""

import asyncio
import os
import sys
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_live_connection():
    """Test basic connection to Mem0 server."""
    from nanobot.memory import Mem0Client

    server_url = os.getenv("MEM0_URL", "http://localhost:8000")
    print(f"🔍 Testing connection to Mem0 server at {server_url}")

    client = Mem0Client(server_url=server_url)

    try:
        # Test health check
        is_healthy = await client.health_check()
        if is_healthy:
            print("✅ Server is healthy")
        else:
            print("❌ Server health check failed")
            return False

        await client.close()
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        await client.close()
        return False


async def test_crud_operations():
    """Test basic CRUD operations."""
    from nanobot.memory import Mem0Client

    server_url = os.getenv("MEM0_URL", "http://localhost:8000")
    print(f"\n🧪 Testing CRUD operations")

    client = Mem0Client(server_url=server_url)
    test_user_id = "test_user_live"
    memory_id: Optional[str] = None

    try:
        # 1. Store a memory
        print("  → Storing memory...")
        result = await client.store_memory(
            user_id=test_user_id,
            content="Test memory: User loves Python programming and AI",
            metadata={"test": True, "category": "preferences"},
        )
        memory_id = result.get("memory_id") if isinstance(result, dict) else None
        print(f"  ✅ Memory stored: {memory_id}")

        # 2. Search memories
        print("  → Searching memories...")
        memories = await client.search_memories(
            user_id=test_user_id, query="Python programming", limit=5
        )
        print(f"  ✅ Found {len(memories)} memories")
        for mem in memories:
            print(f"     - {mem.get('memory', 'N/A')[:60]}...")

        # 3. Get specific memory
        if memory_id:
            print(f"  → Getting memory {memory_id}...")
            memory = await client.get_memory(memory_id)
            print(f"  ✅ Retrieved memory: {memory.get('memory', 'N/A')[:50]}...")

            # 4. Update memory
            print(f"  → Updating memory {memory_id}...")
            updated = await client.update_memory(
                memory_id=memory_id, content="Updated: User loves Python, AI, and FastAPI"
            )
            print(f"  ✅ Memory updated")

            # 5. Delete memory
            print(f"  → Deleting memory {memory_id}...")
            await client.delete_memory(memory_id)
            print(f"  ✅ Memory deleted")

        # 6. List all user memories
        print("  → Listing all user memories...")
        all_memories = await client.list_user_memories(user_id=test_user_id, limit=100)
        print(f"  ✅ User has {len(all_memories)} memories total")

        await client.close()
        return True

    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        import traceback

        traceback.print_exc()
        await client.close()
        return False


async def test_multi_user_isolation():
    """Test that different users have isolated memories."""
    from nanobot.memory import Mem0Client

    server_url = os.getenv("MEM0_URL", "http://localhost:8000")
    print(f"\n🔒 Testing multi-user isolation")

    client = Mem0Client(server_url=server_url)

    try:
        # User 1 stores memory
        await client.store_memory(
            user_id="user_alice", content="Alice loves coffee", metadata={"test": "isolation"}
        )

        # User 2 stores memory
        await client.store_memory(
            user_id="user_bob", content="Bob loves tea", metadata={"test": "isolation"}
        )

        # User 1 searches - should only see Alice's memory
        alice_results = await client.search_memories(user_id="user_alice", query="loves", limit=10)

        # User 2 searches - should only see Bob's memory
        bob_results = await client.search_memories(user_id="user_bob", query="loves", limit=10)

        # Verify isolation
        alice_memories = "coffee" in str(alice_results)
        bob_memories = "tea" in str(bob_results)
        no_crossover = "coffee" not in str(bob_results) and "tea" not in str(alice_results)

        if alice_memories and bob_memories and no_crossover:
            print("  ✅ Multi-user isolation working correctly")
            print(f"     Alice found: {len(alice_results)} memories (about coffee)")
            print(f"     Bob found: {len(bob_results)} memories (about tea)")
        else:
            print("  ❌ Multi-user isolation may be broken")
            print(f"     Alice results: {alice_results}")
            print(f"     Bob results: {bob_results}")
            return False

        await client.close()
        return True

    except Exception as e:
        print(f"❌ Isolation test failed: {e}")
        import traceback

        traceback.print_exc()
        await client.close()
        return False


async def test_sync_wrapper():
    """Test the synchronous wrapper."""
    from nanobot.memory import Mem0ClientSync

    server_url = os.getenv("MEM0_URL", "http://localhost:8000")
    print(f"\n🔄 Testing sync wrapper")

    client = Mem0ClientSync(server_url=server_url)

    try:
        # Test health check
        is_healthy = client.health_check()
        print(f"  ✅ Sync health check: {is_healthy}")

        # Test store
        result = client.store_memory(user_id="test_sync_user", content="Sync wrapper test memory")
        print(f"  ✅ Sync store memory: {result}")

        # Test search
        memories = client.search_memories(user_id="test_sync_user", query="sync", limit=5)
        print(f"  ✅ Sync search found: {len(memories)} memories")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Sync wrapper test failed: {e}")
        import traceback

        traceback.print_exc()
        client.close()
        return False


async def main():
    """Run all live tests."""
    print("=" * 70)
    print("Mem0 Client Live Integration Tests")
    print("=" * 70)

    results = {}

    # Test 1: Connection
    results["connection"] = await test_live_connection()
    if not results["connection"]:
        print("\n❌ Cannot proceed - server not available")
        print("\n💡 Start Mem0 server with:")
        print("   docker run -d -p 8000:8000 mem0ai/mem0:latest")
        return 1

    # Test 2: CRUD operations
    results["crud"] = await test_crud_operations()

    # Test 3: Multi-user isolation
    results["isolation"] = await test_multi_user_isolation()

    # Test 4: Sync wrapper
    results["sync"] = await test_sync_wrapper()

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary:")
    print("=" * 70)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
