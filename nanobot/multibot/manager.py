"""Multi-bot manager for running multiple bot instances."""

import asyncio
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.bus.queue import MessageBus
from nanobot.config.multibot import BotConfig, MCPConfig, MultiBotConfig
from nanobot.config.schema import Config
from nanobot.multibot.bot_instance import BotInstance


class MultiBotManager:
    """
    Manages multiple bot instances.

    Each bot has:
    - Isolated workspace and personality
    - Separate Telegram channel
    - Enabled MCPs
    """

    def __init__(self, config: MultiBotConfig, global_config: Config):
        self.config = config
        self.global_config = global_config

        # Shared message bus for all bots
        self.bus = MessageBus()

        # Bot instances
        self.bots: dict[str, BotInstance] = {}

        # MCP servers (shared across bots)
        self.mcps: dict[str, Any] = {}

        # Initialize
        self._init_mcps()
        self._init_bots()

    def _init_mcps(self) -> None:
        """Initialize MCP server configurations."""
        for mcp_cfg in self.config.mcps.mcps:
            self.mcps[mcp_cfg.name] = {
                "config": mcp_cfg,
                "type": mcp_cfg.type,
            }
            logger.info(f"MCP {mcp_cfg.name} configured (type: {mcp_cfg.type})")

    def _init_bots(self) -> None:
        """Initialize bot instances."""
        for bot_cfg in self.config.bots:
            # Check if bot has Telegram enabled
            if not bot_cfg.channels.telegram_enabled:
                logger.warning(f"Bot {bot_cfg.id} has no Telegram enabled, skipping")
                continue

            # Create bot instance
            self.bots[bot_cfg.id] = BotInstance(
                config=bot_cfg,
                global_config=self.global_config,
                shared_bus=self.bus,
                available_mcps=self.mcps,
            )
            logger.info(f"Bot {bot_cfg.id} initialized")

    async def start_all(self) -> None:
        """Start all bot instances."""
        if not self.bots:
            logger.warning("No bots to start")
            return

        logger.info(f"Starting {len(self.bots)} bot(s)...")

        # Start all bots concurrently
        tasks = [bot.start() for bot in self.bots.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("All bots started")

    async def stop_all(self) -> None:
        """Stop all bot instances."""
        logger.info("Stopping all bots...")

        # Stop all bots concurrently
        tasks = [bot.stop() for bot in self.bots.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("All bots stopped")

    def get_bot(self, bot_id: str) -> BotInstance | None:
        """Get bot instance by ID."""
        return self.bots.get(bot_id)

    def get_bot_by_token(self, token: str) -> BotInstance | None:
        """Get bot instance by Telegram token."""
        for bot in self.bots.values():
            if bot.config.channels.telegram_token == token:
                return bot
        return None

    def get_status(self) -> dict[str, Any]:
        """Get status of all bots."""
        return {
            "bots": {bot_id: bot.get_status() for bot_id, bot in self.bots.items()},
            "mcps": list(self.mcps.keys()),
            "total_bots": len(self.bots),
        }

    @classmethod
    def from_config_file(cls, config_path: str | Path, global_config: Config) -> "MultiBotManager":
        """Create MultiBotManager from configuration file."""
        config_path = Path(config_path).expanduser()

        if not config_path.exists():
            logger.warning(f"Multi-bot config not found: {config_path}")
            # Return empty manager
            return cls(MultiBotConfig(), global_config)

        # Load configuration
        multi_bot_config = MultiBotConfig.from_file(config_path)

        logger.info(f"Loaded multi-bot config from {config_path}")
        logger.info(f"  Bots: {len(multi_bot_config.bots)}")
        logger.info(f"  MCPs: {len(multi_bot_config.mcps.mcps)}")

        return cls(multi_bot_config, global_config)
