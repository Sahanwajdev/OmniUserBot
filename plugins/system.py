import os
import sys
import time
import asyncio
from telethon import events
from core.decorators import omni_cmd
from core.loader import reload_plugins
from config import config
from helpers.system_info import get_system_summary


@omni_cmd(
    pattern="alive",
    desc="Displays userbot status, uptime, system resources, and version.",
    usage=".alive",
    category="System"
)
async def bot_alive(event):
    client = event.client
    uptime = client.uptime_str
    sys_info = get_system_summary()
    prefix = "".join(config.COMMAND_PREFIXES)
    total_cmds = len(client.commands)

    me_name = getattr(client.me, "first_name", "Owner") if client.me else "Owner"
    me_id = getattr(client.me, "id", "") if client.me else ""
    owner_str = f"[{me_name}](tg://user?id={me_id})" if me_id else me_name

    text = (
        f"**{config.ALIVE_EMOJI} {config.BOT_NAME} is Online!**\n\n"
        f"• **Owner:** {owner_str}\n"
        f"• **Uptime:** `{uptime}`\n"
        f"• **Prefix:** `{prefix}`\n"
        f"• **Commands:** `{total_cmds} Loaded`\n"
        f"• **Python:** `{sys_info['python']}`\n"
        f"• **Telethon:** `v{sys_info['telethon']}`\n"
        f"• **CPU:** `{sys_info['cpu_usage']}` | **RAM:** `{sys_info['ram_usage']}`\n\n"
        f"💬 _{config.ALIVE_TEXT}_"
    )
    await event.reply_or_edit(text)


@omni_cmd(
    pattern="ping",
    desc="Measures round-trip response latency to Telegram datacenters.",
    usage=".ping",
    category="System"
)
async def bot_ping(event):
    start = time.perf_counter()
    msg = await event.reply_or_edit("⚡ `Pinging...`")
    end = time.perf_counter()
    latency_ms = (end - start) * 1000

    await msg.edit(f"🏓 **Pong!**\n⏱️ **Latency:** `{latency_ms:.2f} ms`")


@omni_cmd(
    pattern="sysinfo",
    desc="Displays detailed hardware and server environment metrics.",
    usage=".sysinfo",
    category="System",
    aliases=["neofetch", "hardware"]
)
async def system_info(event):
    sys_info = get_system_summary()
    out = (
        f"🖥️ **Host System Information**\n\n"
        f"• **Operating System:** `{sys_info['os']}`\n"
        f"• **Python Version:** `{sys_info['python']}`\n"
        f"• **Telethon Core:** `{sys_info['telethon']}`\n"
        f"• **CPU Cores:** `{sys_info['cpu_cores']}`\n"
        f"• **CPU Load:** `{sys_info['cpu_usage']}`\n"
        f"• **RAM Usage:** `{sys_info['ram_usage']}`\n"
        f"• **Disk Usage:** `{sys_info['disk_usage']}`\n"
        f"• **Bot Uptime:** `{event.client.uptime_str}`"
    )
    await event.reply_or_edit(out)


@omni_cmd(
    pattern="reload",
    desc="Hot-reloads all plugins dynamically without stopping the bot.",
    usage=".reload",
    category="System"
)
async def reload_cmd(event):
    msg = await event.reply_or_edit("🔄 **Hot-reloading all plugins...**")
    try:
        count = reload_plugins(event.client)
        await msg.edit(f"✅ **Reload Complete!** Loaded `{count}` plugins and `{len(event.client.commands)}` commands.")
    except Exception as e:
        await msg.edit(f"❌ **Reload Failed:** `{e}`")


@omni_cmd(
    pattern="restart",
    desc="Gracefully restarts the userbot process.",
    usage=".restart",
    category="System",
    aliases=["reboot"]
)
async def restart_cmd(event):
    await event.reply_or_edit("🔄 **Restarting OmniUserBot...**\n_Please wait a few seconds._")
    await event.client.disconnect()
    os.execv(sys.executable, [sys.executable] + sys.argv)
