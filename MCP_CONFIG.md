# MCP Configuration for Nanobot

This file defines all available MCP servers that can be used by your bots.

## MCP Server Types

### 1. HTTP-based MCPs
These MCPs expose a REST API (like Supermemory cloud):

```json
{
  "name": "supermemory",
  "type": "http",
  "url": "https://api.supermemory.ai",
  "env": {
    "SUPERMEMORY_API_KEY": "your-key"
  }
}
```

### 2. Command-based MCPs
These MCPs run as subprocesses (most common):

```json
{
  "name": "exa-search",
  "type": "command",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-exa"],
  "env": {
    "EXA_API_KEY": "your-key"
  }
}
```

## Configuration Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Unique identifier for this MCP |
| `type` | string | ✅ Yes | "command" or "http" |
| `description` | string | ❌ No | Human-readable description |
| `command` | string | ⚠️ If type=command | Executable to run |
| `args` | array | ❌ No | Arguments for command |
| `url` | string | ⚠️ If type=http | HTTP endpoint URL |
| `env` | object | ❌ No | Environment variables |
| `health_check_enabled` | boolean | ❌ No | Enable health checks (default: true) |
| `health_check_endpoint` | string | ❌ No | Health check path for HTTP (default: /health) |
| `health_check_timeout` | int | ❌ No | Timeout in seconds (default: 5) |

## Available MCP Servers

### Official MCP Servers

1. **Exa Search** - Web search
   ```bash
   npm install -g @modelcontextprotocol/server-exa
   ```
   Get API key: https://exa.ai

2. **Filesystem** - File operations
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   ```

3. **GitHub** - GitHub integration
   ```bash
   npm install -g @modelcontextprotocol/server-github
   ```
   Requires: GITHUB_TOKEN

4. **Brave Search** - Web search
   ```bash
   npm install -g @modelcontextprotocol/server-brave-search
   ```
   Requires: BRAVE_API_KEY

5. **PostgreSQL** - Database queries
   ```bash
   npm install -g @modelcontextprotocol/server-postgres
   ```

### Custom/Community MCPs

Check the [MCP Registry](https://github.com/modelcontextprotocol/servers) for more servers.

## Usage

1. Add MCP configurations to this file
2. Reference them in your `bots.json`:

```json
{
  "id": "my-bot",
  "mcps": ["exa-search", "supermemory"]
}
```

3. Restart nanobot to load MCPs

## Health Checks

Nanobot automatically checks MCP health on startup:

- **HTTP MCPs**: Sends GET request to `{url}{health_check_endpoint}`
- **Command MCPs**: Checks if process starts within `health_check_timeout` seconds

Failed MCPs are logged but don't prevent bot startup.
