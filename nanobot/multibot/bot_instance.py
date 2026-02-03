"""Bot instance with isolated context and workspace."""

import asyncio
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.agent.context import ContextBuilder
from nanobot.agent.loop import AgentLoop
from nanobot.agent.memory import MemoryStore
from nanobot.bus.events import InboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.config.multibot import BotConfig
from nanobot.config.schema import Config


class BotInstance:
    """
    Single bot instance with isolated workspace and MCPs.

    Each bot has:
    - Its own workspace (memory, files, skills)
    - Its own ContextBuilder (SOUL.md, AGENTS.md, etc)
    - Its own AgentLoop
    - Its own enabled MCPs
    """

    def __init__(
        self,
        config: BotConfig,
        global_config: Config,
        shared_bus: MessageBus,
        available_mcps: dict[str, Any],
    ):
        self.config = config
        self.global_config = global_config
        self.bus = shared_bus
        self.available_mcps = available_mcps

        # Setup workspace
        self.workspace = config.workspace_path
        self._init_workspace()

        # Initialize context builder with bot's workspace
        self.context = ContextBuilder(self.workspace)

        # Initialize agent loop
        self.loop = AgentLoop(
            config=self._make_agent_config(),
            bus=self.bus,
            workspace=self.workspace,
        )

        # Track enabled MCPs for this bot
        self.enabled_mcps = self._init_mcps()

        # Track running state
        self._running = False

    def _init_workspace(self) -> None:
        """Create workspace structure with default files."""
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.workspace / "memory").mkdir(exist_ok=True)
        (self.workspace / "skills").mkdir(exist_ok=True)

        # Create default SOUL.md if not exists
        soul_file = self.workspace / "SOUL.md"
        if not soul_file.exists():
            soul_file.write_text(
                f"""# Alma

Eu sou {self.config.name}.

{self.config.description}

## Personalidade

- Útil e amigável
- Conciso e direto
- Especialista no meu domínio
"""
            )

        # Create default AGENTS.md if not exists
        agents_file = self.workspace / "AGENTS.md"
        if not agents_file.exists():
            agents_file.write_text(
                """# Instruções do Agente

Você é um assistente de IA útil.

## Diretrizes

- Sempre explique o que está fazendo
- Use ferramentas quando necessário
- Lembre-se de informações importantes
"""
            )

    def _make_agent_config(self) -> Config:
        """Create agent config from bot config."""
        # Override agent defaults with bot-specific settings
        agent_config = Config()

        # Set workspace
        agent_config.agents.defaults.workspace = str(self.workspace)

        # Set model if specified
        if self.config.agent.model:
            agent_config.agents.defaults.model = self.config.agent.model

        # Set temperature
        if self.config.agent.temperature:
            agent_config.agents.defaults.temperature = self.config.agent.temperature

        # Set max tokens
        if self.config.agent.max_tokens:
            agent_config.agents.defaults.max_tokens = self.config.agent.max_tokens

        return agent_config

    def _init_mcps(self) -> dict[str, Any]:
        """Initialize enabled MCPs for this bot."""
        enabled = {}
        for mcp_name in self.config.mcps:
            if mcp_name in self.available_mcps:
                enabled[mcp_name] = self.available_mcps[mcp_name]
                logger.info(f"Bot {self.config.id}: MCP {mcp_name} enabled")
            else:
                logger.warning(f"Bot {self.config.id}: MCP {mcp_name} not found in config")

        return enabled

    async def start(self) -> None:
        """Start the bot instance."""
        if self._running:
            logger.warning(f"Bot {self.config.id} already running")
            return

        logger.info(f"Starting bot {self.config.id} ({self.config.name})...")
        self._running = True

        # Start agent loop
        await self.loop.start()

        logger.info(f"Bot {self.config.id} started")

    async def stop(self) -> None:
        """Stop the bot instance."""
        if not self._running:
            return

        logger.info(f"Stopping bot {self.config.id}...")
        self._running = False

        # Stop agent loop
        await self.loop.stop()

        logger.info(f"Bot {self.config.id} stopped")

    async def process_message(
        self,
        sender_id: str,
        chat_id: str,
        content: str,
        media: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Process an incoming message.

        Args:
            sender_id: Sender identifier
            chat_id: Chat ID for replies
            content: Message content
            media: Optional list of media file paths
            metadata: Optional metadata
        """
        # Create inbound message
        msg = InboundMessage(
            sender_id=sender_id,
            chat_id=chat_id,
            content=content,
            media=media or [],
            metadata=metadata or {},
        )

        # Route to agent loop
        await self.bus.publish_inbound(msg)

    @property
    def is_running(self) -> bool:
        """Check if bot is running."""
        return self._running

    def get_status(self) -> dict[str, Any]:
        """Get bot status."""
        return {
            "id": self.config.id,
            "name": self.config.name,
            "workspace": str(self.workspace),
            "model": self.config.agent.model,
            "mcps": list(self.enabled_mcps.keys()),
            "running": self._running,
        }
