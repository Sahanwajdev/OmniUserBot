import os
from collections import defaultdict
from pathlib import Path
from telethon import Button, events
from core.decorators import omni_cmd
from config import config
import core.client as client_module

HELP_IMAGE_URL = "https://files.catbox.moe/rhzor8.jpg"
HELP_LOCAL_PATH = config.DOWNLOAD_DIR / "help_banner.jpg"


async def get_help_media():
    """Returns local cached banner or remote URL."""
    if HELP_LOCAL_PATH.exists() and HELP_LOCAL_PATH.stat().st_size > 0:
        return str(HELP_LOCAL_PATH)
    try:
        from helpers.http_client import http_client
        session = await http_client.get_session()
        async with session.get(HELP_IMAGE_URL) as resp:
            if resp.status == 200:
                content = await resp.read()
                HELP_LOCAL_PATH.write_bytes(content)
                return str(HELP_LOCAL_PATH)
    except Exception:
        pass
    return HELP_IMAGE_URL


def _get_active_client(fallback=None):
    if getattr(client_module, "bot", None):
        return client_module.bot
    return fallback


def _get_categorized_commands(client):
    categorized = defaultdict(list)
    cmds = getattr(client, "commands", {}) if client else {}
    for name, meta in cmds.items():
        cat = meta.get("category", "General")
        categorized[cat].append(meta)
    return categorized


def _build_hub_view(client):
    prefix = config.COMMAND_PREFIXES[0]
    me_name = getattr(client.me, "first_name", "Owner") if (client and client.me) else "Owner"
    me_user = f"@{client.me.username}" if (client and client.me and client.me.username) else f"ID: {client.me.id}" if (client and client.me) else "Active"
    total_cmds = len(client.commands) if (client and client.commands) else 102
    total_modules = len(client.plugins) if (client and client.plugins) else 17

    categorized = _get_categorized_commands(client)

    lines = [
        "╔══════════════════════════════════╗",
        f"║  ⚡ {config.BOT_NAME.upper()} COMMAND HUB ⚡  ║",
        "╚══════════════════════════════════╝",
        "╭──────────────────────────────────╮",
        f"│ 👤 Owner: {me_name} ({me_user})",
        f"│ ⚡ Prefix: {prefix}",
        f"│ 📦 Commands: {total_cmds} Loaded",
        f"│ 📁 Modules: {total_modules} Active",
        f"│ 💡 Guide: {prefix}help <module> or {prefix}help <cmd>",
        "╰──────────────────────────────────╯\n",
        "╔═════ 🔘 EXPLORE CATEGORIES ═════╗"
    ]

    for cat in sorted(categorized.keys()):
        count = len(categorized[cat])
        cmd_trigger = cat.lower()
        lines.append(f"║ {cat:<15} ({count:02d}) : {prefix}help {cmd_trigger}")

    lines.append("╚══════════════════════════════════╝\n")
    lines.append(f"✨ _{config.BOT_NAME}: Real-Time Direct Block, Tagging & Downloader._")
    lines.append(f"👉 _Type {prefix}help all or tap below to explore._")

    caption = "\n".join(lines)
    if len(caption) > 1020:
        caption = caption[:1015] + "..."

    # Normal Telegram inline buttons (2 columns)
    buttons = []
    row = []
    for cat in sorted(categorized.keys()):
        count = len(categorized[cat])
        safe_key = cat.lower().replace(" ", "_").replace("&", "and")
        cb_data = f"hcat_{safe_key}".encode("utf-8")[:64]
        row.append(Button.inline(f"{cat} ({count:02d})", cb_data))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        Button.inline(f"All Commands ({total_cmds})", b"hcat_all"),
        Button.inline("Close Menu", b"h_close")
    ])

    return caption, buttons


def _build_category_view(client, cat_key: str):
    prefix = config.COMMAND_PREFIXES[0]
    categorized = _get_categorized_commands(client)

    matched_cat = None
    for cat in categorized:
        normalized = cat.lower().replace(" ", "_").replace("&", "and")
        if normalized == cat_key or cat.lower() == cat_key.replace("_", " "):
            matched_cat = cat
            break

    if not matched_cat:
        return None, None

    cmds = categorized[matched_cat]
    lines = [
        "╔══════════════════════════════════╗",
        f"║       {matched_cat.upper()} COMMANDS ({len(cmds):02d})",
        "╚══════════════════════════════════╝",
        "╭──────────────────────────────────╮",
        f"│ Category: {matched_cat}",
        f"│ Available Commands: {len(cmds)}",
        f"│ Type {prefix}help <cmd> for detail",
        "╰──────────────────────────────────╯\n"
    ]

    for m in sorted(cmds, key=lambda x: x["name"]):
        cname = m["name"]
        desc = m.get("description", "No description.")
        if len(desc) > 30:
            desc = desc[:28] + ".."
        lines.append(f"• `{prefix}{cname}` — _{desc}_")

    caption = "\n".join(lines)
    if len(caption) > 1020:
        caption = caption[:1015] + "..."

    buttons = [
        [
            Button.inline("« Back to Categories", b"h_home"),
            Button.inline("Close Menu", b"h_close")
        ]
    ]

    return caption, buttons


def _build_all_view(client):
    prefix = config.COMMAND_PREFIXES[0]
    categorized = _get_categorized_commands(client)
    total_cmds = len(client.commands) if client else 0

    lines = [
        "╔══════════════════════════════════╗",
        f"║     ALL COMMANDS INDEX ({total_cmds})",
        "╚══════════════════════════════════╝\n",
        f"• Active Prefix: `{prefix}`",
        f"• Total Loaded: `{total_cmds}` commands\n"
    ]

    for cat in sorted(categorized.keys()):
        cmd_names = ", ".join([f"`{prefix}{c['name']}`" for c in sorted(categorized[cat], key=lambda x: x["name"])])
        lines.append(f"• **{cat}** ({len(categorized[cat])}): {cmd_names}")

    caption = "\n".join(lines)
    if len(caption) > 1020:
        caption = caption[:1015] + "..."

    buttons = [
        [
            Button.inline("« Back to Categories", b"h_home"),
            Button.inline("Close Menu", b"h_close")
        ]
    ]

    return caption, buttons


def _build_command_manual(client, found_cmd):
    prefix = config.COMMAND_PREFIXES[0]
    aliases_str = ", ".join([f"`{prefix}{a}`" for a in found_cmd.get("aliases", [])]) or "None"
    manual = (
        "╔══════════════════════════════════╗\n"
        f"║  COMMAND MANUAL: `{found_cmd['name'].upper()}`\n"
        "╚══════════════════════════════════╝\n\n"
        f"• **Category:** `{found_cmd['category']}`\n"
        f"• **Description:** {found_cmd['description']}\n"
        f"• **Usage:** `{found_cmd['usage']}`\n"
        f"• **Aliases:** {aliases_str}\n\n"
        f"🔙 _Run `{prefix}help` to view all categories._"
    )
    buttons = [
        [
            Button.inline("« Back to Categories", b"h_home"),
            Button.inline("Close Menu", b"h_close")
        ]
    ]
    return manual, buttons


@omni_cmd(
    pattern="help",
    desc="Opens the interactive help menu with photo banner and inline buttons.",
    usage=".help [category/command/all]",
    category="General",
    allow_all=True
)
async def help_menu(event):
    client = event.client
    query = event.text_args.strip().lower()
    prefix = config.COMMAND_PREFIXES[0]

    # Try assistant bot inline query for genuine inline buttons
    if getattr(client, "tgbot", None) and config.BOT_USERNAME:
        try:
            bot_user = config.BOT_USERNAME.lstrip("@")
            inline_q = f"help:{query}" if query else "help"
            results = await client.inline_query(bot_user, inline_q)
            if results:
                reply_to = None
                if not event.out:
                    reply_to = event.id
                elif event.reply_to_msg_id:
                    reply_to = event.reply_to_msg_id

                await results[0].click(event.chat_id, reply_to=reply_to)
                if event.out:
                    await event.delete()
                return
        except Exception:
            pass

    # Fallback to direct client rendering if inline bot is unavailable
    if query and query != "all":
        # Check command
        found_cmd = None
        for name, meta in client.commands.items():
            if query == name.lower() or query in [a.lower() for a in meta.get("aliases", [])]:
                found_cmd = meta
                break
        if found_cmd:
            man_text, man_btns = _build_command_manual(client, found_cmd)
            await event.reply_or_edit(man_text, buttons=man_btns)
            return

        # Check category
        cat_key = query.replace(" ", "_").replace("&", "and")
        cat_text, cat_btns = _build_category_view(client, cat_key)
        if cat_text:
            await event.reply_or_edit(cat_text, buttons=cat_btns)
            return

    if query == "all":
        all_text, all_btns = _build_all_view(client)
        await event.reply_or_edit(all_text, buttons=all_btns)
        return

    # Master hub direct send
    hub_text, hub_btns = _build_hub_view(client)
    media = await get_help_media()
    try:
        if event.out:
            await event.delete()
            await client.send_file(
                event.chat_id,
                file=media,
                caption=hub_text,
                buttons=hub_btns
            )
        else:
            await client.send_file(
                event.chat_id,
                file=media,
                caption=hub_text,
                reply_to=event.id,
                buttons=hub_btns
            )
    except Exception:
        await event.reply_or_edit(hub_text, buttons=hub_btns)


# ---------------- Assistant Bot Handlers (Inline & Callback) ----------------

@events.register(events.InlineQuery)
async def help_inline_query_handler(event):
    """Answers inline queries from userbot with photo banner and inline buttons."""
    query = (event.text or "").strip().lower()
    client = _get_active_client()
    builder = event.builder
    media = await get_help_media()

    # Determine view based on query
    if query.startswith("help:"):
        sub = query[5:].strip()
    else:
        sub = query

    if sub == "all":
        text, btns = _build_all_view(client)
        title = f"{config.BOT_NAME} — All Commands"
    elif sub:
        # Category lookup
        cat_key = sub.replace(" ", "_").replace("&", "and")
        cat_text, cat_btns = _build_category_view(client, cat_key)
        if cat_text:
            text, btns = cat_text, cat_btns
            title = f"{config.BOT_NAME} — {sub.title()} Commands"
        else:
            # Command manual lookup
            found_cmd = None
            if client and client.commands:
                for name, meta in client.commands.items():
                    if sub == name.lower() or sub in [a.lower() for a in meta.get("aliases", [])]:
                        found_cmd = meta
                        break
            if found_cmd:
                text, btns = _build_command_manual(client, found_cmd)
                title = f"{config.BOT_NAME} — {found_cmd['name'].upper()} Manual"
            else:
                text, btns = _build_hub_view(client)
                title = f"{config.BOT_NAME} Command Hub"
    else:
        text, btns = _build_hub_view(client)
        title = f"{config.BOT_NAME} Command Hub"

    try:
        res = builder.photo(
            file=media,
            text=text,
            buttons=btns
        )
    except Exception:
        res = builder.article(
            title=title,
            text=text,
            buttons=btns
        )

    await event.answer([res], cache_time=0)


help_inline_query_handler.bot_event_filter = events.InlineQuery()


@events.register(events.CallbackQuery)
async def help_callback_handler(event):
    """Handles inline button clicks for category navigation and menu closure."""
    data = event.data.decode("utf-8") if event.data else ""
    if not (data.startswith("h") or data.startswith("hcat_")):
        return

    client = _get_active_client()

    if data == "h_close":
        sender_id = event.sender_id
        is_owner = (client and client.me and sender_id == client.me.id)
        is_sudo = sender_id in config.SUDO_USERS
        if is_owner or is_sudo:
            try:
                await event.delete()
            except Exception:
                pass
        else:
            await event.answer("⚠️ Only the bot owner can close this menu.", alert=True)
        return

    if data == "h_home":
        hub_text, hub_btns = _build_hub_view(client)
        try:
            await event.edit(hub_text, buttons=hub_btns)
        except Exception:
            pass
        await event.answer()
        return

    if data == "hcat_all":
        all_text, all_btns = _build_all_view(client)
        try:
            await event.edit(all_text, buttons=all_btns)
        except Exception:
            pass
        await event.answer()
        return

    if data.startswith("hcat_"):
        cat_key = data[5:]
        cat_text, cat_btns = _build_category_view(client, cat_key)
        if cat_text:
            try:
                await event.edit(cat_text, buttons=cat_btns)
            except Exception:
                pass
        await event.answer()
        return


help_callback_handler.bot_event_filter = events.CallbackQuery()
