from collections import defaultdict
from telethon import Button
from core.decorators import omni_cmd
from config import config

CATEGORY_ICONS = {
    "Security": "🛡️",
    "Admin": "👮",
    "Tagger": "👥",
    "Media": "🎥",
    "Web Search": "🔍",
    "Scrapers": "🌐",
    "Tools": "🛠️",
    "Notes & Filters": "📝",
    "Profile": "🎭",
    "Locks": "🔒",
    "Fun": "🕹️",
    "Memes": "😹",
    "System": "⚙️",
    "Automation": "⏰",
    "General": "📦",
    "Account Security": "🔐",
}


@omni_cmd(
    pattern="help",
    desc="Shows all available modules and commands, or detailed help for a specific command.",
    usage=".help [module/command/all]",
    category="General",
    allow_all=True
)
async def help_menu(event):
    client = event.client
    query = event.text_args.strip().lower()
    prefix = config.COMMAND_PREFIXES[0]

    # Map categories and command lookup
    categorized = defaultdict(list)
    cat_lookup = {}
    for name, meta in client.commands.items():
        cat = meta.get("category", "General")
        categorized[cat].append(meta)
        cat_lookup[cat.lower()] = cat

    # Case 1: Specific Command Manual
    if query and query != "all" and query not in cat_lookup:
        found_cmd = None
        for name, meta in client.commands.items():
            if query == name.lower() or query in [a.lower() for a in meta.get("aliases", [])]:
                found_cmd = meta
                break

        if found_cmd:
            cat_icon = CATEGORY_ICONS.get(found_cmd.get("category", ""), "📌")
            aliases_str = ", ".join([f"`{prefix}{a}`" for a in found_cmd.get("aliases", [])]) or "None"
            manual = (
                f"╔══════════════════════════════╗\n"
                f"║  📖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗠𝗔𝗡𝗨𝗔𝗟: `{found_cmd['name'].upper()}`\n"
                f"╚══════════════════════════════╝\n\n"
                f"• {cat_icon} **Category:** `{found_cmd['category']}`\n"
                f"• 📝 **Description:** {found_cmd['description']}\n"
                f"• 💡 **Usage:** `{found_cmd['usage']}`\n"
                f"• 🏷️ **Aliases:** {aliases_str}\n\n"
                f"🔙 _Run `{prefix}help` to view all categories._"
            )
            buttons = [
                [
                    Button.url("🐙 GitHub Repository", "https://github.com/Sahanwajdev/OmniUserBot"),
                    Button.url("💬 Commands Guide", "https://github.com/Sahanwajdev/OmniUserBot#readme")
                ]
            ]
            try:
                await event.reply_or_edit(manual, buttons=buttons)
            except Exception:
                await event.reply_or_edit(manual)
            return

    # Case 2: Specific Category Exploration (.help <category>)
    if query in cat_lookup:
        actual_cat = cat_lookup[query]
        cmds = categorized[actual_cat]
        cat_icon = CATEGORY_ICONS.get(actual_cat, "📁")

        out = [
            f"╔══════════════════════════════╗",
            f"║  {cat_icon} **{actual_cat.upper()} MODULE**",
            f"╚══════════════════════════════╝",
            f"╭──────────────────────────────╮",
            f"│ 📂 Category: `{actual_cat}`",
            f"│ 📦 Total Commands: `{len(cmds)}`",
            f"│ 💡 Detailed info: `{prefix}help <cmd>`",
            f"╰──────────────────────────────╯\n"
        ]

        for m in sorted(cmds, key=lambda x: x["name"]):
            desc = m.get("description", "No description.")
            out.append(f"• `{prefix}{m['name']}` — _{desc}_")

        out.append(f"\n🔙 _Return to category menu: `{prefix}help`_")

        buttons = [
            [
                Button.url("🐙 GitHub Repo", "https://github.com/Sahanwajdev/OmniUserBot"),
                Button.url("⚡ Alive Check", "https://github.com/Sahanwajdev/OmniUserBot#readme")
            ]
        ]
        try:
            await event.reply_or_edit("\n".join(out), buttons=buttons)
        except Exception:
            await event.reply_or_edit("\n".join(out))
        return

    # Case 3: Show All Commands Index (.help all)
    if query == "all":
        out = [
            f"⚡ **{config.BOT_NAME} — Complete Commands Index**\n",
            f"• **Active Prefix:** `{prefix}`",
            f"• **Total Commands:** `{len(client.commands)}`\n"
        ]
        for category, cmd_metas in sorted(categorized.items()):
            cat_icon = CATEGORY_ICONS.get(category, "📁")
            names = "  ".join([f"`{prefix}{c['name']}`" for c in sorted(cmd_metas, key=lambda x: x["name"])])
            out.append(f"{cat_icon} **{category}** ({len(cmd_metas)}):\n{names}\n")

        out.append(f"💡 _Syntax info: `{prefix}help <command>`_")
        await event.reply_or_edit("\n".join(out))
        return

    # Case 4: Master Colorful Hub Menu (.help)
    me_name = getattr(client.me, "first_name", "Owner") if client.me else "Owner"
    me_user = f"@{client.me.username}" if (client.me and client.me.username) else f"ID: {client.me.id}" if client.me else "Active"
    total_cmds = len(client.commands)
    total_modules = len(client.plugins)

    hub = [
        "╔══════════════════════════════════╗",
        f"║  ⚡ **{config.BOT_NAME.upper()} COMMAND HUB** ⚡  ║",
        "╚══════════════════════════════════╝",
        "╭──────────────────────────────────╮",
        f"│ 👤 **Owner:** `{me_name}` ({me_user})",
        f"│ ⚡ **Prefix:** `{prefix}`",
        f"│ 📦 **Total Commands:** `{total_cmds}` Loaded",
        f"│ 📁 **Modules:** `{total_modules}` Active",
        f"│ 💡 **Guide:** `{prefix}help <module>` or `{prefix}help <cmd>`",
        "╰──────────────────────────────────╯\n",
        "╔═════ 🔘 **EXPLORE CATEGORIES** ═════╗"
    ]

    for category, cmd_metas in sorted(categorized.items()):
        cat_icon = CATEGORY_ICONS.get(category, "📁")
        cat_arg = category.lower()
        hub.append(f"║ {cat_icon} **{category:<16}** `({len(cmd_metas):02d})` : `{prefix}help {cat_arg}`")

    hub.append("╚══════════════════════════════════╝")
    hub.append(f"\n✨ _OmniUserBot: Powered by Telethon with Real-Time Direct Block, Tagging & Downloader._")
    hub.append(f"👉 _Type `{prefix}help all` to see full list at once._")

    buttons = [
        [
            Button.url("🐙 GitHub Repository", "https://github.com/Sahanwajdev/OmniUserBot"),
            Button.url("💬 Commands Guide", "https://github.com/Sahanwajdev/OmniUserBot#readme")
        ]
    ]

    try:
        await event.reply_or_edit("\n".join(hub), buttons=buttons)
    except Exception:
        await event.reply_or_edit("\n".join(hub))
