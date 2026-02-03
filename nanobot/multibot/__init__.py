"""Multi-bot package initialization."""

from nanobot.multibot.bot_instance import BotInstance
from nanobot.multibot.manager import MultiBotManager
from nanobot.multibot.telegram_channel import MultiTelegramChannel

__all__ = ["BotInstance", "MultiBotManager", "MultiTelegramChannel"]
