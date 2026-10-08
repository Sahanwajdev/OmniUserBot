import json
from pathlib import Path
from telethon import events
from core.decorators import omni_cmd
from config import config

STORAGE_FILE = config.BASE_DIR / "notes_filters.json"

# State structure
DATA = {
    "notes": {},      # note_name: content_text
    "filters": {},    # str(chat_id): { keyword: reply_text }
}


def load_storage():
    if STORAGE_FILE.exists():
        try:
            d = json.loads(STORAGE_FILE.read_text(encoding="utf-8"))
            DATA["notes"] = d.get("notes", {})
            DATA["filters"] = d.get("filters", {})
        except Exception:
            pass


def save_storage():
    try:
        STORAGE_FILE.write_text(json.dumps(DATA, indent=2), encoding="utf-8")
    except Exception:
        pass


load_storage()


# --- NOTES ---

@omni_cmd(
    pattern="save",
    desc="Saves a note with text or replied message content.",
    usage=".save <note_name> [text or reply]",
    category="Notes & Filters",
    aliases=["snip"]
)
async def save_note(event):
    args = event.text_args.split(maxsplit=1)
    if not args:
        await event.reply_or_edit("❌ **Usage:** `.save <note_name> [content]` or reply to a message.")
        return

    name = args[0].lower()
    content = args[1] if len(args) > 1 else ""

    if not content:
        reply = await event.get_reply_message()
        if reply and reply.text:
            content = reply.text

    if not content:
        await event.reply_or_edit("❌ Please provide text content or reply to a message.")
        return

    DATA["notes"][name] = content
    save_storage()
    await event.reply_or_edit(f"📝 **Note Saved:** `{name}`\nRetrieve it anytime using `.get {name}`.")


@omni_cmd(
    pattern="get",
    desc="Retrieves and posts a saved note.",
    usage=".get <note_name>",
    category="Notes & Filters"
)
async def get_note(event):
    name = event.text_args.strip().lower()
    if not name:
        await event.reply_or_edit("❌ **Usage:** `.get <note_name>`")
        return

    if name not in DATA["notes"]:
        await event.reply_or_edit(f"❌ Note `{name}` does not exist. Use `.notes` to view all saved notes.")
        return

    content = DATA["notes"][name]
    await event.reply_or_edit(content)


@omni_cmd(
    pattern="clear",
    desc="Deletes a saved note.",
    usage=".clear <note_name>",
    category="Notes & Filters"
)
async def clear_note(event):
    name = event.text_args.strip().lower()
    if not name:
        await event.reply_or_edit("❌ **Usage:** `.clear <note_name>`")
        return

    if name in DATA["notes"]:
        del DATA["notes"][name]
        save_storage()
        await event.reply_or_edit(f"🗑️ **Note Deleted:** `{name}`")
    else:
        await event.reply_or_edit(f"❌ Note `{name}` not found.")


@omni_cmd(
    pattern="notes",
    desc="Lists all saved notes.",
    usage=".notes",
    category="Notes & Filters"
)
async def list_notes(event):
    if not DATA["notes"]:
        await event.reply_or_edit("📝 No saved notes yet. Create one with `.save <name> <text>`.")
        return

    out = ["📝 **Your Saved Notes:**\n"]
    for k in sorted(DATA["notes"].keys()):
        out.append(f"• `{k}`")

    out.append("\n💡 Retrieve with `.get <name>`")
    await event.reply_or_edit("\n".join(out))


# --- CHAT FILTERS ---

@omni_cmd(
    pattern="filter",
    desc="Sets an automated auto-reply trigger for a keyword in this chat.",
    usage=".filter <keyword> [reply_text]",
    category="Notes & Filters",
    only_groups=True
)
async def set_filter(event):
    args = event.text_args.split(maxsplit=1)
    if not args:
        await event.reply_or_edit("❌ **Usage:** `.filter <keyword> [reply_text]` or reply to message.")
        return

    keyword = args[0].lower()
    content = args[1] if len(args) > 1 else ""

    if not content:
        reply = await event.get_reply_message()
        if reply and reply.text:
            content = reply.text

    if not content:
        await event.reply_or_edit("❌ Provide reply text or reply to a message.")
        return

    chat_id = str(event.chat_id)
    if chat_id not in DATA["filters"]:
        DATA["filters"][chat_id] = {}

    DATA["filters"][chat_id][keyword] = content
    save_storage()
    await event.reply_or_edit(f"🎯 **Filter Added:** Whenever anyone types `{keyword}`, bot will auto-reply.")


@omni_cmd(
    pattern="stop",
    desc="Stops and deletes a chat filter.",
    usage=".stop <keyword>",
    category="Notes & Filters",
    only_groups=True
)
async def stop_filter(event):
    keyword = event.text_args.strip().lower()
    chat_id = str(event.chat_id)

    if chat_id in DATA["filters"] and keyword in DATA["filters"][chat_id]:
        del DATA["filters"][chat_id][keyword]
        save_storage()
        await event.reply_or_edit(f"🛑 **Filter Removed:** `{keyword}`")
    else:
        await event.reply_or_edit(f"❌ Filter `{keyword}` not found in this chat.")


@omni_cmd(
    pattern="filters",
    desc="Lists all active filters in the current chat.",
    usage=".filters",
    category="Notes & Filters",
    only_groups=True
)
async def list_filters(event):
    chat_id = str(event.chat_id)
    chat_filters = DATA["filters"].get(chat_id, {})

    if not chat_filters:
        await event.reply_or_edit("🎯 No active filters in this chat. Add one with `.filter <keyword> <text>`.")
        return

    out = [f"🎯 **Active Filters in this Chat (`{len(chat_filters)}`):**\n"]
    for k in sorted(chat_filters.keys()):
        out.append(f"• `{k}`")

    await event.reply_or_edit("\n".join(out))


# Background listener for filter triggers
@events.register(events.NewMessage(incoming=True))
async def chat_filter_listener(event):
    if not (event.is_group or event.is_channel) or not event.raw_text:
        return

    chat_id = str(event.chat_id)
    chat_filters = DATA["filters"].get(chat_id)
    if not chat_filters:
        return

    sender = await event.get_sender()
    if sender and (sender.bot or sender.is_self):
        return

    text_lower = event.raw_text.lower()
    for keyword, reply_text in chat_filters.items():
        if keyword in text_lower.split():
            await event.reply(reply_text)
            break


chat_filter_listener.event_filter = events.NewMessage(incoming=True)
