import os
from pathlib import Path
from telethon.tl.functions.account import GetAuthorizationsRequest, ResetAuthorizationRequest
from telethon.tl.functions.messages import ReadHistoryRequest
from dotenv import set_key

from core.decorators import omni_cmd
from config import config

ENV_PATH = config.BASE_DIR / ".env"


@omni_cmd(
    pattern="sessions",
    desc="Lists all active authorized Telegram sessions and devices for your account.",
    usage=".sessions",
    category="Security",
    aliases=["devices", "auths"]
)
async def list_sessions(event):
    msg = await event.reply_or_edit("🔍 **Fetching active Telegram sessions...**")
    try:
        res = await event.client(GetAuthorizationsRequest())
        auths = res.authorizations

        out = [f"📱 **Active Telegram Sessions (`{len(auths)}`):**\n"]
        for i, auth in enumerate(auths, 1):
            current_tag = " `[THIS DEVICE]` 🟢" if getattr(auth, "current", False) else ""
            device = auth.device_model or "Unknown Device"
            platform = auth.platform or "Unknown OS"
            app = auth.app_name or "Telegram"
            ip = auth.ip or "Unknown IP"
            country = auth.country or "Unknown"

            out.append(
                f"**{i}. {device} ({platform})**{current_tag}\n"
                f"• **App:** `{app}` | **IP:** `{ip}` ({country})\n"
                f"• **Hash:** `{auth.hash}`\n"
            )

        out.append("💡 Use `.killall` to terminate all other active sessions.")
        await msg.edit("\n".join(out))
    except Exception as e:
        await msg.edit(f"❌ Failed to fetch sessions: `{e}`")


@omni_cmd(
    pattern="killall",
    desc="Terminates all other active Telegram sessions except your current device.",
    usage=".killall",
    category="Security",
    aliases=["sessionkiller", "terminatesessions"]
)
async def kill_other_sessions(event):
    msg = await event.reply_or_edit("⚠️ **Terminating all other Telegram sessions...**")
    client = event.client
    try:
        res = await client(GetAuthorizationsRequest())
        killed = 0
        for auth in res.authorizations:
            if not getattr(auth, "current", False):
                try:
                    await client(ResetAuthorizationRequest(hash=auth.hash))
                    killed += 1
                except Exception:
                    pass

        await msg.edit(f"🔒 **Security Sweep Complete!**\nTerminated `{killed}` other session(s). Your account is secure.")
    except Exception as e:
        await msg.edit(f"❌ Failed to terminate sessions: `{e}`")


@omni_cmd(
    pattern="readall",
    desc="Marks all unread chats and dialogs as read.",
    usage=".readall",
    category="Tools",
    aliases=["clearnotifs", "clearnotif"]
)
async def mark_all_read(event):
    msg = await event.reply_or_edit("🧹 **Marking all unread dialogs as read...**")
    client = event.client
    count = 0
    try:
        async for dialog in client.iter_dialogs():
            if dialog.unread_count > 0:
                try:
                    await client.send_read_acknowledge(dialog.entity, max_id=dialog.message.id)
                    count += 1
                except Exception:
                    pass

        await msg.edit(f"✅ **Done!** Cleared unread notifications in `{count}` chat(s).")
    except Exception as e:
        await msg.edit(f"❌ Failed to clear notifications: `{e}`")


@omni_cmd(
    pattern="setprefix",
    desc="Changes the userbot command prefix on the fly without restarting.",
    usage=".setprefix <new_prefix_character>",
    category="System",
    aliases=["prefix"]
)
async def change_prefix(event):
    new_prefix = event.text_args.strip()
    if not new_prefix or len(new_prefix) > 2:
        await event.reply_or_edit("❌ **Usage:** `.setprefix <symbol>` (e.g. `.setprefix !` or `.setprefix ,`)")
        return

    old_prefix = config.COMMAND_PREFIXES[0]
    config.COMMAND_PREFIXES = [new_prefix]

    # Save to .env if present
    if ENV_PATH.exists():
        try:
            set_key(str(ENV_PATH), "COMMAND_PREFIX", new_prefix)
        except Exception:
            pass

    # Reload plugins to re-bind regexes with new prefix
    from core.loader import reload_plugins
    reload_plugins(event.client)

    await event.reply_or_edit(f"⚡ **Prefix Updated!**\nChanged from `{old_prefix}` to `{new_prefix}`.\nTest it with: `{new_prefix}alive`")


@omni_cmd(
    pattern="cat",
    desc="Views the contents of a replied text file, script, or document in chat.",
    usage=".cat (as reply to text file)",
    category="Tools",
    aliases=["readfile", "open"]
)
async def view_file_content(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply_or_edit("❌ Reply to a document or text file to view its content.")
        return

    msg = await event.reply_or_edit("📖 **Reading file...**")
    temp_path = config.DOWNLOAD_DIR / f"temp_view_{event.id}.txt"
    try:
        await reply.download_media(file=str(temp_path))
        content = temp_path.read_text(encoding="utf-8", errors="replace")

        if len(content) > 3500:
            content = content[:3400] + "\n... *(Truncated)*"

        ext = temp_path.suffix.lstrip(".") or "text"
        out = f"📄 **File Content:**\n```{ext}\n{content}\n```"
        await msg.edit(out)
    except Exception as e:
        await msg.edit(f"❌ Failed to read file: `{e}`")
    finally:
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except Exception:
                pass
