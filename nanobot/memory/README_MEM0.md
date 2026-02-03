# Mem0 Integration for Nanobot

Persistent memory capabilities for Nanobot through Mem0 (drop-in replacement for Supermemory).

## Features

- ✅ **Persistent Memory**: Store and retrieve memories across sessions
- ✅ **Semantic Search**: Find relevant memories using natural language
- ✅ **User Isolation**: Separate memory spaces per user
- ✅ **Async & Sync**: Both async and synchronous client interfaces
- ✅ **Open Source**: 100% MIT license - no vendor lock-in
- ✅ **Self-Hosted**: Full control over your data
- ✅ **No Limits**: You define the limits

## Quick Start

### 1. Start Mem0 Server

**Option A: Docker Compose (Recommended)**

```bash
git clone https://github.com/Mem0-ai/mem0.git
cd mem0
docker-compose up -d
```

This starts:
- Mem0 API server on http://localhost:8000
- PostgreSQL database with pgvector
- Qdrant vector database

**Option B: Docker Single Container**

```bash
docker run -d \
  -p 8000:8000 \
  -e POSTGRES_URI="postgresql://user:pass@host:port/db" \
  mem0ai/mem0:latest
```

**Option C: Local Install**

```bash
pip install mem0ai
mem0 server
```

### 2. Configure Environment

```bash
export MEM0_URL="http://localhost:8000"
export MEM0_ENABLED="true"
export MEM0_COLLECTION="nanobot"  # Optional
```

### 3. Use in Nanobot

```python
from nanobot.memory import Mem0ClientSync

# Initialize client
client = Mem0ClientSync()

# Store a memory
client.store_memory(
    user_id="user123",
    content="User prefers Python over JavaScript",
    metadata={"source": "chat", "tags": ["preference"]}
)

# Search memories
memories = client.search_memories(
    user_id="user123",
    query="programming languages",
    limit=5
)

for memory in memories:
    print(f"Content: {memory['content']}")
    print(f"Score: {memory['score']}")
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Nanobot Agent                                      │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Memory Module                               │  │
│  │  - mem0_client.py (Mem0 client)             │  │
│  │  - config.py (Configuration)                │  │
│  └──────────────────────────────────────────────┘  │
│                      │                              │
│                      ▼                              │
│  ┌──────────────────────────────────────────────┐  │
│  │  Mem0 Server                                │  │
│  │  - Persistent storage                        │  │
│  │  - Semantic search                           │  │
│  │  - User isolation                            │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## API Reference

### Mem0Client (Async)

```python
client = Mem0Client(
    server_url="http://localhost:8000",
    collection_name="nanobot"
)

# Store memory
await client.store_memory(
    user_id="user123",
    content="Memory content",
    metadata={"key": "value"}
)

# Search memories
memories = await client.search_memories(
    user_id="user123",
    query="search query",
    limit=5
)

# Get specific memory
memory = await client.get_memory(memory_id="abc123")

# Update memory
updated = await client.update_memory(
    memory_id="abc123",
    content="New content"
)

# Delete memory
success = await client.delete_memory(memory_id="abc123")

# List all user memories
all_memories = await client.list_user_memories(
    user_id="user123",
    limit=100
)
```

### Mem0ClientSync (Synchronous)

Same API as async client but with blocking calls:

```python
client = Mem0ClientSync()

# All methods are synchronous
client.store_memory(user_id="user123", content="...")
memories = client.search_memories(user_id="user123", query="...")
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MEM0_URL` | Mem0 server URL | `http://localhost:8000` | No |
| `MEM0_API_KEY` | Authentication key | `None` | No |
| `MEM0_TIMEOUT` | Request timeout (seconds) | `30` | No |
| `MEM0_ENABLED` | Enable memory feature | `true` | No |
| `MEM0_COLLECTION` | Collection name | `nanobot` | No |

## Backward Compatibility

Mem0 client is a **drop-in replacement** for Supermemory:

```python
# Old code using Supermemory
from nanobot.memory import SupermemoryMCPClientSync

# Still works! Just imports Mem0Client instead
client = SupermemoryMCPClientSync()  # Actually Mem0Client under the hood
```

No code changes needed - just update environment variables:

```bash
# Old
export SUPERMEMORY_MCP_URL="http://localhost:3000"

# New
export MEM0_URL="http://localhost:8000"
```

## Multi-Bot Configuration

Configure different Mem0 instances per bot or share one:

```json
{
  "mcps": {
    "mcps": [
      {
        "name": "mem0-shared",
        "type": "http",
        "url": "http://localhost:8000",
        "description": "Shared Mem0 for all bots"
      }
    ]
  }
}
```

Or use user_id to separate memories per bot automatically!

## Docker Deployment

### Option 1: Separate Docker Container

```yaml
# docker-compose.yml
services:
  mem0:
    image: mem0ai/mem0:latest
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_URI=postgresql://mem0:password@postgres:5432/mem0
    depends_on:
      - postgres
      - qdrant
  
  nanobot:
    build: .
    environment:
      - MEM0_URL=http://mem0:8000
      - MEM0_ENABLED=true
    depends_on:
      - mem0
```

### Option 2: Same Container (Recommended for Simplicity)

Run Mem0 and nanobot in the same Dokploy project.

## Migration from Supermemory

If you have data in Supermemory:

1. **Export from Supermemory** (if still accessible):
```bash
# Via Supermemory API
curl -H "Authorization: Bearer $SUPERMEMORY_API_KEY" \
  https://api.supermemory.ai/v1/memory/list \
  > supermemory_export.json
```

2. **Import to Mem0**:
```python
from nanobot.memory import Mem0ClientSync

client = Mem0ClientSync()

with open("supermemory_export.json") as f:
    memories = json.load(f)

for memory in memories:
    client.store_memory(
        user_id=memory["user_id"],
        content=memory["content"],
        metadata=memory.get("metadata", {})
    )
```

## Troubleshooting

### Connection Refused

```bash
# Check if Mem0 server is running
curl http://localhost:8000/health

# Start server
cd mem0 && docker-compose up -d
```

### Import Errors

```bash
# No new dependencies needed!
# Mem0 client uses httpx (already required)
```

### Memory Not Persisting

```bash
# Check environment variables
echo $MEM0_URL
echo $MEM0_ENABLED

# Check logs
docker logs mem0
```

## Benefits over Supermemory

| Feature | Supermemory | Mem0 |
|---------|-------------| ------|
| **Open Source** | ❌ | ✅ MIT |
| **Self-Hosted** | ⚠️ Limited | ✅ Full |
| **Limits** | ❌ Unknown | ✅ None |
| **Data Control** | ❌ Cloud | ✅ Yours |
| **Vendor Lock-in** | ❌ Yes | ✅ No |
| **Multi-Bot** | ❌ | ✅ user_id isolation |

## License

MIT - See main LICENSE file.

## Contributing

Contributions welcome! Please read `CONTRIBUTING.md`.
