import asyncio
from telethon.tl.types import ChatBannedRights, ChatAdminRights
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from core.decorators import omni_cmd
from helpers.telegram_tools import get_target_user, parse_time_delta
from config import config


@omni_cmd(
    pattern="del",
    desc="Deletes the replied message.",
    usage=".del (as reply)",
    category="Admin"
)
async def delete_message(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply_or_edit("❌ Reply to a message to delete it.")
        return

    await reply.delete()
    if event.out:
        await event.delete()


@omni_cmd(
    pattern="purge",
    desc="Bulk deletes messages. Reply to start from a message or specify count.",
    usage=".purge <count> or reply to a message",
    category="Admin",
    only_groups=False
)
async def purge_messages(event):
    reply = await event.get_reply_message()
    client = event.client
    chat = event.chat_id

    if reply:
        # Purge from replied message to this message
        start_id = reply.id
        end_id = event.id
        msg_ids = list(range(start_id, end_id + 1))
        
        # Telegram allows batch delete up to 100 at a time
        count = 0
        for i in range(0, len(msg_ids), 100):
            batch = msg_ids[i:i + 100]
            await client.delete_messages(chat, batch)
            count += len(batch)
            await asyncio.sleep(0.2)

        notice = await client.send_message(chat, f"🧹 **Purged {count} messages!**")
        await asyncio.sleep(3)
        await notice.delete()
        return

    # Count-based purge
    args = event.text_args.strip()
    if not args.isdigit():
        await event.reply_or_edit("❌ Specify number of messages to purge or reply to a message.")
        return

    limit = min(int(args), 200)
    messages = await client.get_messages(chat, limit=limit + 1)
    msg_ids = [m.id for m in messages]

    for i in range(0, len(msg_ids), 100):
        batch = msg_ids[i:i + 100]
        await client.delete_messages(chat, batch)
        await asyncio.sleep(0.2)

    notice = await client.send_message(chat, f"🧹 **Purged {len(msg_ids) - 1} messages!**")
    await asyncio.sleep(3)
    await notice.delete()


@omni_cmd(
    pattern="pin",
    desc="Pins the replied message in the chat.",
    usage=".pin [loud] (as reply)",
    category="Admin"
)
async def pin_message(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply_or_edit("❌ Reply to a message to pin it.")
        return

    silent = "loud" not in event.text_args.lower()
    try:
        await event.client.pin_message(event.chat_id, reply.id, notify=not silent)
        await event.reply_or_edit("📌 **Message pinned successfully!**")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ Administrator privileges with pin rights are required in this chat.")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to pin: `{e}`")


@omni_cmd(
    pattern="unpin",
    desc="Unpins the replied message or unpins all messages.",
    usage=".unpin (as reply or .unpin all)",
    category="Admin"
)
async def unpin_message(event):
    try:
        if event.text_args.lower() == "all":
            await event.client.unpin_message(event.chat_id)
            await event.reply_or_edit("📌 **All pinned messages unpinned.**")
            return

        reply = await event.get_reply_message()
        if not reply:
            await event.reply_or_edit("❌ Reply to a pinned message to unpin it.")
            return

        await event.client.unpin_message(event.chat_id, reply.id)
        await event.reply_or_edit("📌 **Message unpinned.**")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ Administrator privileges with pin rights are required in this chat.")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to unpin: `{e}`")


@omni_cmd(
    pattern="ban",
    desc="Bans a user from the group.",
    usage=".ban <user> [reason]",
    category="Admin",
    only_groups=True
)
async def ban_user(event):
    target, reason = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** Reply to user or specify `@username` / `id`.")
        return

    try:
        rights = ChatBannedRights(until_date=None, view_messages=True)
        await event.client.edit_permissions(event.chat_id, target.id, rights)
        reason_text = f"\n**Reason:** {reason}" if reason else ""
        await event.reply_or_edit(f"🔨 **Banned:** [{target.first_name}](tg://user?id={target.id}){reason_text}")
    except (ChatAdminRequiredError, UserAdminInvalidError):
        await event.reply_or_edit("❌ You need administrator permissions with ban rights.")


@omni_cmd(
    pattern="unban",
    desc="Unbans a user in the group.",
    usage=".unban <user>",
    category="Admin",
    only_groups=True
)
async def unban_user(event):
    target, _ = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** Reply to user or specify `@username` / `id`.")
        return

    try:
        rights = ChatBannedRights(until_date=None, view_messages=False)
        await event.client.edit_permissions(event.chat_id, target.id, rights)
        await event.reply_or_edit(f"🕊️ **Unbanned:** [{target.first_name}](tg://user?id={target.id})")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ You need admin permissions to unban.")


@omni_cmd(
    pattern="mute",
    desc="Mutes a user with optional duration (e.g. 10m, 2h, 1d).",
    usage=".mute <user> [duration]",
    category="Admin",
    only_groups=True
)
async def mute_user(event):
    target, duration_str = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** Reply to user or `.mute @username [10m/1h]`.")
        return

    until_date = None
    time_delta = parse_time_delta(duration_str) if duration_str else None
    if time_delta:
        import datetime
        until_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=time_delta)

    try:
        rights = ChatBannedRights(until_date=until_date, send_messages=True)
        await event.client.edit_permissions(event.chat_id, target.id, rights)
        dur_text = f" for `{duration_str}`" if duration_str else " indefinitely"
        await event.reply_or_edit(f"🔇 **Muted:** [{target.first_name}](tg://user?id={target.id}){dur_text}")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ You need admin rights to mute users.")


@omni_cmd(
    pattern="unmute",
    desc="Unmutes a user.",
    usage=".unmute <user>",
    category="Admin",
    only_groups=True
)
async def unmute_user(event):
    target, _ = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** Reply to user or `.unmute @username`.")
        return

    try:
        rights = ChatBannedRights(until_date=None, send_messages=False)
        await event.client.edit_permissions(event.chat_id, target.id, rights)
        await event.reply_or_edit(f"🔊 **Unmuted:** [{target.first_name}](tg://user?id={target.id})")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ Admin privileges required.")


@omni_cmd(
    pattern="kick",
    desc="Kicks a user from the group.",
    usage=".kick <user>",
    category="Admin",
    only_groups=True
)
async def kick_user(event):
    target, _ = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** Reply to user or `.kick @username`.")
        return

    try:
        await event.client.kick_participant(event.chat_id, target.id)
        await event.reply_or_edit(f"👢 **Kicked:** [{target.first_name}](tg://user?id={target.id})")
    except ChatAdminRequiredError:
        await event.reply_or_edit("❌ Admin privileges required to kick.")


@omni_cmd(
    pattern="promote",
    desc="Promotes a user to admin with custom rank title.",
    usage=".promote <user> [custom title]",
    category="Admin",
    only_groups=True
)
async def promote_user(event):
    target, title = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** `.promote <user> [title]`")
        return

    try:
        rights = ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=False,
            manage_call=True,
        )
        await event.client.edit_admin(event.chat_id, target.id, rights, rank=title or "Admin")
        title_text = f" as **{title}**" if title else ""
        await event.reply_or_edit(f"⭐ **Promoted:** [{target.first_name}](tg://user?id={target.id}){title_text}")
    except Exception as e:
        await event.reply_or_edit(f"❌ Could not promote: `{e}`")


@omni_cmd(
    pattern="demote",
    desc="Demotes an admin to normal member.",
    usage=".demote <user>",
    category="Admin",
    only_groups=True
)
async def demote_user(event):
    target, _ = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** `.demote <user>`")
        return

    try:
        rights = ChatAdminRights(
            change_info=False,
            post_messages=False,
            edit_messages=False,
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
        )
        await event.client.edit_admin(event.chat_id, target.id, rights)
        await event.reply_or_edit(f"⬇️ **Demoted:** [{target.first_name}](tg://user?id={target.id})")
    except Exception as e:
        await event.reply_or_edit(f"❌ Could not demote: `{e}`")


@omni_cmd(
    pattern="admins",
    desc="Lists all administrators in the group.",
    usage=".admins",
    category="Admin",
    only_groups=True
)
async def list_admins(event):
    client = event.client
    admins = await client.get_participants(event.chat_id, filter=event.client.participants.types.ChannelParticipantsAdmins)
    out = [f"🛡️ **Administrators in {event.chat.title}** (`{len(admins)}`)\n"]
    for a in admins:
        name = a.first_name or "Deleted"
        bot_tag = "🤖 [Bot] " if a.bot else ""
        out.append(f"• {bot_tag}[{name}](tg://user?id={a.id}) (`{a.id}`)")

    await event.reply_or_edit("\n".join(out))


@omni_cmd(
    pattern="zombies",
    desc="Finds and cleans deleted accounts from the group.",
    usage=".zombies [clean]",
    category="Admin",
    only_groups=True
)
async def clean_zombies(event):
    client = event.client
    clean_mode = "clean" in event.text_args.lower()
    msg = await event.reply_or_edit("🧟 **Scanning for deleted accounts...**")

    zombies = []
    async for user in client.iter_participants(event.chat_id):
        if user.deleted:
            zombies.append(user)

    if not zombies:
        await msg.edit("✅ **Clean!** No deleted accounts found in this group.")
        return

    if not clean_mode:
        await msg.edit(f"🧟 Found **{len(zombies)}** deleted accounts.\nRun `.zombies clean` to remove them.")
        return

    removed = 0
    for z in zombies:
        try:
            await client.kick_participant(event.chat_id, z.id)
            removed += 1
            await asyncio.sleep(0.3)
        except Exception:
            pass

    await msg.edit(f"🧹 **Cleaned {removed} / {len(zombies)} deleted accounts!**")


@omni_cmd(
    pattern="leaveall",
    desc="Leaves all groups and channels that you did not create, preserving your owned chats.",
    usage=".leaveall [preview/groups/channels]",
    category="Admin",
    aliases=["leaveallnonowned", "cleanleft", "purgegroups", "leavegroups", "leavechannels"]
)
async def leave_all_non_owned(event):
    client = event.client
    raw_text = (event.raw_text or "").lower()
    args = event.text_args.lower().strip()
    cmd_name = raw_text.split()[0].lstrip("".join(config.COMMAND_PREFIXES)).lower()

    only_groups = "groups" in args or cmd_name == "leavegroups"
    only_channels = "channels" in args or cmd_name == "leavechannels"
    is_preview = "preview" in args or "list" in args

    msg = await event.reply_or_edit("🔍 **Scanning all joined groups and channels...**")

    to_leave = []
    owned_chats = []

    async for dialog in client.iter_dialogs():
        # Only process channels and groups
        if not (dialog.is_channel or dialog.is_group):
            continue

        # NEVER leave your configured log chat
        if config.LOG_CHAT_ID and dialog.id == config.LOG_CHAT_ID:
            owned_chats.append((dialog.name, dialog.id, "Log Chat"))
            continue

        entity = dialog.entity
        is_creator = getattr(entity, "creator", False)

        # NEVER leave channels or groups created by you
        if is_creator:
            owned_chats.append((dialog.name, dialog.id, "Created by You"))
            continue

        # Filter by type if requested
        if only_groups and not dialog.is_group:
            continue
        if only_channels and dialog.is_group:
            continue

        to_leave.append(dialog)

    if not to_leave:
        await msg.edit(f"✅ **No non-owned chats found to leave.**\n🛡️ **Preserved {len(owned_chats)} owned chats.**")
        return

    if is_preview:
        preview_text = [f"📋 **Found {len(to_leave)} non-owned chats that would be left:**\n"]
        for d in to_leave[:15]:
            chat_type = "Group" if d.is_group else "Channel"
            preview_text.append(f"• [{chat_type}] `{d.name}` (`{d.id}`)")
        if len(to_leave) > 15:
            preview_text.append(f"\n_...and {len(to_leave) - 15} more chats._")
        preview_text.append(f"\n🛡️ **{len(owned_chats)} owned chats are protected.**")
        preview_text.append("\n👉 Run `.leaveall` to execute the rapid leave.")
        await msg.edit("\n".join(preview_text))
        return

    await msg.edit(
        f"🚀 **Leaving {len(to_leave)} non-owned chats...**\n"
        f"🛡️ _Preserving {len(owned_chats)} owned channels/groups._"
    )

    left_count = 0
    failed_count = 0

    for dialog in to_leave:
        try:
            await client.delete_dialog(dialog.entity)
            left_count += 1
            # Rapid 0.2s pause for real-time speed while respecting Telegram limits
            await asyncio.sleep(0.2)
        except Exception as e:
            from telethon.errors import FloodWaitError
            if isinstance(e, FloodWaitError):
                await asyncio.sleep(e.seconds)
                try:
                    await client.delete_dialog(dialog.entity)
                    left_count += 1
                except Exception:
                    failed_count += 1
            else:
                failed_count += 1

    summary = (
        f"🧹 **Cleanup Completed in Rapid Time!**\n\n"
        f"• **Chats Left:** `{left_count}`\n"
        f"• **Failed / Unreachable:** `{failed_count}`\n"
        f"• **Your Owned Chats Preserved:** `{len(owned_chats)}` 🛡️\n"
        f"• **Log Chat Preserved:** `Safe` 🔒"
    )
    await msg.edit(summary)

