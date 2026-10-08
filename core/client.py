import asyncio
import time
from typing import Optional, Dict, Any
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import User

from config import config
from .logger import log


class OmniClient(TelegramClient):
    """
    OmniUserBot TelegramClient subclass.
    Provides automated session handling, owner caching, plugin registration,
    and enhanced helper methods.
    """

    def __init__(self):
        self.start_time = time.time()
        self.me: Optional[User] = None
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.plugins: Dict[str, Any] = {}
        self.version = "1.0.0"

        # Initialize session
        if config.STRING_SESSION:
            session = StringSession(config.STRING_SESSION)
            log.info("Loaded credentials with Telethon StringSession.")
        else:
            session = str(config.BASE_DIR / config.SESSION_NAME)
            log.info(f"Using local SQLite session file: {config.SESSION_NAME}.session")

        if not config.API_ID or not config.API_HASH:
            raise ValueError(
                "API_ID and API_HASH must be configured in .env or environment variables. "
                "Get them from https://my.telegram.org"
            )

        super().__init__(
            session=session,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            sequential_updates=True,
            auto_reconnect=True,
            retry_delay=1,
        )

    async def init_client(self):
        """Connects and caches the current authenticated user."""
        self.me = await self.get_me()
        log.info(
            f"Logged in as: {self.me.first_name} "
            f"(@{self.me.username or 'NoUsername'}) [ID: {self.me.id}]"
        )
        if config.LOG_CHAT_ID:
            try:
                await self.send_message(
                    config.LOG_CHAT_ID,
                    f"**⚡ {config.BOT_NAME} v{self.version} Started!**\n"
                    f"• **User:** [{self.me.first_name}](tg://user?id={self.me.id})\n"
                    f"• **Prefixes:** `{' '.join(config.COMMAND_PREFIXES)}`\n"
                    f"• **Commands:** `{len(self.commands)} loaded`"
                )
            except Exception as e:
                log.warning(f"Could not send startup log to LOG_CHAT_ID: {e}")

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def uptime_str(self) -> str:
        seconds = int(self.uptime_seconds)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    async def edit_or_reply(self, event, text: str, parse_mode: str = "md", link_preview: bool = False, **kwargs):
        """
        Edits the message if it's an outgoing message from the owner,
        or replies to it if it was sent by someone else (e.g. Sudo user).
        Splits automatically if message exceeds Telegram limit.
        """
        if len(text) > config.MAX_MESSAGE_LENGTH:
            # Send initial part as edit/reply and remaining parts as replies
            chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
            first_chunk = chunks[0]
            if event.out:
                msg = await event.edit(first_chunk, parse_mode=parse_mode, link_preview=link_preview, **kwargs)
            else:
                msg = await event.reply(first_chunk, parse_mode=parse_mode, link_preview=link_preview, **kwargs)

            for chunk in chunks[1:]:
                await asyncio.sleep(0.3)
                await event.respond(chunk, parse_mode=parse_mode, link_preview=link_preview)
            return msg

        if event.out:
            return await event.edit(text, parse_mode=parse_mode, link_preview=link_preview, **kwargs)
        else:
            return await event.reply(text, parse_mode=parse_mode, link_preview=link_preview, **kwargs)


# Global bot instance placeholder (instantiated in main.py)
bot: Optional[OmniClient] = None
