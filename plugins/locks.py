from telethon.tl.types import ChatBannedRights
from telethon.errors import ChatAdminRequiredError
from core.decorators import omni_cmd

LOCK_TYPES = {
    "msg": {"send_messages": True},
    "media": {"send_media": True},
    "stickers": {"send_stickers": True},
    "gifs": {"send_gifs": True},
    "games": {"send_games": True},
    "links": {"embed_link_previews": True},
    "invites": {"invite_users": True},
    "pin": {"pin_messages": True},
    "changeinfo": {"change_info": True},
    "all": {
        "send_messages": True,
        "send_media": True,
        "send_stickers": True,
        "send_gifs": True,
        "send_games": True,
        "embed_link_previews": True,
        "invite_users": True,
        "pin_messages": True,
        "change_info": True,
    },
}


@omni_cmd(
    pattern="lock",
    desc="Locks chat permissions for normal members (e.g. media, stickers, links).",
    usage=".lock <type>\nTypes: msg, media, stickers, gifs, games, links, invites, pin, changeinfo, all",
    category="Admin",
    only_groups=True
)
async def lock_chat(event):
    target = event.text_args.lower().strip()
    if target not in LOCK_TYPES:
        types_str = ", ".join(f"`{k}`" for k in LOCK_TYPES.keys())
        await event.reply_or_edit(f"🔒 **Usage:** `.lock <type>`\n**Valid Types:** {types_str}")
        return

    rights_kwargs = LOCK_TYPES[target]
    rights = ChatBannedRights(until_date=None, **rights_kwargs)

    try:
        await event.client.edit_permissions(event.chat_id, rights=rights)
        await event.reply_or_edit(f"🔒 **Locked:** `{target}` is now restricted for non-admins.")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ Administrator privileges required to manage group permissions.")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to lock: `{e}`")


@omni_cmd(
    pattern="unlock",
    desc="Unlocks chat permissions for normal members.",
    usage=".unlock <type>\nTypes: msg, media, stickers, gifs, games, links, invites, pin, changeinfo, all",
    category="Admin",
    only_groups=True
)
async def unlock_chat(event):
    target = event.text_args.lower().strip()
    if target not in LOCK_TYPES:
        types_str = ", ".join(f"`{k}`" for k in LOCK_TYPES.keys())
        await event.reply_or_edit(f"🔓 **Usage:** `.unlock <type>`\n**Valid Types:** {types_str}")
        return

    # Invert rights kwargs to False
    rights_kwargs = {k: False for k in LOCK_TYPES[target].keys()}
    rights = ChatBannedRights(until_date=None, **rights_kwargs)

    try:
        await event.client.edit_permissions(event.chat_id, rights=rights)
        await event.reply_or_edit(f"🔓 **Unlocked:** `{target}` is now permitted for members.")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ Administrator privileges required to manage group permissions.")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to unlock: `{e}`")


@omni_cmd(
    pattern="locks",
    desc="Displays current chat restriction status.",
    usage=".locks",
    category="Admin",
    only_groups=True
)
async def view_locks(event):
    chat = await event.get_chat()
    banned = getattr(chat, "default_banned_rights", None)
    if not banned:
        await event.reply_or_edit("ℹ️ No default restrictions set for this chat.")
        return

    def status(flag):
        return "🔒 Locked" if flag else "🔓 Allowed"

    out = (
        f"🛡️ **Permissions for {chat.title}:**\n\n"
        f"• **Messages:** {status(banned.send_messages)}\n"
        f"• **Media:** {status(banned.send_media)}\n"
        f"• **Stickers:** {status(banned.send_stickers)}\n"
        f"• **GIFs:** {status(banned.send_gifs)}\n"
        f"• **Links:** {status(banned.embed_link_previews)}\n"
        f"• **Pin Messages:** {status(banned.pin_messages)}\n"
        f"• **Invites:** {status(banned.invite_users)}"
    )
    await event.reply_or_edit(out)
