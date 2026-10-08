from collections import defaultdict
from core.decorators import omni_cmd
from config import config


@omni_cmd(
    pattern="help",
    desc="Shows all available modules and commands, or detailed help for a specific command.",
    usage=".help [command_name]",
    category="General"
)
async def help_menu(event):
    client = event.client
    query = event.text_args.strip().lower()
    prefix = config.COMMAND_PREFIXES[0]

    # Detailed command help
    if query:
        # Check if query matches a command name or alias
        found_cmd = None
        for name, meta in client.commands.items():
            if query == name.lower() or query in [a.lower() for a in meta.get("aliases", [])]:
                found_cmd = meta
                break

        if found_cmd:
            aliases_str = ", ".join([f"`{a}`" for a in found_cmd.get("aliases", [])]) or "None"
            out = (
                f"📖 **Command Manual:** `{found_cmd['name']}`\n\n"
                f"• **Category:** `{found_cmd['category']}`\n"
                f"• **Description:** {found_cmd['description']}\n"
                f"• **Usage:** `{found_cmd['usage']}`\n"
                f"• **Aliases:** {aliases_str}"
            )
            await event.reply_or_edit(out)
            return

    # Categorized overview
    categorized = defaultdict(list)
    for name, meta in client.commands.items():
        cat = meta.get("category", "General")
        categorized[cat].append(name)

    total_cmds = len(client.commands)
    out = [
        f"⚡ **{config.BOT_NAME} — Command Center**\n",
        f"• **Active Prefix:** `{prefix}`",
        f"• **Total Commands:** `{total_cmds}`",
        f"• **Help Syntax:** `{prefix}help <command>` for details\n"
    ]

    for category, cmd_list in sorted(categorized.items()):
        cmd_names = "  ".join([f"`{prefix}{c}`" for c in sorted(cmd_list)])
        out.append(f"📁 **{category}** ({len(cmd_list)}):\n{cmd_names}\n")

    out.append("✨ _OmniUserBot: Powered by modern Telethon with ultra-fast search & automation._")
    await event.reply_or_edit("\n".join(out))
