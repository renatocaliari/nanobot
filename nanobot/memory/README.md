# Nanobot Memory Module

Persistent memory capabilities for Nanobot through Supermemory MCP.

## Features

- ✅ **Persistent Memory**: Store and retrieve memories across sessions
- ✅ **Semantic Search**: Find relevant memories using natural language
- ✅ **User Isolation**: Separate memory spaces per user
- ✅ **Async & Sync**: Both async and synchronous client interfaces
- ✅ **MCP Protocol**: Standard Model Context Protocol integration

## Quick Start

### 1. Install Dependencies

```bash
pip install httpx
```

### 2. Configure Environment

```bash
export SUPERMEMORY_MCP_URL="http://localhost:3000"
export SUPERMEMORY_API_KEY="your-api-key"  # Optional
export SUPERMEMORY_ENABLED="true"
```

### 3. Use in Nanobot

```python
from nanobot.memory import SupermemoryMCPClientSync

# Initialize client
client = SupermemoryMCPClientSync()

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
│  │  - mcp_client.py (MCP client)               │  │
│  │  - config.py (Configuration)                │  │
│  └──────────────────────────────────────────────┘  │
│                      │                              │
│                      ▼                              │
│  ┌──────────────────────────────────────────────┐  │
│  │  Supermemory MCP Server                      │  │
│  │  - Persistent storage                        │  │
│  │  - Semantic search                           │  │
│  │  - Knowledge graph                           │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## API Reference

### SupermemoryMCPClient (Async)

```python
client = SupermemoryMCPClient(
    server_url="http://localhost:3000",
    api_key="optional-key",
    timeout=30.0
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

### SupermemoryMCPClientSync (Synchronous)

Same API as async client but with blocking calls:

```python
client = SupermemoryMCPClientSync()

# All methods are synchronous
client.store_memory(user_id="user123", content="...")
memories = client.search_memories(user_id="user123", query="...")
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SUPERMEMORY_MCP_URL` | MCP server URL | `http://localhost:3000` | No |
| `SUPERMEMORY_API_KEY` | Authentication key | `None` | No |
| `SUPERMEMORY_TIMEOUT` | Request timeout (seconds) | `30` | No |
| `SUPERMEMORY_ENABLED` | Enable memory feature | `true` | No |

## Self-Hosting Supermemory MCP

See `.supermemory/README.md` for self-hosting instructions.

Quick start:

```bash
git clone https://github.com/supermemoryai/supermemory-mcp.git
cd supermemory-mcp
npm install
npm run dev
```

## Docker Deployment

The full Docker setup includes Supermemory MCP:

```bash
docker-compose up -d
```

This starts:
- Nanobot with Supermemory integration
- Supermemory MCP server
- PostgreSQL database
- Qdrant vector store

See `DOKPLOY.md` for complete deployment guide.

## Examples

### Context-Aware Chat

```python
from nanobot.memory import SupermemoryMCPClientSync

client = SupermemoryMCPClientSync()

def chat_with_memory(user_id: str, message: str):
    # Search relevant memories
    memories = client.search_memories(
        user_id=user_id,
        query=message,
        limit=3
    )

    # Build context from memories
    context = "\n".join([m["content"] for m in memories])

    # Generate response with context
    response = generate_response(message, context)

    # Store interaction
    client.store_memory(
        user_id=user_id,
        content=f"User: {message}\nAssistant: {response}",
        metadata={"type": "chat_interaction"}
    )

    return response
```

### User Preferences

```python
# Store preference
client.store_memory(
    user_id="user123",
    content="User prefers dark mode in all applications",
    metadata={"type": "preference", "category": "ui"}
)

# Retrieve preferences
preferences = client.search_memories(
    user_id="user123",
    query="preferences settings",
    filters={"type": "preference"}
)
```

### Learning from Feedback

```python
def record_feedback(user_id: str, rating: int, context: str):
    client.store_memory(
        user_id=user_id,
        content=f"User rated response {rating}/5. Context: {context}",
        metadata={"type": "feedback", "rating": rating}
    )
```

## Troubleshooting

### Connection Refused

```bash
# Check if MCP server is running
curl http://localhost:3000/health

# Start server
cd supermemory-mcp && npm run dev
```

### Import Errors

```bash
# Install dependencies
pip install httpx

# Or with Docker
docker-compose build
```

### Memory Not Persisting

```bash
# Check environment variables
echo $SUPERMEMORY_MCP_URL
echo $SUPERMEMORY_ENABLED

# Check logs
docker-compose logs supermemory-mcp
```

## License

MIT - See main LICENSE file.

## Contributing

Contributions welcome! Please read `CONTRIBUTING.md`.
