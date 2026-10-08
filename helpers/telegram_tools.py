import re
from typing import Optional, Tuple, Any
from telethon.tl.types import User, ChannelParticipantsAdmins
from telethon.errors import UserNotMutualContactError


def parse_time_delta(time_str: str) -> Optional[int]:
    """Parses time strings like 10m, 2h, 1d into total seconds."""
    match = re.match(r"^(\d+)([smhd])$", time_str.lower().strip())
    if not match:
        return None
    val, unit = match.groups()
    val = int(val)
    if unit == "s":
        return val
    elif unit == "m":
        return val * 60
    elif unit == "h":
        return val * 3600
    elif unit == "d":
        return val * 86400
    return None


async def get_target_user(event, custom_args: Optional[str] = None) -> Tuple[Optional[User], str]:
    """
    Extracts the target user from:
    1. Reply to message
    2. First word in arguments (e.g. username or numeric ID)
    Returns: (target_user, remaining_text_arguments)
    """
    client = event.client
    args = (custom_args if custom_args is not None else getattr(event, "text_args", "")).strip()
    reply = await event.get_reply_message()

    # Case 1: Replying to a message
    if reply:
        target = await reply.get_sender()
        return target, args

    # Case 2: Mentioned or specified in text
    if args:
        parts = args.split(maxsplit=1)
        first_arg = parts[0]
        remaining = parts[1] if len(parts) > 1 else ""

        try:
            if first_arg.isdigit() or (first_arg.startswith("-") and first_arg[1:].isdigit()):
                user_id = int(first_arg)
                target = await client.get_entity(user_id)
                return target, remaining
            elif first_arg.startswith("@"):
                target = await client.get_entity(first_arg)
                return target, remaining
        except Exception:
            pass

    return None, args


async def is_admin(client, chat_id: int, user_id: int) -> bool:
    """Checks if the given user is an admin or creator in the chat."""
    try:
        permissions = await client.get_permissions(chat_id, user_id)
        return permissions.is_admin or permissions.is_creator
    except Exception:
        return False
