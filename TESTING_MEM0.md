# Mem0 Testing Guide

This guide explains how to test the Mem0 integration in nanobot.

## Prerequisites

### Required: Docker

The Mem0 server requires Docker to run. Make sure Docker is installed and running:

```bash
# Check Docker is installed
docker --version

# Check Docker is running
docker ps
```

**If Docker is not installed:**
- **Mac**: Install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Linux**: Install Docker Engine following [official docs](https://docs.docker.com/engine/install/)
- **Windows**: Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

## Test Suite Overview

### 1. Unit Tests (`tests/test_mem0_integration.py`)

These tests validate the client code structure without requiring a running server:

```bash
# Run unit tests (no server required)
source .venv/bin/activate
pytest tests/test_mem0_integration.py -v
```

**What they test:**
- ✅ Module imports
- ✅ Client initialization
- ✅ API method signatures
- ✅ Backward compatibility aliases
- ✅ Sync wrapper functionality

**When to run:** After any code changes to `mem0_client.py`

---

### 2. Live Integration Tests (`tests/test_mem0_live.py`)

These tests require a running Mem0 server and validate full CRUD operations:

```bash
# Step 1: Start Mem0 server
docker run -d -p 8000:8000 mem0ai/mem0:latest

# Step 2: Wait for server to be healthy (10-20 seconds)
curl http://localhost:8000/health

# Step 3: Run live tests
python tests/test_mem0_live.py

# Optional: Use custom server URL
MEM0_URL=http://localhost:8001 python tests/test_mem0_live.py
```

**What they test:**
- ✅ Server connection and health check
- ✅ Create, Read, Update, Delete (CRUD) operations
- ✅ Search functionality
- ✅ Multi-user isolation
- ✅ Sync wrapper functionality

**When to run:**
- Before deploying to production
- After Mem0 server upgrades
- When debugging integration issues

---

## Test Scenarios

### Scenario 1: Quick Verification (No Server)

```bash
# Just run unit tests to verify code structure
pytest tests/test_mem0_integration.py -v
```

**Expected output:**
```
✓ PASS: Imports
✓ PASS: Module Exports
✓ PASS: Client Initialization
✓ PASS: Backward Compatibility
✓ PASS: API Method Signatures
✓ PASS: Sync Wrapper
Total: 6/6 tests passed
```

---

### Scenario 2: Full Integration Test (With Server)

```bash
# Start Mem0 server
docker run -d --name mem0-test -p 8000:8000 mem0ai/mem0:latest

# Wait for health
sleep 15  # Give it time to start
curl http://localhost:8000/health

# Run all tests
pytest tests/ -v

# Cleanup
docker stop mem0-test
docker rm mem0-test
```

---

### Scenario 3: Manual Testing

```bash
# Start server
docker run -d -p 8000:8000 mem0ai/mem0:latest

# Open Python REPL
source .venv/bin/activate
python

>>> import asyncio
>>> from nanobot.memory import Mem0Client
>>>
>>> async def test():
...     client = Mem0Client(server_url="http://localhost:8000")
...
...     # Store memory
...     result = await client.store_memory(
...         user_id="test_user",
...         content="I love Python and AI",
...         metadata={"test": True}
...     )
...     print(f"Stored: {result}")
...
...     # Search
...     memories = await client.search_memories(
...         user_id="test_user",
...         query="Python",
...         limit=5
...     )
...     print(f"Found: {len(memories)} memories")
...
...     await client.close()
>>>
>>> asyncio.run(test())
```

---

## Docker Compose Testing

For testing the full stack (Mem0 + PostgreSQL + Nanobot):

```bash
# Deploy everything
docker-compose -f docker-compose.mem0.yml up -d

# Wait for services to be healthy
docker-compose -f docker-compose.mem0.yml ps

# Run tests against the deployed stack
MEM0_URL=http://localhost:8000 python tests/test_mem0_live.py

# Cleanup
docker-compose -f docker-compose.mem0.yml down -v
```

---

## Troubleshooting

### Issue: "Cannot connect to Mem0 server"

**Cause:** Mem0 server is not running

**Solution:**
```bash
# Check if server is running
curl http://localhost:8000/health

# If not running, start it
docker run -d -p 8000:8000 mem0ai/mem0:latest

# Check Docker is running
docker ps
```

---

### Issue: "Docker command not found"

**Cause:** Docker is not installed or not in PATH

**Solution:**
1. Install Docker Desktop for your platform
2. Start Docker Desktop application
3. Verify installation: `docker --version`

---

### Issue: "Port 8000 already in use"

**Cause:** Another service is using port 8000

**Solution:**
```bash
# Option 1: Use different port
docker run -d -p 8001:8000 mem0ai/mem0:latest
MEM0_URL=http://localhost:8001 python tests/test_mem0_live.py

# Option 2: Stop conflicting service
lsof -ti:8000 | xargs kill -9

# Option 3: Find what's using the port
lsof -i:8000
```

---

### Issue: "Tests timeout"

**Cause:** Mem0 server taking too long to start

**Solution:**
```bash
# Wait longer before running tests
docker run -d -p 8000:8000 mem0ai/mem0:latest
sleep 30  # Wait 30 seconds
curl http://localhost:8000/health  # Verify health first
python tests/test_mem0_live.py
```

---

## CI/CD Integration

For automated testing without Docker (CI/CD environments):

```bash
# Run only unit tests (no server required)
pytest tests/test_mem0_integration.py -v --tb=short

# Mock tests for CI/CD
pytest tests/ -v -m "not integration"
```

Create `pytest.ini` to exclude integration tests in CI:

```ini
[pytest]
markers =
    integration: Tests requiring live Mem0 server
    unit: Tests that don't require external services
```

Then mark tests in `test_mem0_live.py`:

```python
import pytest

@pytest.mark.integration
async def test_live_connection():
    ...

@pytest.mark.unit
def test_imports():
    ...
```

Run in CI:

```bash
# CI: Only unit tests
pytest tests/ -v -m "not integration"

# Local: All tests
pytest tests/ -v
```

---

## Performance Testing

To test performance under load:

```python
import asyncio
import time
from nanobot.memory import Mem0Client

async def benchmark_stores(n=100):
    client = Mem0Client(server_url="http://localhost:8000")
    start = time.time()

    tasks = [
        client.store_memory(
            user_id=f"user_{i % 10}",
            content=f"Test memory {i}"
        )
        for i in range(n)
    ]

    await asyncio.gather(*tasks)
    elapsed = time.time() - start

    await client.close()
    print(f"Stored {n} memories in {elapsed:.2f}s ({n/elapsed:.2f} mem/s)")

asyncio.run(benchmark_stores(100))
```

---

## Next Steps After Testing

Once all tests pass:

1. **Deploy to Production:** Follow `DEPLOYMENT_MEM0_STRATEGY.md`
2. **Update Documentation:** Add Mem0 to main README
3. **Migrate from Supermemory:** Use backward compatibility aliases
4. **Monitor Performance:** Set up logging and metrics

---

## Summary

| Test Type | Server Required | Command | When to Run |
|-----------|----------------|---------|-------------|
| Unit Tests | ❌ No | `pytest tests/test_mem0_integration.py` | After code changes |
| Integration Tests | ✅ Yes | `python tests/test_mem0_live.py` | Before deployment |
| Manual Tests | ✅ Yes | Python REPL | Debugging |
| Full Stack | ✅ Yes | `docker-compose -f docker-compose.mem0.yml up` | Production testing |

**Quick Start:**
```bash
# One command to run everything (if Docker is installed)
docker run -d -p 8000:8000 mem0ai/mem0:latest && \
sleep 15 && \
python tests/test_mem0_live.py
```
