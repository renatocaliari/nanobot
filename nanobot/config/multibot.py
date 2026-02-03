"""Multi-bot configuration schemas."""

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator


class BotChannelConfig(BaseModel):
    """Channel configuration for a single bot."""

    telegram_enabled: bool = False
    telegram_token: str = ""
    telegram_allow_from: list[str] = Field(default_factory=list)

    @field_validator("telegram_enabled", mode="before")
    @classmethod
    def parse_enabled(cls, v: Any) -> bool:
        """Parse enabled from string."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("telegram_allow_from", mode="before")
    @classmethod
    def parse_allow_from(cls, v: Any) -> list[str]:
        """Parse allow_from from string or list."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if not v or v.strip() == "":
                return []
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [v]
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",")]
        return []


class BotAgentConfig(BaseModel):
    """Agent configuration for a single bot."""

    model: str = "zai/glm-4.7"
    temperature: float = 0.7
    max_tokens: int = 8192


class BotConfig(BaseModel):
    """Configuration for a single bot instance."""

    id: str
    name: str
    description: str = ""

    # Channel configuration
    channels: BotChannelConfig = Field(default_factory=BotChannelConfig)

    # Workspace path (can be relative or absolute, ~ expanded)
    workspace: str = "~/.nanobot/workspace"

    # Agent settings
    agent: BotAgentConfig = Field(default_factory=BotAgentConfig)

    # MCP servers to enable (list of MCP names from mcp.json)
    mcps: list[str] = Field(default_factory=list)

    @property
    def workspace_path(self) -> Path:
        """Get expanded workspace path."""
        return Path(self.workspace).expanduser()


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""

    name: str
    type: str  # "command" or "http"
    description: str = ""

    # Command-based MCP (npx, python, etc.)
    command: str = ""
    args: list[str] = Field(default_factory=list)

    # HTTP-based MCP (REST API)
    url: str = ""

    # Environment variables
    env: dict[str, str] = Field(default_factory=dict)

    # Health check configuration
    health_check_enabled: bool = True
    health_check_endpoint: str = "/health"
    health_check_timeout: int = 5


class MCPConfig(BaseModel):
    """Configuration for MCP servers."""

    mcps: list[MCPServerConfig] = Field(default_factory=list)

    def get_mcp(self, name: str) -> MCPServerConfig | None:
        """Get MCP config by name."""
        for mcp in self.mcps:
            if mcp.name == name:
                return mcp
        return None


class MultiBotConfig(BaseModel):
    """Root configuration for multi-bot setup."""

    bots: list[BotConfig] = Field(default_factory=list)
    mcps: MCPConfig = Field(default_factory=MCPConfig)

    def get_bot(self, bot_id: str) -> BotConfig | None:
        """Get bot config by ID."""
        for bot in self.bots:
            if bot.id == bot_id:
                return bot
        return None

    @classmethod
    def from_file(cls, path: str | Path) -> "MultiBotConfig":
        """Load configuration from JSON file."""
        import json

        config_path = Path(path).expanduser()
        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = json.load(f)

        return cls(**data)

    def to_file(self, path: str | Path) -> None:
        """Save configuration to JSON file."""
        import json

        config_path = Path(path).expanduser()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(self.model_dump(mode="json"), f, indent=2)
