# Fork Changes & Improvements

This fork of [HKUDS/nanobot](https://github.com/HKUDS/nanobot) includes additional features, bug fixes, and deployment configurations. Below is a comprehensive list of changes.

## 🆕 New Features

### 1. Z.AI / Zhipu AI Provider Support ⭐
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

### 3. Gemini Provider Support
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

---

## 📋 Complete File Changes

### Modified Files:
- `nanobot/config/schema.py` - Added zai/gemini providers, fixed ToolsConfig
- `nanobot/providers/litellm_provider.py` - Added Z.AI detection and setup
- `nanobot/cli/commands.py` - Fixed error messages, added Telegram display
- `nanobot/heartbeat/service.py` - Fixed token comparison
- `nanobot/agent/tools/web.py` - Added URL validation and redirect limits
- `nanobot/agent/tools/base.py` - Added parameter validation
- `pyproject.toml` - Added jsonschema dependency

### New Files:
- `docker-compose.yml`
- `test-build.sh`
- `DOKPLOY.md`
- `README-DOKPLOY.md`
- `FORK_CHANGES.md` (this file)
- `tests/__init__.py`
- `tests/test_tool_validation.py`
- `nanobot/memory/__init__.py`
- `nanobot/memory/config.py`
- `nanobot/memory/mcp_client.py`
- `nanobot/memory/README.md`

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
| Z.AI Provider | ❌ | ✅ |
| Dokploy Deployment | ❌ | ✅ |
| Docker Compose | Basic | Production-ready |
| Gemini Provider | ❌ | ✅ |
| Tool Validation | ❌ | ✅ |
| Env Var Pattern | Mixed | Standardized |
| Web Fetch Security | ⚠️ Limited | ✅ Enhanced |
| CLI Display | ⚠️ Partial | ✅ Complete |
| Bug Fixes | - | ✅ 5 fixes |

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
