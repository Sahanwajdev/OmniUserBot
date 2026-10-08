import os
from collections import defaultdict
from pathlib import Path
from telethon import Button, events
from core.decorators import omni_cmd
from config import config

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


def _get_categorized_commands(client):
    categorized = defaultdict(list)
    for name, meta in client.commands.items():
        cat = meta.get("category", "General")
        categorized[cat].append(meta)
    return categorized


def _build_hub_view(client):
    prefix = config.COMMAND_PREFIXES[0]
    me_name = getattr(client.me, "first_name", "Owner") if client.me else "Owner"
    me_user = f"@{client.me.username}" if (client.me and client.me.username) else f"ID: {client.me.id}" if client.me else "Active"
    total_cmds = len(client.commands)
    total_modules = len(client.plugins)

    categorized = _get_categorized_commands(client)

    lines = [
        "╔══════════════════════════════════╗",
        f"║     {config.BOT_NAME.upper()} COMMAND HUB      ║",
        "╚══════════════════════════════════╝",
        "╭──────────────────────────────────╮",
        f"│ Owner: {me_name} ({me_user})",
        f"│ Prefix: {prefix}",
        f"│ Total Commands: {total_cmds} Loaded",
        f"│ Modules: {total_modules} Active",
        f"│ Guide: {prefix}help <module> or {prefix}help <cmd>",
        "╰──────────────────────────────────╯\n",
        "╔═════ 🔘 EXPLORE CATEGORIES ═════╗"
    ]

    for cat in sorted(categorized.keys()):
        count = len(categorized[cat])
        cmd_trigger = cat.lower()
        lines.append(f"║ {cat:<18} ({count:02d}) : {prefix}help {cmd_trigger}")

    lines.append("╚══════════════════════════════════╝\n")
    lines.append(f"✨ _{config.BOT_NAME}: Real-Time Direct Block, Tagging & Downloader._")
    lines.append(f"👉 _Type {prefix}help all to see full list at once._")

    # Normal inline buttons (NO style parameters)
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

    return "\n".join(lines), buttons


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
    out = [
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
        desc = m.get("description", "No description.")
        out.append(f"• `{prefix}{m['name']}` — _{desc}_")

    # Normal inline buttons (NO style parameters)
    buttons = [
        [
            Button.inline("Back to Categories", b"h_home"),
            Button.inline("Close Menu", b"h_close")
        ]
    ]

    return "\n".join(out), buttons


def _build_all_view(client):
    prefix = config.COMMAND_PREFIXES[0]
    categorized = _get_categorized_commands(client)
    total_cmds = len(client.commands)

    out = [
        f"**{config.BOT_NAME} — Complete Commands Index**\n",
        f"• Active Prefix: `{prefix}`",
        f"• Total Commands: `{total_cmds}`\n"
    ]

    for cat, cmd_metas in sorted(categorized.items()):
        names = "  ".join([f"`{prefix}{c['name']}`" for c in sorted(cmd_metas, key=lambda x: x["name"])])
        out.append(f"**{cat}** ({len(cmd_metas)}):\n{names}\n")

    buttons = [
        [
            Button.inline("Back to Categories", b"h_home"),
            Button.inline("Close Menu", b"h_close")
        ]
    ]

    return "\n".join(out), buttons


@omni_cmd(
    pattern="help",
    desc="Opens the interactive help menu with photo banner and category buttons.",
    usage=".help [category/command/all]",
    category="General",
    allow_all=True
)
async def help_menu(event):
    client = event.client
    query = event.text_args.strip().lower()
    prefix = config.COMMAND_PREFIXES[0]

    # Case 1: Specific Command Manual (.help <command>)
    if query and query != "all":
        found_cmd = None
        for name, meta in client.commands.items():
            if query == name.lower() or query in [a.lower() for a in meta.get("aliases", [])]:
                found_cmd = meta
                break

        if found_cmd:
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
                    Button.inline("Back to Categories", b"h_home"),
                    Button.inline("Close Menu", b"h_close")
                ]
            ]
            try:
                await event.reply_or_edit(manual, buttons=buttons)
            except Exception:
                await event.reply_or_edit(manual)
            return

        # Case 2: Specific Category (.help <category>)
        cat_key = query.replace(" ", "_").replace("&", "and")
        cat_text, cat_buttons = _build_category_view(client, cat_key)
        if cat_text:
            try:
                await event.reply_or_edit(cat_text, buttons=cat_buttons)
            except Exception:
                await event.reply_or_edit(cat_text)
            return

    # Case 3: Show All Commands (.help all)
    if query == "all":
        all_text, all_buttons = _build_all_view(client)
        try:
            await event.reply_or_edit(all_text, buttons=all_buttons)
        except Exception:
            await event.reply_or_edit(all_text)
        return

    # Case 4: Master Hub with Image Banner (https://files.catbox.moe/rhzor8.jpg)
    hub_text, hub_buttons = _build_hub_view(client)
    media = await get_help_media()

    try:
        if event.out:
            await event.delete()
            await client.send_file(
                event.chat_id,
                file=media,
                caption=hub_text,
                buttons=hub_buttons
            )
        else:
            await client.send_file(
                event.chat_id,
                file=media,
                caption=hub_text,
                reply_to=event.id,
                buttons=hub_buttons
            )
    except Exception:
        # Fallback to text edit/reply
        await event.reply_or_edit(hub_text, buttons=hub_buttons)


@events.register(events.CallbackQuery)
async def help_callback_handler(event):
    data = event.data.decode("utf-8") if event.data else ""
    if not data.startswith("h"):
        return

    client = event.client

    if data == "h_close":
        try:
            await event.delete()
        except Exception:
            pass
        return

    if data == "h_home":
        hub_text, hub_buttons = _build_hub_view(client)
        try:
            await event.edit(hub_text, buttons=hub_buttons)
        except Exception:
            pass
        return

    if data == "hcat_all":
        all_text, all_buttons = _build_all_view(client)
        try:
            await event.edit(all_text, buttons=all_buttons)
        except Exception:
            pass
        return

    if data.startswith("hcat_"):
        cat_key = data[5:]
        cat_text, cat_buttons = _build_category_view(client, cat_key)
        if cat_text:
            try:
                await event.edit(cat_text, buttons=cat_buttons)
            except Exception:
                pass
        return


help_callback_handler.event_filter = events.CallbackQuery()
