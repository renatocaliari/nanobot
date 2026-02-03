# Multi-Bot Architecture Design

## Overview

Support multiple Telegram bots with separate:
- **Personalities** (SOUL.md, AGENTS.md per bot)
- **Workspaces** (isolated memory and files)
- **MCP Servers** (different MCPs per bot)
- **Memories** (Mem0 multi-user isolation via `user_id`)

## Configuration Structure

### 1. Bots Configuration (`~/.nanobot/bots.json`)

```json
{
  "bots": [
    {
      "id": "health-bot",
      "name": "Dr. Bot Saúde",
      "description": "Assistente especializado em saúde e bem-estar",

      "channels": {
        "telegram": {
          "enabled": true,
          "token": "BOT_TOKEN_1",
          "allow_from": ["123456789"]
        }
      },

      "workspace": "~/.nanobot/workspaces/health-bot",

      "agent": {
        "model": "zai/glm-4.7",
        "temperature": 0.7
      },

      "mcps": ["mem0", "exa-search"]
    },
    {
      "id": "finance-bot",
      "name": "Finance Bot",
      "description": "Assistente especializado em finanças pessoais",

      "channels": {
        "telegram": {
          "enabled": true,
          "token": "BOT_TOKEN_2",
          "allow_from": ["123456789"]
        }
      },

      "workspace": "~/.nanobot/workspaces/finance-bot",

      "agent": {
        "model": "zai/glm-4.7-flash",
        "temperature": 0.5
      },

      "mcps": ["mem0", "exa-search"]
    }
  ]
}
```

### 2. MCP Configuration (`~/.nanobot/mcp.json`)

Global MCP server definitions (shared across bots):

```json
{
  "mcps": [
    {
      "name": "mem0",
      "type": "http",
      "description": "Self-hosted multi-tenant memory system (default)",

      "config": {
        "url": "http://localhost:8000",
        "env": {
          "MEM0_API_KEY": "optional-key"
        }
      },

      "health_check": {
        "endpoint": "/v1/health",
        "expected_status": 200
      }
    },
    {
      "name": "exa-search",
      "type": "command",
      "description": "Web search via Exa AI",

      "config": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-exa"],
        "env": {
          "EXA_API_KEY": "your-api-key"
        }
      },

      "health_check": {
        "command_timeout": 5
      }
    },
    {
      "name": "filesystem",
      "type": "command",
      "description": "File system operations",

      "config": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
      },

      "health_check": {
        "command_timeout": 3
      }
    }
  ]
}
```

### 3. Workspace Structure

Each bot has its own workspace:

```
~/.nanobot/workspaces/
├── health-bot/
│   ├── SOUL.md              # Personality
│   ├── AGENTS.md            # Instructions
│   ├── USER.md              # User info
│   ├── TOOLS.md             # Tools doc
│   ├── memory/
│   │   ├── MEMORY.md        # Long-term memory
│   │   └── 2026-02-03.md    # Daily notes
│   ├── skills/              # Custom skills
│   │   └── health-tips/
│   │       └── SKILL.md
│   └── HEARTBEAT.md         # Periodic tasks
│
└── finance-bot/
    ├── SOUL.md              # Different personality
    ├── AGENTS.md
    ├── USER.md
    ├── TOOLS.md
    ├── memory/
    ├── skills/
    └── HEARTBEAT.md
```

### 4. Memory Isolation with Mem0

**Mem0** provides multi-user memory isolation through the `user_id` parameter, enabling bot-specific memory without workspace isolation.

**How it works:**
- Each bot uses a unique `user_id` when calling Mem0
- Memories are automatically isolated per `user_id` at the database level
- Each bot can only access its own memories
- No memory "leakage" between bots

**Example usage:**
```python
from nanobot.memory import Mem0Client

# Health bot memories
client = Mem0Client(server_url="http://localhost:8000")
await client.store_memory(
    user_id="health-bot",
    content="User prefers swimming for exercise",
    metadata={"category": "fitness"}
)

# Finance bot memories (separate from health bot)
await client.store_memory(
    user_id="finance-bot",
    content="User invests in index funds",
    metadata={"category": "investments"}
)

# Each bot only sees its own memories
health_memories = await client.search_memories(
    user_id="health-bot",
    query="exercise"
)
# Returns only health-bot memories

finance_memories = await client.search_memories(
    user_id="finance-bot",
    query="investments"
)
# Returns only finance-bot memories
```

**Benefits:**
- ✅ **Database-level isolation** - No cross-bot memory access
- ✅ **Simple API** - Just pass `user_id` parameter
- ✅ **Self-hosted** - No external dependencies
- ✅ **Scalable** - Add unlimited bots with unique `user_id` values
- ✅ **Semantic search** - Find memories by meaning, not just keywords

## Architecture Components

### 1. BotConfig Schema

```python
class BotConfig(BaseModel):
    """Configuration for a single bot instance."""

    id: str
    name: str
    description: str = ""

    # Channels per bot
    channels: ChannelConfig

    # Workspace path
    workspace: str

    # Agent settings
    agent: AgentDefaults

    # MCP servers to enable
    mcps: list[str] = Field(default_factory=list)
```

### 2. MultiBotManager

```python
class MultiBotManager:
    """Manages multiple bot instances."""

    def __init__(self, bots_config: list[BotConfig], mcp_config: MCPConfig):
        self.bots: dict[str, BotInstance] = {}
        self.mcps: dict[str, MCPServer] = {}

        # Initialize MCPs
        self._init_mcps(mcp_config)

        # Initialize bots
        for bot_cfg in bots_config:
            self.bots[bot_cfg.id] = BotInstance(bot_cfg, self.mcps)

    async def start_all(self):
        """Start all enabled bots."""
        for bot in self.bots.values():
            await bot.start()

    async def stop_all(self):
        """Stop all bots."""
        for bot in self.bots.values():
            await bot.stop()
```

### 3. BotInstance

```python
class BotInstance:
    """Single bot instance with isolated context."""

    def __init__(self, config: BotConfig, available_mcps: dict):
        self.config = config
        self.workspace = Path(config.workspace).expanduser()

        # Create workspace if not exists
        self._init_workspace()

        # Initialize ContextBuilder with bot's workspace
        self.context = ContextBuilder(self.workspace)

        # Initialize enabled MCPs for this bot
        self.mcps = self._init_mcps(available_mcps)

        # Initialize channels
        self.channels = self._init_channels()

    def _init_workspace(self):
        """Create workspace structure with default files."""
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Create default SOUL.md if not exists
        soul_file = self.workspace / "SOUL.md"
        if not soul_file.exists():
            soul_file.write_text(f"""# Soul

Eu sou {self.config.name}.

{self.config.description}

## Personalidade

- Útil e amigável
- Conciso e direto
- Especialista no meu domínio
""")
```

### 4. MCP Manager

```python
class MCPManager:
    """Manages MCP servers lifecycle."""

    def __init__(self, config: MCPConfig):
        self.config = config
        self.servers: dict[str, MCPServer] = {}

    async def start_all(self):
        """Start all configured MCP servers."""
        for mcp_cfg in self.config.mcps:
            self.servers[mcp_cfg.name] = await self._start_mcp(mcp_cfg)

    async def check_health(self) -> dict[str, bool]:
        """Check health of all MCP servers."""
        status = {}
        for name, server in self.servers.items():
            status[name] = await server.is_healthy()
        return status

    def get_status(self) -> dict[str, dict]:
        """Get detailed status of all MCPs."""
        return {
            name: {
                "type": server.config.type,
                "enabled": True,
                "healthy": await server.is_healthy(),
                "config": server.config.config
            }
            for name, server in self.servers.items()
        }
```

## Migration Path

### Phase 1: Backward Compatibility

- Keep existing single-bot config working
- Add `bots.json` as optional override
- If `bots.json` exists, use multi-bot mode
- Otherwise, use legacy single-bot mode

### Phase 2: Migration Tool

```bash
nanobot migrate-to-multi-bot
```

Creates `bots.json` from existing config:
- Converts `~/.nanobot/config.json` → `~/.nanobot/bots.json`
- Creates default workspace
- Copies existing SOUL.md, AGENTS.md, etc.

### Phase 3: Deprecate Legacy Config

- Warn users to migrate
- Keep legacy mode for 2-3 versions
- Eventually remove legacy mode

## Example: Adding a New Bot

```bash
# 1. Create workspace
mkdir -p ~/.nanobot/workspaces/cooking-bot

# 2. Create personality
cat > ~/.nanobot/workspaces/cooking-bot/SOUL.md << 'EOF'
# Chef Bot 🧑‍🍳

Eu sou Chef Bot, seu assistente de culinária.

## Personalidade

- Apaixonado por gastronomia
- Detalhista em receitas
- Criativo com ingredientes
EOF

# 3. Add to bots.json
nano ~/.nanobot/bots.json
```

```json
{
  "id": "cooking-bot",
  "name": "Chef Bot",
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allow_from": ["123456789"]
    }
  },
  "workspace": "~/.nanobot/workspaces/cooking-bot",
  "mcps": ["exa-search", "mem0"]
}
```

```bash
# 4. Restart nanobot
nanobot gateway
```

## Benefits

✅ **Isolation**: Each bot has separate personality, memory, and MCPs
✅ **Simplicity**: JSON config, no code changes needed
✅ **Scalability**: Add/remove bots without touching code
✅ **Flexibility**: Different models, temps, MCPs per bot
✅ **Backward Compatible**: Existing single-bot setup still works
