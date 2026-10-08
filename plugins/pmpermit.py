import json
from pathlib import Path
from telethon import events
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from core.decorators import omni_cmd
from helpers.telegram_tools import get_target_user
from config import config

PMPERMIT_DATA_FILE = config.BASE_DIR / "pmpermit.json"

# State structure
PMPERMIT_STATE = {
    "enabled": True,
    "max_warns": 4,
    "approved": set(),
    "warns": {},  # user_id: count
}


def load_pmpermit():
    if PMPERMIT_DATA_FILE.exists():
        try:
            data = json.loads(PMPERMIT_DATA_FILE.read_text(encoding="utf-8"))
            PMPERMIT_STATE["enabled"] = data.get("enabled", True)
            PMPERMIT_STATE["approved"] = set(data.get("approved", []))
        except Exception:
            pass


def save_pmpermit():
    try:
        data = {
            "enabled": PMPERMIT_STATE["enabled"],
            "approved": list(PMPERMIT_STATE["approved"]),
        }
        PMPERMIT_DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


load_pmpermit()


@omni_cmd(
    pattern="pmpermit",
    desc="Enables or disables PM Security Guardian.",
    usage=".pmpermit <on/off/status>",
    category="Security"
)
async def toggle_pmpermit(event):
    arg = event.text_args.lower().strip()
    if arg == "on":
        PMPERMIT_STATE["enabled"] = True
        save_pmpermit()
        await event.reply_or_edit("🛡️ **PMPermit Guardian Enabled!** Unapproved users will be restricted.")
    elif arg == "off":
        PMPERMIT_STATE["enabled"] = False
        save_pmpermit()
        await event.reply_or_edit("🔓 **PMPermit Guardian Disabled!** Anyone can send direct messages.")
    else:
        status = "Active 🟢" if PMPERMIT_STATE["enabled"] else "Disabled 🔴"
        count = len(PMPERMIT_STATE["approved"])
        await event.reply_or_edit(
            f"🛡️ **PMPermit Guardian Status:** `{status}`\n"
            f"• **Approved Users:** `{count}`\n"
            f"• **Max Warnings:** `{PMPERMIT_STATE['max_warns']}`\n\n"
            f"💡 **Usage:** `.pmpermit on` or `.pmpermit off`"
        )


@omni_cmd(
    pattern="approve",
    desc="Approves a user to send private messages.",
    usage=".approve (in PM or reply or with ID)",
    category="Security",
    aliases=["a"]
)
async def approve_user(event):
    target, _ = await get_target_user(event)
    if not target and event.is_private:
        target = await event.get_chat()

    if not target:
        await event.reply_or_edit("❌ Specify user or run inside private chat.")
        return

    PMPERMIT_STATE["approved"].add(target.id)
    PMPERMIT_STATE["warns"].pop(target.id, None)
    save_pmpermit()
    await event.reply_or_edit(f"✅ **Approved:** [{getattr(target, 'first_name', 'User')}](tg://user?id={target.id}) can now PM freely.")


@omni_cmd(
    pattern="disapprove",
    desc="Disapproves a previously approved user.",
    usage=".disapprove (in PM or reply or with ID)",
    category="Security",
    aliases=["da"]
)
async def disapprove_user(event):
    target, _ = await get_target_user(event)
    if not target and event.is_private:
        target = await event.get_chat()

    if not target:
        await event.reply_or_edit("❌ Specify user or run inside private chat.")
        return

    PMPERMIT_STATE["approved"].discard(target.id)
    save_pmpermit()
    await event.reply_or_edit(f"⛔ **Disapproved:** [{getattr(target, 'first_name', 'User')}](tg://user?id={target.id}) is now subject to PMPermit guard.")


@omni_cmd(
    pattern="block",
    desc="Blocks a user on Telegram.",
    usage=".block [user or reply or in PM]",
    category="Security"
)
async def block_user_cmd(event):
    target, _ = await get_target_user(event)
    if not target and event.is_private:
        target = await event.get_chat()

    if not target:
        await event.reply_or_edit("❌ Specify user or run inside private chat.")
        return

    try:
        await event.client(BlockRequest(target.id))
        PMPERMIT_STATE["approved"].discard(target.id)
        save_pmpermit()
        await event.reply_or_edit(f"🚫 **Blocked:** [{getattr(target, 'first_name', 'User')}](tg://user?id={target.id})")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to block: `{e}`")


@omni_cmd(
    pattern="unblock",
    desc="Unblocks a user on Telegram.",
    usage=".unblock [user or reply]",
    category="Security"
)
async def unblock_user_cmd(event):
    target, _ = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ Specify user or user ID.")
        return

    try:
        await event.client(UnblockRequest(target.id))
        await event.reply_or_edit(f"🕊️ **Unblocked:** [{getattr(target, 'first_name', 'User')}](tg://user?id={target.id})")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to unblock: `{e}`")


# Incoming PM listener
@events.register(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def pmpermit_incoming_handler(event):
    if not PMPERMIT_STATE["enabled"]:
        return

    sender = await event.get_sender()
    if not sender or sender.bot or sender.is_self:
        return

    # Check if approved or contact or sudo
    if sender.id in PMPERMIT_STATE["approved"] or sender.contact or sender.id in config.SUDO_USERS:
        return

    warn_count = PMPERMIT_STATE["warns"].get(sender.id, 0) + 1
    PMPERMIT_STATE["warns"][sender.id] = warn_count
    max_warns = PMPERMIT_STATE["max_warns"]

    if warn_count >= max_warns:
        try:
            await event.reply(
                "🚫 **Spam limit exceeded.** You have been automatically blocked by OmniUserBot Security Guardian."
            )
            await event.client(BlockRequest(sender.id))
        except Exception:
            pass
        return

    await event.reply(
        f"⚠️ **OmniUserBot PM Guardian Notice**\n\n"
        f"Hello [{sender.first_name}](tg://user?id={sender.id}), this account is protected.\n"
        f"Please state your purpose clearly and **do not spam** until approved.\n\n"
        f"🚨 **Warning:** `{warn_count} / {max_warns}` (Exceeding limit will result in an automatic block)."
    )
