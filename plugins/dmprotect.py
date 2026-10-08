import json
from pathlib import Path
from telethon import events
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from core.decorators import omni_cmd
from helpers.telegram_tools import get_target_user
from config import config

DMPROTECT_DATA_FILE = config.BASE_DIR / "dmprotect.json"

# State structure
DMPROTECT_STATE = {
    "enabled": True,
    "mode": "block",  # "block" = DIRECT BLOCK on first DM; "warn" = warn before block
    "max_warns": 3,
    "direct_block_msg": "⛔ **Direct Messages are blocked on this account.** You have been directly blocked.",
    "warn_msg": "⚠️ **DM Notice:** Please do not spam. You have {warns}/{max_warns} warnings before an automatic block.",
    "allowed": set(),
    "warns": {},  # user_id: count
}


def load_state():
    if DMPROTECT_DATA_FILE.exists():
        try:
            data = json.loads(DMPROTECT_DATA_FILE.read_text(encoding="utf-8"))
            DMPROTECT_STATE["enabled"] = data.get("enabled", True)
            DMPROTECT_STATE["mode"] = data.get("mode", "block")
            DMPROTECT_STATE["max_warns"] = data.get("max_warns", 3)
            DMPROTECT_STATE["direct_block_msg"] = data.get(
                "direct_block_msg",
                "⛔ **Direct Messages are blocked on this account.** You have been directly blocked."
            )
            DMPROTECT_STATE["allowed"] = set(data.get("allowed", []))
        except Exception:
            pass


def save_state():
    try:
        data = {
            "enabled": DMPROTECT_STATE["enabled"],
            "mode": DMPROTECT_STATE["mode"],
            "max_warns": DMPROTECT_STATE["max_warns"],
            "direct_block_msg": DMPROTECT_STATE["direct_block_msg"],
            "allowed": list(DMPROTECT_STATE["allowed"]),
        }
        DMPROTECT_DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


load_state()


@omni_cmd(
    pattern="dmprotect",
    desc="Controls DM Protection & Direct Block system.",
    usage=".dmprotect <on/off/mode/msg/status>\nExample: .dmprotect mode block",
    category="Security",
    aliases=["antipm", "pmpermit"]
)
async def dm_protect_control(event):
    args = event.text_args.strip().split(maxsplit=1)
    sub = args[0].lower() if args else "status"

    if sub == "on":
        DMPROTECT_STATE["enabled"] = True
        save_state()
        mode_desc = "DIRECT BLOCK on 1st message" if DMPROTECT_STATE["mode"] == "block" else "Warning Mode"
        await event.reply_or_edit(f"🛡️ **DM Protect Enabled!**\nMode: `{mode_desc}`")

    elif sub == "off":
        DMPROTECT_STATE["enabled"] = False
        save_state()
        await event.reply_or_edit("🔓 **DM Protect Disabled!** Anyone can send direct messages.")

    elif sub == "mode":
        if len(args) > 1 and args[1].lower() in ("block", "direct", "strict"):
            DMPROTECT_STATE["mode"] = "block"
            save_state()
            await event.reply_or_edit("⚡ **DM Protect Mode:** `DIRECT BLOCK` 🚫\n_Anyone unauthorized who DMs will be blocked instantly on first message!_")
        elif len(args) > 1 and args[1].lower() in ("warn", "warning"):
            DMPROTECT_STATE["mode"] = "warn"
            save_state()
            await event.reply_or_edit(f"⚠️ **DM Protect Mode:** `WARNING MODE`\n_Users receive up to {DMPROTECT_STATE['max_warns']} warnings before being blocked._")
        else:
            await event.reply_or_edit("💡 **Usage:** `.dmprotect mode block` (direct block) or `.dmprotect mode warn`")

    elif sub == "msg":
        if len(args) > 1 and args[1].strip():
            new_msg = args[1].strip()
            DMPROTECT_STATE["direct_block_msg"] = new_msg
            save_state()
            await event.reply_or_edit(f"✅ **Direct Block Message Updated:**\n_{new_msg}_")
        else:
            await event.reply_or_edit("💡 **Usage:** `.dmprotect msg <custom rejection message>`")

    else:
        status = "Active 🟢" if DMPROTECT_STATE["enabled"] else "Disabled 🔴"
        mode_text = "⚡ DIRECT BLOCK (Instant)" if DMPROTECT_STATE["mode"] == "block" else f"⚠️ Warning Mode ({DMPROTECT_STATE['max_warns']} warns)"
        count = len(DMPROTECT_STATE["allowed"])
        await event.reply_or_edit(
            f"🛡️ **DM Protect Status Overview**\n\n"
            f"• **Status:** `{status}`\n"
            f"• **Protection Mode:** `{mode_text}`\n"
            f"• **Allowed / Whitelisted Users:** `{count}`\n"
            f"• **Block Message:** _{DMPROTECT_STATE['direct_block_msg']}_\n\n"
            f"💡 **Commands:**\n"
            f"• `.dmprotect on` / `.dmprotect off`\n"
            f"• `.dmprotect mode block` (Instantly blocks unknown DMs)\n"
            f"• `.dmprotect mode warn` (Gives warnings before block)\n"
            f"• `.allow <user>` (Whitelists user to DM freely)\n"
            f"• `.disallow <user>` (Removes user from whitelist)\n"
            f"• `.allowed` (Lists all whitelisted users)"
        )


@omni_cmd(
    pattern="allow",
    desc="Adds user to the allowed whitelist so they can DM you freely.",
    usage=".allow [user or reply or in PM]",
    category="Security",
    aliases=["approve", "a", "whitelist"]
)
async def allow_user(event):
    target, _ = await get_target_user(event)
    if not target and event.is_private:
        target = await event.get_chat()

    if not target:
        await event.reply_or_edit("❌ Specify user (@username or ID) or run command in private chat.")
        return

    DMPROTECT_STATE["allowed"].add(target.id)
    DMPROTECT_STATE["warns"].pop(target.id, None)
    save_state()
    name = getattr(target, "first_name", "User")
    await event.reply_or_edit(f"✅ **Allowed:** [{name}](tg://user?id={target.id}) (`{target.id}`) is added to whitelist and can DM freely.")


@omni_cmd(
    pattern="disallow",
    desc="Removes a user from the allowed whitelist.",
    usage=".disallow [user or reply or in PM]",
    category="Security",
    aliases=["disapprove", "da", "unwhitelist"]
)
async def disallow_user(event):
    target, _ = await get_target_user(event)
    if not target and event.is_private:
        target = await event.get_chat()

    if not target:
        await event.reply_or_edit("❌ Specify user (@username or ID) or run command in private chat.")
        return

    DMPROTECT_STATE["allowed"].discard(target.id)
    save_state()
    name = getattr(target, "first_name", "User")
    await event.reply_or_edit(f"⛔ **Disallowed:** [{name}](tg://user?id={target.id}) removed from whitelist. DM Protect will now apply.")


@omni_cmd(
    pattern="allowed",
    desc="Lists all users currently allowed to send direct messages.",
    usage=".allowed",
    category="Security",
    aliases=["allowlist", "whitelisted"]
)
async def list_allowed_users(event):
    if not DMPROTECT_STATE["allowed"]:
        await event.reply_or_edit("📋 No users in allowlist yet. Use `.allow <user>` to whitelist someone.")
        return

    out = [f"📋 **Allowed Users Whitelist (`{len(DMPROTECT_STATE['allowed'])}`):**\n"]
    for uid in sorted(DMPROTECT_STATE["allowed"]):
        out.append(f"• [User](tg://user?id={uid}) (`{uid}`)")

    await event.reply_or_edit("\n".join(out))


@omni_cmd(
    pattern="block",
    desc="Directly blocks a user on Telegram.",
    usage=".block [user or reply]",
    category="Security"
)
async def block_user(event):
    target, _ = await get_target_user(event)
    if not target and event.is_private:
        target = await event.get_chat()

    if not target:
        await event.reply_or_edit("❌ Specify target user to block.")
        return

    try:
        await event.client(BlockRequest(target.id))
        DMPROTECT_STATE["allowed"].discard(target.id)
        save_state()
        await event.reply_or_edit(f"🚫 **Blocked:** [{getattr(target, 'first_name', 'User')}](tg://user?id={target.id})")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to block: `{e}`")


@omni_cmd(
    pattern="unblock",
    desc="Unblocks a user on Telegram.",
    usage=".unblock <user>",
    category="Security"
)
async def unblock_user(event):
    target, _ = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ Specify user to unblock.")
        return

    try:
        await event.client(UnblockRequest(target.id))
        await event.reply_or_edit(f"🕊️ **Unblocked:** [{getattr(target, 'first_name', 'User')}](tg://user?id={target.id})")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to unblock: `{e}`")


# Incoming DM Listener
@events.register(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def dm_protect_incoming_listener(event):
    if not DMPROTECT_STATE["enabled"]:
        return

    sender = await event.get_sender()
    if not sender or sender.bot or sender.is_self:
        return

    # Whitelist checks: Allowed list, Contact, Sudo
    if (
        sender.id in DMPROTECT_STATE["allowed"]
        or sender.contact
        or sender.id in config.SUDO_USERS
    ):
        return

    # DIRECT BLOCK MODE
    if DMPROTECT_STATE["mode"] == "block":
        try:
            # Send block message
            await event.reply(DMPROTECT_STATE["direct_block_msg"])
            # Instantly block user
            await event.client(BlockRequest(sender.id))
        except Exception:
            pass
        return

    # WARNING MODE
    warns = DMPROTECT_STATE["warns"].get(sender.id, 0) + 1
    DMPROTECT_STATE["warns"][sender.id] = warns
    max_warns = DMPROTECT_STATE["max_warns"]

    if warns >= max_warns:
        try:
            await event.reply("🚫 **Spam limit exceeded.** You have been automatically blocked.")
            await event.client(BlockRequest(sender.id))
        except Exception:
            pass
        return

    # Send warning
    msg_text = (
        f"⚠️ **DM Notice from OmniUserBot**\n\n"
        f"Hello [{sender.first_name}](tg://user?id={sender.id}), direct messages are restricted.\n"
        f"Do not spam. You have **{warns}/{max_warns}** warnings before being blocked."
    )
    await event.reply(msg_text)
