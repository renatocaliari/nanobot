"""Multi-Telegram channel manager for running multiple Telegram bots."""

import asyncio
from typing import Any

from loguru import logger
from telegram import Update
from telegram.error import Conflict
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.multibot.bot_instance import BotInstance
from nanobot.multibot.manager import MultiBotManager


def _markdown_to_telegram_html(text: str) -> str:
    """
    Convert markdown to Telegram-safe HTML.
    """
    if not text:
        return ""

    import re

    # 1. Extract and protect code blocks
    code_blocks: list[str] = []

    def save_code_block(m):
        code_blocks.append(m.group(1))
        return f"\x00CB{len(code_blocks) - 1}\x00"

    text = re.sub(r"```[\w]*\n?([\s\S]*?)```", save_code_block, text)

    # 2. Extract and protect inline code
    inline_codes: list[str] = []

    def save_inline_code(m):
        inline_codes.append(m.group(1))
        return f"\x00IC{len(inline_codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", save_inline_code, text)

    # 3. Headers
    text = re.sub(r"^#{1,6}\s+(.+)$", r"\1", text, flags=re.MULTILINE)

    # 4. Blockquotes
    text = re.sub(r"^>\s*(.*)$", r"\1", text, flags=re.MULTILINE)

    # 5. Escape HTML special characters
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # 6. Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    # 7. Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)

    # 8. Italic
    text = re.sub(r"(?<![a-zA-Z0-9])_([^_]+)_(?![a-zA-Z0-9])", r"<i>\1</i>", text)

    # 9. Strikethrough
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)

    # 10. Bullet lists
    text = re.sub(r"^[-*]\s+", "• ", text, flags=re.MULTILINE)

    # 11. Restore inline code
    for i, code in enumerate(inline_codes):
        escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace(f"\x00IC{i}\x00", f"<code>{escaped}</code>")

    # 12. Restore code blocks
    for i, code in enumerate(code_blocks):
        escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace(f"\x00CB{i}\x00", f"<pre><code>{escaped}</code></pre>")

    return text


class MultiTelegramChannel:
    """
    Manages multiple Telegram bot instances.

    Each bot instance gets its own Telegram bot with unique token.
    """

    def __init__(self, multi_bot_manager: MultiBotManager, bus: MessageBus):
        self.multi_bot_manager = multi_bot_manager
        self.bus = bus

        # Telegram applications (one per bot)
        self.apps: dict[str, Application] = {}

        # Map token -> bot_id
        self.token_to_bot: dict[str, str] = {}

        # Track running state
        self._running = False

        # Store chat_ids for replies (bot_id -> sender_id -> chat_id)
        self._chat_ids: dict[str, dict[str, int]] = {}

    async def start(self) -> None:
        """Start all Telegram bots."""
        logger.info("Starting multi-Telegram channel...")

        # Initialize Telegram application for each bot
        for bot_id, bot_instance in self.multi_bot_manager.bots.items():
            token = bot_instance.config.channels.telegram_token

            if not token:
                logger.warning(f"Bot {bot_id} has no Telegram token, skipping")
                continue

            try:
                # Build the application
                app = Application.builder().token(token).build()

                # Add message handler
                app.add_handler(
                    MessageHandler(
                        (
                            filters.TEXT
                            | filters.PHOTO
                            | filters.VOICE
                            | filters.AUDIO
                            | filters.Document.ALL
                        )
                        & ~filters.COMMAND,
                        lambda u, c, bot_id=bot_id: self._on_message(u, c, bot_id),
                    )
                )

                # Add /start command
                app.add_handler(
                    CommandHandler(
                        "start", lambda u, c, bot_id=bot_id: self._on_start(u, c, bot_id)
                    )
                )

                # Add error handler
                app.add_error_handler(self._error_handler)

                self.apps[bot_id] = app
                self.token_to_bot[token] = bot_id

                # Initialize and start polling
                await app.initialize()
                await app.start()

                # Get bot info
                bot_info = await app.bot.get_me()
                logger.info(f"Bot {bot_id}: Telegram @{bot_info.username} connected")

                # Start polling
                await app.updater.start_polling(
                    allowed_updates=["message"], drop_pending_updates=True
                )

                # Initialize chat_id tracking for this bot
                self._chat_ids[bot_id] = {}

            except Exception as e:
                logger.error(f"Failed to start Telegram for bot {bot_id}: {e}")

        self._running = True
        logger.info(f"Multi-Telegram channel started with {len(self.apps)} bot(s)")

    async def stop(self) -> None:
        """Stop all Telegram bots."""
        logger.info("Stopping multi-Telegram channel...")

        self._running = False

        # Stop all Telegram applications
        for bot_id, app in self.apps.items():
            try:
                logger.info(f"Stopping Telegram for bot {bot_id}...")
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception as e:
                logger.error(f"Error stopping Telegram for bot {bot_id}: {e}")

        self.apps.clear()
        self.token_to_bot.clear()
        self._chat_ids.clear()

        logger.info("Multi-Telegram channel stopped")

    async def send(self, msg: OutboundMessage) -> None:
        """
        Send a message through the appropriate Telegram bot.

        The msg.channel should be in format "telegram:{bot_id}:{chat_id}"
        """
        # Parse channel format
        parts = msg.channel.split(":", 2)
        if len(parts) < 3 or parts[0] != "telegram":
            logger.error(f"Invalid channel format: {msg.channel}")
            return

        bot_id = parts[1]
        chat_id = parts[2]

        # Get the Telegram application for this bot
        app = self.apps.get(bot_id)
        if not app:
            logger.error(f"No Telegram app found for bot {bot_id}")
            return

        try:
            # Convert markdown to Telegram HTML
            html_content = _markdown_to_telegram_html(msg.content)

            # Send message
            await app.bot.send_message(chat_id=int(chat_id), text=html_content, parse_mode="HTML")

        except ValueError:
            logger.error(f"Invalid chat_id: {chat_id}")
        except Exception as e:
            logger.warning(f"HTML parse failed, falling back to plain text: {e}")
            try:
                await app.bot.send_message(chat_id=int(chat_id), text=msg.content)
            except Exception as e2:
                logger.error(f"Error sending Telegram message: {e2}")

    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Telegram errors."""
        if isinstance(context.error, Conflict):
            logger.warning(
                "Telegram polling conflict detected (normal during overlapping deployments)"
            )
            return

        logger.error(f"Telegram error: {context.error}")

    async def _on_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: str
    ) -> None:
        """Handle /start command."""
        if not update.message or not update.effective_user:
            return

        bot_instance = self.multi_bot_manager.get_bot(bot_id)
        if not bot_instance:
            return

        user = update.effective_user
        bot_name = bot_instance.config.name

        await update.message.reply_text(
            f"👋 Hi {user.first_name}! I'm {bot_name}.\n\nSend me a message and I'll respond!"
        )

    async def _on_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: str
    ) -> None:
        """Handle incoming message for a specific bot."""
        if not update.message or not update.effective_user:
            return

        # Get bot instance
        bot_instance = self.multi_bot_manager.get_bot(bot_id)
        if not bot_instance:
            logger.error(f"No bot instance found for {bot_id}")
            return

        message = update.message
        user = update.effective_user
        chat_id = message.chat_id

        # Build sender_id
        sender_id = str(user.id)
        if user.username:
            sender_id = f"{sender_id}|{user.username}"

        # Check allowlist
        allow_from = bot_instance.config.channels.telegram_allow_from
        if allow_from and sender_id not in allow_from and str(user.id) not in allow_from:
            logger.warning(f"Message from {sender_id} not in allowlist, ignoring")
            await message.reply_text("⚠️ You're not authorized to use this bot.")
            return

        # Store chat_id for replies
        if bot_id not in self._chat_ids:
            self._chat_ids[bot_id] = {}
        self._chat_ids[bot_id][sender_id] = chat_id

        # Build content
        content_parts = []
        media_paths = []

        if message.text:
            content_parts.append(message.text)
        if message.caption:
            content_parts.append(message.caption)

        # Handle media
        media_file = None
        media_type = None

        if message.photo:
            media_file = message.photo[-1]
            media_type = "image"
        elif message.voice:
            media_file = message.voice
            media_type = "voice"
        elif message.audio:
            media_file = message.audio
            media_type = "audio"
        elif message.document:
            media_file = message.document
            media_type = "file"

        # Download media if present
        if media_file:
            try:
                from pathlib import Path

                file = await context.bot.get_file(media_file.file_id)
                ext = self._get_extension(media_type, getattr(media_file, "mime_type", None))

                media_dir = Path.home() / ".nanobot" / "media"
                media_dir.mkdir(parents=True, exist_ok=True)

                file_path = media_dir / f"{media_file.file_id[:16]}{ext}"
                await file.download_to_drive(str(file_path))

                media_paths.append(str(file_path))
                content_parts.append(f"[{media_type}: {file_path}]")
                logger.debug(f"Downloaded {media_type} to {file_path}")
            except Exception as e:
                logger.error(f"Failed to download media: {e}")
                content_parts.append(f"[{media_type}: download failed]")

        content = "\n".join(content_parts) if content_parts else "[empty message]"

        logger.debug(f"Telegram message for {bot_id} from {sender_id}: {content[:50]}...")

        # Process message through bot instance
        # Set reply_to channel for responses
        reply_channel = f"telegram:{bot_id}:{chat_id}"

        await bot_instance.process_message(
            sender_id=sender_id,
            chat_id=reply_channel,
            content=content,
            media=media_paths,
            metadata={
                "message_id": message.message_id,
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "bot_id": bot_id,
                "is_group": message.chat.type != "private",
            },
        )

    def _get_extension(self, media_type: str, mime_type: str | None) -> str:
        """Get file extension based on media type."""
        if mime_type:
            ext_map = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/gif": ".gif",
                "audio/ogg": ".ogg",
                "audio/mpeg": ".mp3",
                "audio/mp4": ".m4a",
            }
            if mime_type in ext_map:
                return ext_map[mime_type]

        type_map = {"image": ".jpg", "voice": ".ogg", "audio": ".mp3", "file": ""}
        return type_map.get(media_type, "")

    @property
    def is_running(self) -> bool:
        """Check if channel is running."""
        return self._running

    def get_status(self) -> dict[str, Any]:
        """Get status of all Telegram bots."""
        return {
            bot_id: {
                "running": app.updater.is_running if app.updater else False,
                "connected": True,
            }
            for bot_id, app in self.apps.items()
        }
