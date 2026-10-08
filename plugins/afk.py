import time
from telethon import events
from core.decorators import omni_cmd
from helpers.formatting import format_time

AFK_STATE = {
    "is_afk": False,
    "reason": "",
    "start_time": 0,
    "last_replied": {},  # user_id: timestamp
}


@omni_cmd(
    pattern="afk",
    desc="Sets your status to Away-From-Keyboard. Auto replies when tagged or PM'd.",
    usage=".afk [optional reason]",
    category="Automation"
)
async def set_afk(event):
    reason = event.text_args.strip() or "Busy right now."
    AFK_STATE["is_afk"] = True
    AFK_STATE["reason"] = reason
    AFK_STATE["start_time"] = time.time()
    AFK_STATE["last_replied"] = {}

    await event.reply_or_edit(
        f"😴 **AFK Mode Activated!**\n"
        f"**Reason:** `{reason}`\n"
        f"_Will auto-reply to tags and PMs until you speak again._"
    )


# Event listener for disabling AFK on outgoing message
@events.register(events.NewMessage(outgoing=True))
async def afk_outgoing_listener(event):
    if not AFK_STATE["is_afk"]:
        return

    # Ignore the .afk command invocation itself
    if event.raw_text and event.raw_text.startswith((".afk", "!afk", "/afk")):
        return

    time_away = time.time() - AFK_STATE["start_time"]
    time_str = format_time(time_away)
    AFK_STATE["is_afk"] = False

    msg = await event.respond(f"✨ **I am back!** Was away for `{time_str}`.")
    import asyncio
    await asyncio.sleep(4)
    try:
        await msg.delete()
    except Exception:
        pass


# Event listener for incoming mentions or private messages while AFK
@events.register(events.NewMessage(incoming=True))
async def afk_incoming_listener(event):
    if not AFK_STATE["is_afk"]:
        return

    client = event.client
    sender = await event.get_sender()
    if not sender or sender.bot or sender.is_self:
        return

    is_pm = event.is_private
    is_mentioned = event.mentioned

    if not (is_pm or is_mentioned):
        return

    # Anti-flood rate limit: max 1 reply every 60 seconds per user
    now = time.time()
    last = AFK_STATE["last_replied"].get(sender.id, 0)
    if now - last < 60:
        return

    AFK_STATE["last_replied"][sender.id] = now
    away_str = format_time(now - AFK_STATE["start_time"])
    reason = AFK_STATE["reason"]

    text = (
        f"💤 **User is currently AFK (Away From Keyboard)**\n\n"
        f"⏱️ **Away Since:** `{away_str} ago`\n"
        f"💬 **Reason:** `{reason}`\n\n"
        f"_I will reply to you as soon as I'm back._"
    )
    await event.reply(text)


afk_outgoing_listener.event_filter = events.NewMessage(outgoing=True)
afk_incoming_listener.event_filter = events.NewMessage(incoming=True)
