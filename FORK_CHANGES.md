# Fork Changes & Improvements

This fork of [HKUDS/nanobot](https://github.com/HKUDS/nanobot) includes additional features, bug fixes, and deployment configurations. Below is a comprehensive list of changes.

## 🆕 New Features

### 1. Mem0 Integration 🧠 (Default Memory System)
Self-hosted, multi-tenant memory system with persistent storage and semantic search.

**Why it matters:**
- **Self-hosted**: No external dependencies or API limits
- **Multi-user isolation**: Each user has separate memory space
- **Semantic search**: Find memories by meaning, not just keywords
- **Open source**: MIT license (no vendor lock-in)
- **Cost**: Free when self-hosted

**Features:**
- ✅ Persistent memory across sessions
- ✅ Multi-tenant architecture (user_id-based isolation)
- ✅ Semantic search with scoring
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Backward compatible with Supermemory API

**Quick Start:**
```bash
# Mem0 is included by default in docker-compose.yml
docker-compose up -d

# Verify Mem0 is running
curl http://localhost:8000/v1/health
```

**Environment Variables:**
```bash
MEM0_URL=http://mem0:8000          # Docker (internal)
MEM0_URL=http://localhost:8000     # Manual (external)
MEM0_API_KEY=                      # Optional
```

**API Usage:**
```python
from nanobot.memory import Mem0Client

client = Mem0Client(server_url="http://localhost:8000")
await client.store_memory(user_id="user123", content="User loves Python")
memories = await client.search_memories(user_id="user123", query="Python")
await client.close()
```

**Documentation:**
- [README_MEM0.md](./README_MEM0.md) - User documentation and API reference
- [TESTING_MEM0.md](./TESTING_MEM0.md) - Testing guide
- [DEPLOYMENT_MEM0_STRATEGY.md](./DEPLOYMENT_MEM0_STRATEGY.md) - Deployment guide
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Migration from Supermemory

**Implementation:**
- `nanobot/memory/mem0_client.py` - Async HTTP client (277 lines)
- `tests/test_mem0_integration.py` - Unit tests (266 lines, 6/6 passing)
- `tests/test_mem0_live.py` - Integration tests (328 lines)
- Backward compatibility aliases: `SupermemoryMCPClient = Mem0Client`

**Files Added:**
- `nanobot/memory/mem0_client.py` - Core Mem0 client implementation
- `nanobot/memory/__init__.py` - Updated exports
- `docker-compose.mem0.yml` - Full stack with PostgreSQL
- `pytest.ini` - CI/CD configuration with test markers
- `README_MEM0.md` - User documentation (320 lines)
- `TESTING_MEM0.md` - Testing guide (313 lines)
- `DEPLOYMENT_MEM0_STRATEGY.md` - Deployment strategy (212 lines)
- `MIGRATION_GUIDE.md` - Migration guide

### 2. Z.AI / Zhipu AI Provider Support ⭐
Native integration with Z.AI (Zhipu AI) for cost-efficient GLM model access.

**Why it matters:**
- **Cost**: $0.11/M tokens (input) vs $0.40/M through OpenRouter (~4x cheaper)
- **Performance**: Direct API access eliminates OpenRouter latency overhead (~300-400ms saved)
- **Z.AI Coding Plan**: $3/month for 180M tokens + 200K context cache

**Configuration:**
```json
{
  "providers": {
    "zai": {
      "apiKey": "z-xxxxxxxxxxxxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "zai/glm-4.7"
    }
  }
}
```

**Supported models:**
- `zai/glm-4.7` - High-end reasoning model (recommended)
- `zai/glm-4.7-flash` - Faster, cheaper alternative
- `zai/glm-4.7-air` - Ultra-fast for simple tasks
- Legacy `zhipu/*` prefix also supported for backward compatibility

**Implementation:**
- Modified `nanobot/config/schema.py` to add `zai` provider
- Enhanced `nanobot/providers/litellm_provider.py` with Z.AI detection logic
- Auto-sets `ZAI_API_KEY` environment variable for LiteLLM
- Auto-adds `zai/` prefix to GLM models if not present

### 2. Docker Deployment for Dokploy 🐳
Complete Docker deployment configuration optimized for Dokploy.

**Files added:**
- `docker-compose.yml` - Production-ready orchestration
  - Health checks (`/health` endpoint)
  - Resource limits (4GB RAM, 2 CPU cores)
  - Volume mounts for config persistence
  - Port 18790:18790 mapping
  - Default command: `nanobot gateway`

- `.env.example` - Environment variables template
- `DOKPLOY.md` - Complete deployment guide (500+ lines)
- `README-DOKPLOY.md` - Quick start instructions
- `test-build.sh` - Local testing script

**Quick Start:**
```bash
# Clone this fork
git clone https://github.com/renatocaliari/nanobot.git
cd nanobot

# Build and test locally
./test-build.sh

# Or use docker-compose
docker-compose up -d
```

**Dokploy Deployment:**
1. Set environment variables:
   ```env
   NANOBOT_PROVIDERS__ZAI__API_KEY=z-xxxxxxxxxxxxx
   NANOBOT_DEFAULT_MODEL=zai/glm-4.7
   ```
2. Configure repository to use `claude/add-dockerfile-uv-1i3Kt` branch
3. Build and deploy

See [DOKPLOY.md](./DOKPLOY.md) for detailed instructions.

### 3. Multi-Bot System with Isolated Workspaces 🤖
Run multiple Telegram bots simultaneously, each with its own personality, workspace, and MCP servers.

**Why it matters:**
- **Specialization**: Create bots for different domains (health, finance, cooking, etc.)
- **Isolation**: Each bot has separate memory, files, and personality
- **No Code**: Configure everything via JSON - no coding required
- **MCP Selection**: Each bot uses only the MCPs it needs

**Configuration (`~/.nanobot/bots.json`):**
```json
{
  "bots": [
    {
      "id": "health-bot",
      "name": "Dr. Bot Saúde",
      "description": "Assistente especializado em saúde",
      "channels": {
        "telegram_enabled": true,
        "telegram_token": "BOT_TOKEN_1",
        "telegram_allow_from": ["123456789"]
      },
      "workspace": "~/.nanobot/workspaces/health-bot",
      "agent": {
        "model": "zai/glm-4.7",
        "temperature": 0.7
      },
      "mcps": ["supermemory", "exa-search"]
    },
    {
      "id": "finance-bot",
      "name": "Finance Bot",
      "description": "Assistente especializado em finanças",
      "workspace": "~/.nanobot/workspaces/finance-bot",
      "mcps": ["exa-search"]
    }
  ]
}
```

**Key Features:**
- ✅ Separate `SOUL.md` per bot (unique personality)
- ✅ Isolated workspaces (memory, files, skills)
- ✅ Per-bot MCP selection
- ✅ Different models, temperatures, settings per bot
- ✅ CLI commands: `nanobot multibot start`, `nanobot multibot status`

**Documentation:**
- [MULTI_BOT_DESIGN.md](./MULTI_BOT_DESIGN.md) - Architecture details
- [MULTI_BOT_COMPLETE.md](./MULTI_BOT_COMPLETE.md) - Complete usage guide
- [bots.json.example](./bots.json.example) - Configuration example

### 4. MCP JSON Configuration System
Configure MCP servers via JSON (like RooCode/OpenCode), without writing code.

**Configuration (`~/.nanobot/bots.json` - MCPs section):**
```json
{
  "mcps": {
    "mcps": [
      {
        "name": "supermemory",
        "type": "http",
        "url": "http://localhost:3000"
      },
      {
        "name": "exa-search",
        "type": "command",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-exa"],
        "env": {
          "EXA_API_KEY": "your-key"
        }
      }
    ]
  }
}
```

**Supported Types:**
- `command` - MCPs running as subprocesses (npx, python, etc.)
- `http` - MCPs with REST API (Supermemory cloud, etc.)

**Documentation:**
- [MCP_CONFIG.md](./MCP_CONFIG.md) - MCP configuration guide

### 5. MCP Status Checker
Check which MCP servers are configured and active.

**Usage:**
```
User: "Quais MCPs estão ativos?"
User: "Status dos servidores MCP"
```

**Response:**
```
# 📊 MCP Servers Status

## Configurados: 2

### 1. Supermemory ✅
- **Tipo**: HTTP
- **URL**: http://localhost:3000
- **Status**: Respondendo

### 2. Exa Search ❌
- **Tipo**: Command
- **Status**: Processo não encontrado
```

**Implementation:**
- Skill: `workspace/skills/mcp-status/SKILL.md`
- Tool: `nanobot/agent/tools/mcp_status.py`

### 6. Gemini Provider Support
Added Google Gemini as a first-class provider.

**Configuration:**
```json
{
  "providers": {
    "gemini": {
      "apiKey": "AIza..."
    }
  },
  "agents": {
    "defaults": {
      "model": "gemini/gemini-2.0-flash-exp"
    }
  }
}
```

### 4. Tool Parameter Validation 🔒
JSON-schema validation for tool parameters to catch errors early.

**Implementation:**
- Added `jsonschema>=4.0.0` dependency
- Modified `nanobot/agent/tools/base.py`:
  - `validate_params(params)` - Validates against tool's JSON schema
  - `execute_safe(**kwargs)` - Validates before execution with clear error messages

**Benefits:**
- Catches missing required parameters
- Validates parameter types (string, number, boolean, etc.)
- Checks value ranges (e.g., `minimum: 1`, `maximum: 100`)
- Provides clear error messages for debugging

**Example:**
```python
# Before: Silent failures or cryptic errors
tool.execute(param="wrong_type")

# After: Clear validation messages
❌ ValidationError: 'max_results' must be <integer>, but got <str '10'>
```

### 5. Environment Variables Standardization
All environment variables now use Pydantic Settings pattern for consistency.

**Pattern:**
- Prefix: `NANOBOT_`
- Nested delimiter: `__` (double underscore)
- Example: `providers.zai.apiKey` → `NANOBOT_PROVIDERS__ZAI__API_KEY`

**Benefits:**
- Consistent naming across all providers
- Works seamlessly with Docker/Kubernetes
- Type-safe with Pydantic validation

**Migration Guide:**

| Old | New |
|-----|-----|
| `OPENROUTER_API_KEY` | `NANOBOT_PROVIDERS__OPENROUTER__API_KEY` |
| `ANTHROPIC_API_KEY` | `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY` |
| `ZAI_API_KEY` | `NANOBOT_PROVIDERS__ZAI__API_KEY` |
| `TELEGRAM_BOT_TOKEN` | `NANOBOT_CHANNELS__TELEGRAM__TOKEN` |

### 6. Scheduled Reminders & Supermemory ⏰
Integrated features from `feature/docker-supermemory` branch.

**Scheduled Reminders:**
- Cron-based task scheduling
- Persistent reminder storage
- Natural language time parsing

**Supermemory:**
- Optional MCP (Model Context Protocol) client integration
- External memory service support
- Made memory an optional dependency (not required for core functionality)

### 7. Multi-Bot System with Isolated Workspaces 🤖
Run multiple Telegram bots simultaneously, each with its own personality, workspace, and MCP servers.

**Why it matters:**
- **Specialization**: Create bots for different domains (health, finance, cooking, etc.)
- **Isolation**: Each bot has separate memory, files, and personality
- **No Code**: Configure everything via JSON - no coding required
- **MCP Selection**: Each bot uses only the MCPs it needs

**Configuration (`~/.nanobot/bots.json`):**
```json
{
  "bots": [
    {
      "id": "health-bot",
      "name": "Dr. Bot Saúde",
      "channels": {
        "telegram_enabled": true,
        "telegram_token": "BOT_TOKEN_1"
      },
      "workspace": "~/.nanobot/workspaces/health-bot",
      "mcps": ["supermemory"]
    },
    {
      "id": "finance-bot",
      "name": "Finance Bot",
      "workspace": "~/.nanobot/workspaces/finance-bot",
      "mcps": ["exa-search"]
    }
  ]
}
```

**Key Features:**
- ✅ Separate `SOUL.md` per bot (unique personality)
- ✅ Isolated workspaces (memory, files, skills)
- ✅ Per-bot MCP selection
- ✅ CLI: `nanobot multibot start`, `nanobot multibot status`

**Implementation:**
- `nanobot/multibot/` - Multi-bot runtime system
- `nanobot/config/multibot.py` - Configuration schema
- `nanobot/cli/multibot.py` - CLI commands

### 8. MCP JSON Configuration System
Configure MCP servers via JSON (like RooCode/OpenCode), without writing code.

**Features:**
- `command` type - MCPs running as subprocesses
- `http` type - MCPs with REST API
- Per-bot MCP selection
- Environment variable support

### 9. MCP Status Checker
Check which MCP servers are configured and active.

**Usage:** Ask your nanobot "Quais MCPs estão ativos?"

**Implementation:**
- Skill: `workspace/skills/mcp-status/SKILL.md`
- Tool: `nanobot/agent/tools/mcp_status.py`

---

## 🐛 Bug Fixes

### 1. Heartbeat Token Comparison (commit `e1e3575`)
**File:** `nanobot/heartbeat/service.py` line 118

**Problem:**
```python
# Before: Never matched!
HEARTBEAT_OK_TOKEN = "HEARTBEAT_OK"
response.upper().replace("_", "")  # Returns "HEARTBEATOOK"
```

**Fix:**
```python
# After: Both sides remove underscores
HEARTBEAT_OK_TOKEN.replace("_", "") == response.upper().replace("_", "")
```

**Impact:** Heartbeat service now correctly detects successful responses.

### 2. Web Fetch Security (commit `470ee2e`)
**File:** `nanobot/agent/tools/web.py`

**Added:**
- `MAX_REDIRECTS = 5` constant to prevent redirect DoS attacks
- `_validate_url()` function:
  - Only allows `http://` and `https://` schemes
  - Blocks `file://`, `ftp://`, `javascript:`, `data:` URLs
  - Validates domain presence
- Configured `httpx.AsyncClient(max_redirects=MAX_REDIRECTS)`

**Impact:** Prevents security vulnerabilities when fetching web content.

### 3. CLI Display Issues (commit `c060ff0`)
**File:** `nanobot/cli/commands.py`

**Fixes:**
- **channels_status command:**
  - Added Telegram channel display
  - Shows enabled/disabled status
  - Displays token (first 10 chars) or "not configured"
  - Renamed "Bridge URL" column to "Configuration"

- **status command:**
  - Fixed to use `config.workspace_path` when config exists
  - Previously always showed default (`~/.nanobot/workspace`)
  - Added Z.AI API key display

**Impact:** CLI now shows accurate configuration information.

### 4. API Key Error Message (commit `bae9a73`)
**File:** `nanobot/cli/commands.py`

**Before:**
```
Error: No API key configured.
Set OPENROUTER_API_KEY or configure in ~/.nanobot/config.json
```

**After:**
```
Error: No API key configured.
Set one in ~/.nanobot/config.json or environment variables:
- providers.zai.apiKey (Z.AI/Zhipu AI)
- providers.openrouter.apiKey (OpenRouter)
- providers.anthropic.apiKey (Anthropic)
- providers.openai.apiKey (OpenAI)
- providers.gemini.apiKey (Google Gemini)
- providers.vllm.apiKey (local models)
```

**Impact:** Users see all available provider options.

### 5. ToolsConfig Default Factory (commit `a753fbb`)
**File:** `nanobot/config/schema.py` line 98

**Problem:**
```python
# Before: Wrong class
tools: WebToolsConfig = Field(default_factory=WebToolsConfig)
```

**Fix:**
```python
# After: Correct class
tools: ToolsConfig = Field(default_factory=ToolsConfig)
```

**Impact:** Configuration now correctly initializes all tool settings.

### 6. Telegram Polling Conflict Error Handler (commit `7333bf8`)
**File:** `nanobot/channels/telegram.py`

**Problem:**
```
telegram.error.Conflict: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

This error appears repeatedly in logs during:
- Overlapping deployments (old + new container)
- Internal retry/reconnection logic
- Webhook cleanup issues

**Fix:**
```python
# Added error handler to catch and suppress Conflict errors
from telegram.error import Conflict

async def _error_handler(self, update, context):
    """Handle errors from the Telegram bot."""
    if isinstance(context.error, Conflict):
        logger.warning("Telegram polling conflict detected (this is normal during overlapping deployments)")
        return
    logger.error(f"Telegram error: {context.error}")

# Registered in start() method
self._app.add_error_handler(self._error_handler)
```

**Impact:** Conflict errors now logged as warnings instead of errors, reducing log spam. Bot continues to function normally - only logging affected.

---

## 📋 Complete File Changes

### Modified Files:
- `nanobot/config/schema.py` - Added zai/gemini providers, fixed ToolsConfig
- `nanobot/providers/litellm_provider.py` - Added Z.AI detection and setup
- `nanobot/cli/commands.py` - Fixed error messages, added Telegram display
- `nanobot/heartbeat/service.py` - Fixed token comparison
- `nanobot/agent/tools/web.py` - Added URL validation and redirect limits
- `nanobot/agent/tools/base.py` - Added parameter validation
- `nanobot/channels/telegram.py` - Added polling conflict error handler
- `pyproject.toml` - Added jsonschema dependency

### New Files:
- `docker-compose.yml` - Production-ready orchestration (includes Mem0)
- `docker-compose.mem0.yml` - Full stack with PostgreSQL
- `test-build.sh`
- `DOKPLOY.md`
- `README-DOKPLOY.md`
- `FORK_CHANGES.md` (this file)
- `README_MEM0.md` - Mem0 user documentation (320 lines)
- `TESTING_MEM0.md` - Testing guide (313 lines)
- `DEPLOYMENT_MEM0_STRATEGY.md` - Deployment strategy (212 lines)
- `MIGRATION_GUIDE.md` - Migration guide
- `pytest.ini` - CI/CD configuration
- `tests/__init__.py`
- `tests/test_tool_validation.py`
- `tests/test_mem0_integration.py` - Mem0 unit tests (266 lines, 6/6 passing)
- `tests/test_mem0_live.py` - Mem0 integration tests (328 lines)
- `nanobot/memory/__init__.py` - Updated exports
- `nanobot/memory/mem0_client.py` - Mem0 HTTP client (277 lines)
- `nanobot/memory/config.py`
- `nanobot/memory/mcp_client.py`
- `nanobot/memory/README.md`
- `nanobot/multibot/__init__.py`
- `nanobot/multibot/bot_instance.py`
- `nanobot/multibot/manager.py`
- `nanobot/multibot/telegram_channel.py`
- `nanobot/config/multibot.py`
- `nanobot/cli/multibot.py`
- `nanobot/agent/tools/mcp_status.py`
- `workspace/skills/mcp-status/SKILL.md`
- `MULTI_BOT_DESIGN.md`
- `MULTI_BOT_COMPLETE.md`
- `MCP_CONFIG.md`
- `bots.json.example`

---

## 🚀 Deployment Guide

### Prerequisites
- Docker and Docker Compose installed
- Z.AI API key (get yours at [z.com](https://z.com))
- Dokploy instance (or any Docker-compatible platform)

### Quick Start (Docker Compose)
```bash
# Clone this fork
git clone https://github.com/renatocaliari/nanobot.git
cd nanobot

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f nanobot
```

### Dokploy Deployment
See [DOKPLOY.md](./DOKPLOY.md) for complete deployment guide.

**Key Environment Variables:**
```env
NANOBOT_PROVIDERS__ZAI__API_KEY=z-xxxxxxxxxxxxx
NANOBOT_DEFAULT_MODEL=zai/glm-4.7
NANOBOT_CHANNELS__TELEGRAM__TOKEN=your_bot_token
NANOBOT_CHANNELS__TELEGRAM__ALLOW_FROM=["123456789"]
```

---

## 🔄 Keeping Your Fork Updated

This fork aims to stay in sync with upstream [HKUDS/nanobot](https://github.com/HKUDS/nanobot). To update:

```bash
git remote add upstream https://github.com/HKUDS/nanobot.git
git fetch upstream
git rebase upstream/main
```

If you encounter conflicts during rebase, please open an issue.

---

## 📊 Comparison with Upstream

 | Feature | Upstream | This Fork |
 |---------|----------|-----------|
 | Mem0 Integration | ❌ | ✅ (Default) |
 | Z.AI Provider | ❌ | ✅ |
 | Dokploy Deployment | ❌ | ✅ |
 | Docker Compose | Basic | Production-ready |
 | Gemini Provider | ❌ | ✅ |
 | Tool Validation | ❌ | ✅ |
 | Env Var Pattern | Mixed | Standardized |
 | Web Fetch Security | ⚠️ Limited | ✅ Enhanced |
 | CLI Display | ⚠️ Partial | ✅ Complete |
 | Multi-Bot System | ❌ | ✅ |
 | MCP JSON Config | ❌ | ✅ |
 | MCP Status Checker | ❌ | ✅ |
 | Bug Fixes | - | ✅ 6 fixes |

---

## 🤝 Contributing

Contributions welcome! Please:

1. Check existing issues before creating new ones
2. Include tests for new features
3. Follow the existing code style
4. Update documentation as needed

---

## 📝 License

This fork maintains the same MIT license as the original [HKUDS/nanobot](https://github.com/HKUDS/nanobot) project.

---

## 🙏 Acknowledgments

- Original [HKUDS/nanobot](https://github.com/HKUDS/nanobot) project
- [Z.AI](https://z.com) for affordable GLM model access
- [LiteLLM](https://github.com/BerriAI/litellm) for unified LLM API
- All contributors to the original project
