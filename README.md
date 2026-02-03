<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="500">
  <h1>nanobot: Ultra-Lightweight Personal AI Assistant</h1>
  <p>
    <a href="https://github.com/HKUDS/nanobot"><img src="https://img.shields.io/badge/fork-of-HKUDS%2Fnanobot-blue" alt="Fork"></a>
    <a href="https://pypi.org/project/nanobot-ai/"><img src="https://img.shields.io/pypi/v/nanobot-ai" alt="PyPI"></a>
    <a href="https://pepy.tech/project/nanobot-ai"><img src="https://static.pepy.tech/badge/nanobot-ai" alt="Downloads"></a>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/Feishu-Group-E9DBFC?style=flat&logo=feishu&logoColor=white" alt="Feishu"></a>
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/WeChat-Group-C5EAB4?style=flat&logo=wechat&logoColor=white" alt="WeChat"></a>
  </p>
</div>

> **📌 This is a fork of [HKUDS/nanobot](https://github.com/HKUDS/nanobot) with additional features and improvements. See [FORK_CHANGES.md](./FORK_CHANGES.md) for details.**

🐈 **nanobot** is an **ultra-lightweight** personal AI assistant inspired by [Clawdbot](https://github.com/openclaw/openclaw) 

⚡️ Delivers core agent functionality in just **~4,000** lines of code — **99% smaller** than Clawdbot's 430k+ lines.

## 📢 News

- **2025-02-03** 🧠 **Mem0 integration** - Self-hosted multi-tenant memory system (default)
- **2025-02-02** 🐳 Docker deployment support added! Deploy to Dokploy in minutes. See [DOKPLOY.md](./DOKPLOY.md)
- **2025-02-02** ⭐ Z.AI provider support for cost-efficient GLM models ($0.11/M tokens)
- **2025-02-01** 🎉 nanobot launched! Welcome to try 🐈 nanobot!

## Key Features of nanobot:

🪶 **Ultra-Lightweight**: Just ~4,000 lines of code — 99% smaller than Clawdbot - core functionality.

🔬 **Research-Ready**: Clean, readable code that's easy to understand, modify, and extend for research.

⚡️ **Lightning Fast**: Minimal footprint means faster startup, lower resource usage, and quicker iterations.

💎 **Easy-to-Use**: One-click to depoly and you're ready to go.

## 🏗️ Architecture

<p align="center">
  <img src="nanobot_arch.png" alt="nanobot architecture" width="800">
</p>

## ✨ Features

**🧠 Persistent Memory with Mem0**

This fork includes **Mem0** - a self-hosted, multi-tenant memory system that enables nanobot to remember important information across conversations.

**Key Features:**
- ✅ **Self-hosted** - No external dependencies or API limits
- ✅ **Multi-user isolation** - Each user has separate memory space
- ✅ **Semantic search** - Find memories by meaning, not just keywords
- ✅ **Automatic management** - Store, retrieve, and organize memories seamlessly

**Usage:**
Mem0 is automatically enabled when using Docker Compose. Memories are stored per user and persist across sessions.

See [README_MEM0.md](./README_MEM0.md) for complete API documentation and usage examples.

---

<table align="center">
  <tr align="center">
    <th><p align="center">📈 24/7 Real-Time Market Analysis</p></th>
    <th><p align="center">🚀 Full-Stack Software Engineer</p></th>
    <th><p align="center">📅 Smart Daily Routine Manager</p></th>
    <th><p align="center">📚 Personal Knowledge Assistant</p></th>
  </tr>
  <tr>
    <td align="center"><p align="center"><img src="case/search.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/code.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/scedule.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/memory.gif" width="180" height="400"></p></td>
  </tr>
  <tr>
    <td align="center">Discovery • Insights • Trends</td>
    <td align="center">Develop • Deploy • Scale</td>
    <td align="center">Schedule • Automate • Organize</td>
    <td align="center">Learn • Memory • Reasoning</td>
  </tr>
</table>

## 📦 Install

**Install from PyPi**

```bash
pip install nanobot-ai
```

**Install from source** (recommended for development)

```bash
# Upstream (original project)
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
pip install -e .

# This fork (includes Z.AI, Dokploy, bug fixes)
git clone https://github.com/renatocaliari/nanobot.git
cd nanobot
pip install -e .
```

**Install with uv**

```bash
uv venv
source .venv/bin/activate
uv pip install nanobot-ai
```

## 🚀 Quick Start

> [!TIP]
> Set your API key in `~/.nanobot/config.json`.
> Get API keys: [Z.AI](https://z.com) (GLM models, $0.11/M tokens) · [OpenRouter](https://openrouter.ai/keys) (LLM) · [Brave Search](https://brave.com/search/api/) (optional, for web search)
> This fork includes Z.AI provider support for cost-efficient GLM model access. See [FORK_CHANGES.md](./FORK_CHANGES.md) for details.

**1. Initialize**

```bash
nanobot onboard
```

**2. Configure** (`~/.nanobot/config.json`)

**Option A: Z.AI (Recommended - Cost Efficient)**
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
  },
  "tools": {
    "web": {
      "search": {
        "apiKey": "BSA-xxx"
      }
    }
  }
}
```

**Option B: OpenRouter**
```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  },
  "tools": {
    "web": {
      "search": {
        "apiKey": "BSA-xxx"
      }
    }
  }
}
```


**3. Chat**

```bash
nanobot agent -m "What is 2+2?"
```

That's it! You have a working AI assistant in 2 minutes.

## 🐳 Docker & Deployment

### Docker Compose (Recommended)

The Docker Compose configuration includes **Mem0 memory service** by default for persistent, multi-tenant memory storage.

```bash
# Clone this fork
git clone https://github.com/renatocaliari/nanobot.git
cd nanobot

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env

# Start services (includes Mem0)
docker-compose up -d

# Check logs
docker-compose logs -f nanobot

# Verify Mem0 is running
curl http://localhost:8000/v1/health
```

**Services included:**
- `nanobot` - Main AI assistant service
- `mem0` - Self-hosted memory system (port 8000)

**Environment variables for Mem0:**
```bash
# Optional: Mem0 API key (if your Mem0 instance requires it)
MEM0_API_KEY=your-api-key

# Optional: Custom Mem0 URL (default: http://mem0:8000)
MEM0_URL=http://mem0:8000
```

### Docker

```bash
docker build -t nanobot .
docker run --rm nanobot onboard
docker run -v ~/.nanobot:/root/.nanobot -p 18790:18790 nanobot
```

Mount `~/.nanobot` so your config and workspace persist across runs. Edit `~/.nanobot/config.json` on the host to add API keys, then restart the container.

### Dokploy Deployment

This fork includes optimized Docker configuration for Dokploy deployment. See [DOKPLOY.md](./DOKPLOY.md) for complete guide.

**Quick setup:**
1. Set environment variables in Dokploy:
   ```env
   NANOBOT_PROVIDERS__ZAI__API_KEY=z-xxxxxxxxxxxxx
   NANOBOT_DEFAULT_MODEL=zai/glm-4.7
   ```
2. Build and deploy using `docker-compose.yml`
3. Access at `http://your-domain:18790`

## 🖥️ Local Models (vLLM)

Run nanobot with your own local models using vLLM or any OpenAI-compatible server.

**1. Start your vLLM server**

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --port 8000
```

**2. Configure** (`~/.nanobot/config.json`)

```json
{
  "providers": {
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://localhost:8000/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "meta-llama/Llama-3.1-8B-Instruct"
    }
  }
}
```

**3. Chat**

```bash
nanobot agent -m "Hello from my local LLM!"
```

> [!TIP]
> The `apiKey` can be any non-empty string for local servers that don't require authentication.

## 💬 Chat Apps

Talk to your nanobot through Telegram or WhatsApp — anytime, anywhere.

| Channel | Setup |
|---------|-------|
| **Telegram** | Easy (just a token) |
| **WhatsApp** | Medium (scan QR) |

<details>
<summary><b>Telegram</b> (Recommended)</summary>

**1. Create a bot**
- Open Telegram, search `@BotFather`
- Send `/newbot`, follow prompts
- Copy the token

**2. Configure**

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

> Get your user ID from `@userinfobot` on Telegram.

**3. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>WhatsApp</b></summary>

Requires **Node.js ≥18**.

**1. Link device**

```bash
nanobot channels login
# Scan QR with WhatsApp → Settings → Linked Devices
```

**2. Configure**

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**3. Run** (two terminals)

```bash
# Terminal 1
nanobot channels login

# Terminal 2
nanobot gateway
```

</details>

## ⚙️ Configuration

<details>
<summary><b>Full config example</b></summary>

```json
{
  "agents": {
    "defaults": {
      "model": "zai/glm-4.7"
    }
  },
  "providers": {
    "zai": {
      "apiKey": "z-xxxxxxxxxxxxx"
    },
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    },
    "anthropic": {
      "apiKey": "sk-ant-xxx"
    },
    "openai": {
      "apiKey": "sk-xxx"
    },
    "gemini": {
      "apiKey": "AIza..."
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "123456:ABC...",
      "allowFrom": ["123456789"]
    },
    "whatsapp": {
      "enabled": false
    }
  },
  "tools": {
    "web": {
      "search": {
        "apiKey": "BSA..."
      }
    }
  }
}
```

**Providers supported in this fork:**
- `zai` - Z.AI / Zhipu AI (GLM models, $0.11/M tokens) ⭐
- `openrouter` - OpenRouter (multi-provider)
- `anthropic` - Anthropic (Claude models)
- `openai` - OpenAI (GPT models)
- `gemini` - Google Gemini ⭐
- `vllm` - Local models via vLLM

</details>

## CLI Reference

| Command | Description |
|---------|-------------|
| `nanobot onboard` | Initialize config & workspace |
| `nanobot agent -m "..."` | Chat with the agent |
| `nanobot agent` | Interactive chat mode |
| `nanobot gateway` | Start the gateway |
| `nanobot status` | Show status |
| `nanobot channels login` | Link WhatsApp (scan QR) |
| `nanobot channels status` | Show channel status |

<details>
<summary><b>Scheduled Tasks (Cron)</b></summary>

```bash
# Add a job
nanobot cron add --name "daily" --message "Good morning!" --cron "0 9 * * *"
nanobot cron add --name "hourly" --message "Check status" --every 3600

# List jobs
nanobot cron list

# Remove a job
nanobot cron remove <job_id>
```

</details>

<details>
<summary><b>Memory Management</b></summary>

```bash
# List all memories
nanobot memory list --user user123

# Search memories
nanobot memory search --user user123 "Python programming"

# Export to backup
nanobot memory export --user user123 --output memories.json

# Import from backup
nanobot memory import --input memories.json --user user123

# Check Mem0 server health
nanobot memory health
```

</details>

## 📁 Project Structure

```
nanobot/
├── agent/          # 🧠 Core agent logic
│   ├── loop.py     #    Agent loop (LLM ↔ tool execution)
│   ├── context.py  #    Prompt builder
│   ├── memory.py   #    Persistent memory
│   ├── skills.py   #    Skills loader
│   ├── subagent.py #    Background task execution
│   └── tools/      #    Built-in tools (incl. spawn)
├── skills/         # 🎯 Bundled skills (github, weather, tmux...)
├── channels/       # 📱 WhatsApp integration
├── bus/            # 🚌 Message routing
├── cron/           # ⏰ Scheduled tasks
├── heartbeat/      # 💓 Proactive wake-up
├── providers/      # 🤖 LLM providers (OpenRouter, etc.)
├── session/        # 💬 Conversation sessions
├── config/         # ⚙️ Configuration
└── cli/            # 🖥️ Commands
```

## 🧪 Testing

### Mem0 Integration Tests

The nanobot fork includes comprehensive Mem0 integration testing:

```bash
# Unit tests (no server required)
pytest tests/test_mem0_integration.py -v

# Live integration tests (requires Mem0 server running)
docker run -d -p 8000:8000 mem0ai/mem0:latest
python tests/test_mem0_live.py

# Run only unit tests (CI/CD friendly)
pytest -m "not integration"

# Run all tests including integration
pytest -m ""
```

See [TESTING_MEM0.md](./TESTING_MEM0.md) for complete testing guide.

## 🤝 Contribute & Roadmap

### Fork Differences

This is a fork of [HKUDS/nanobot](https://github.com/HKUDS/nanobot) with additional features:

- 🧠 **Mem0 Integration** (Default) - Self-hosted multi-tenant memory system
- ⭐ **Z.AI Provider** - Cost-efficient GLM models ($0.11/M tokens)
- 🐳 **Dokploy Deployment** - Production-ready Docker configuration
- 🔒 **Security Fixes** - URL validation, redirect limits
- ✨ **Tool Validation** - JSON-schema parameter validation
- 🐛 **Bug Fixes** - Heartbeat, CLI display, error messages

See [FORK_CHANGES.md](./FORK_CHANGES.md) for complete list of changes and migration guide.

### Upstream Contribution

PRs welcome! The codebase is intentionally small and readable. 🤗

**Roadmap** — Pick an item and [open a PR](https://github.com/HKUDS/nanobot/pulls)!

- [ ] **Multi-modal** — See and hear (images, voice, video)
- [ ] **Long-term memory** — Never forget important context
- [ ] **Better reasoning** — Multi-step planning and reflection
- [ ] **More integrations** — Discord, Slack, email, calendar
- [ ] **Self-improvement** — Learn from feedback and mistakes

### Contributors

<a href="https://github.com/HKUDS/nanobot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/nanobot" />
</a>

---

## ⭐ Star History

<div align="center">
  <a href="https://star-history.com/#HKUDS/nanobot&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date" style="border-radius: 15px; box-shadow: 0 0 30px rgba(0, 217, 255, 0.3);" />
    </picture>
  </a>
</div>

<p align="center">
  <em> Thanks for visiting ✨ nanobot!</em><br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.nanobot&style=for-the-badge&color=00d4ff" alt="Views">
</p>
