import functools
import re
import traceback
from typing import Callable, Optional, List, Union
from telethon import events

from config import config
from .logger import log

# Registry of all registered command definitions
COMMAND_REGISTRY = {}


def register_cmd(
    name: str,
    desc: str = "No description provided.",
    usage: str = "",
    category: str = "General",
    aliases: Optional[List[str]] = None,
):
    """
    Metadata registrar for userbot commands.
    Used for documentation and dynamic help menu generation.
    """
    cmd_names = [name] + (aliases or [])
    COMMAND_REGISTRY[name] = {
        "name": name,
        "aliases": aliases or [],
        "description": desc,
        "usage": usage or f"{config.COMMAND_PREFIXES[0]}{name}",
        "category": category,
        "all_names": cmd_names,
    }


def omni_cmd(
    pattern: str,
    desc: str = "",
    usage: str = "",
    category: str = "General",
    aliases: Optional[List[str]] = None,
    allow_sudo: bool = True,
    allow_all: bool = False,
    only_groups: bool = False,
    only_pm: bool = False,
):
    """
    Core decorator for OmniUserBot commands.
    Automatically binds prefix, permission controls, and error handling.
    """
    all_names = [pattern] + (aliases or [])
    escaped_prefixes = re.escape("".join(config.COMMAND_PREFIXES))
    names_regex = "|".join([re.escape(n) for n in all_names])
    
    # Matches: .cmd or .cmd args
    regex_pattern = re.compile(rf"^[{escaped_prefixes}]({names_regex})(?:\s+([\s\S]+))?$", re.IGNORECASE)

    # Register in command metadata
    register_cmd(
        name=pattern,
        desc=desc,
        usage=usage or f"{config.COMMAND_PREFIXES[0]}{pattern}",
        category=category,
        aliases=aliases,
    )

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(event):
            client = event.client
            sender_id = event.sender_id

            # Permission check: Owner, Sudo, or Public command
            is_owner = event.out or (client.me and sender_id == client.me.id)
            is_sudo = allow_sudo and (sender_id in config.SUDO_USERS)

            if not (allow_all or is_owner or is_sudo):
                return

            # Chat filters
            if only_groups and not (event.is_group or event.is_channel):
                await event.reply("❌ This command can only be used in groups/channels.")
                return

            if only_pm and not event.is_private:
                await event.reply("❌ This command can only be used in private messages.")
                return

            # Extract arguments
            match = regex_pattern.match(event.raw_text or "")
            args_text = match.group(2).strip() if (match and match.group(2)) else ""

            # Bind helper methods to event
            event.text_args = args_text
            event.reply_or_edit = functools.partial(client.edit_or_reply, event)

            try:
                await func(event)
            except Exception as e:
                err_trace = traceback.format_exc()
                log.error(f"Error in command '{pattern}':\n{err_trace}")
                
                # Format clean error message to user
                err_msg = (
                    f"⚠️ **Command Error: `{pattern}`**\n"
                    f"**Error:** `{type(e).__name__}: {str(e)}`\n\n"
                    f"💡 *Check your parameters or review terminal logs for details.*"
                )
                try:
                    await client.edit_or_reply(event, err_msg)
                except Exception:
                    pass

        # Attach Telethon event handler
        from telethon.events import NewMessage
        wrapper.event_filter = NewMessage(pattern=regex_pattern)
        wrapper.raw_cmd = pattern
        return wrapper

    return decorator
