import asyncio
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.messages import GetCommonChatsRequest
from core.decorators import omni_cmd


@omni_cmd(
    pattern="whois",
    desc="Fetches comprehensive profile details and Telegram metadata for a user.",
    usage=".whois [username/ID] or reply to user",
    category="Tools",
    aliases=["info"]
)
async def whois_cmd(event):
    client = event.client
    user = None
    args = event.text_args.strip()

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user = await reply.get_sender()
    elif args:
        try:
            target = int(args) if args.lstrip("-").isdigit() else args
            user = await client.get_entity(target)
        except Exception as e:
            await event.reply_or_edit(f"❌ User not found: `{e}`")
            return
    else:
        user = client.me or await client.get_me()

    if not user:
        await event.reply_or_edit("❌ Unable to locate target user.")
        return

    status = await event.reply_or_edit("🔍 Inspecting profile...")
    try:
        full_user = await client(GetFullUserRequest(user.id))
        full = full_user.full_user

        # Profile photos count
        photos = await client(GetUserPhotosRequest(user_id=user.id, offset=0, max_id=0, limit=1))
        photos_count = photos.count if hasattr(photos, "count") else len(getattr(photos, "photos", []))

        # Common chats count
        common_chats = await client(GetCommonChatsRequest(user_id=user.id, max_id=0, limit=100))
        common_count = len(common_chats.chats) if hasattr(common_chats, "chats") else 0

        first_name = user.first_name or "None"
        last_name = user.last_name or "None"
        username = f"@{user.username}" if user.username else "No Username"
        user_id = user.id
        dc_id = getattr(getattr(user, "photo", None), "dc_id", "Unknown")
        bio = full.about or "No Bio Available"
        is_bot = "Yes" if user.bot else "No"
        is_verified = "Yes" if user.verified else "No"
        is_premium = "Yes" if getattr(user, "premium", False) else "No"
        is_restricted = "Yes" if user.restricted else "No"
        permanent_link = f"[Profile Link](tg://user?id={user_id})"

        msg = (
            f"👤 **User Information: [{first_name}](tg://user?id={user_id})**\n\n"
            f"• **First Name:** `{first_name}`\n"
            f"• **Last Name:** `{last_name}`\n"
            f"• **Username:** {username}\n"
            f"• **Telegram ID:** `{user_id}`\n"
            f"• **Data Center:** `DC {dc_id}`\n"
            f"• **Permanent Link:** {permanent_link}\n"
            f"• **Profile Photos:** `{photos_count}`\n"
            f"• **Common Chats:** `{common_count}`\n"
            f"• **Telegram Premium:** `{is_premium}`\n"
            f"• **Verified Account:** `{is_verified}`\n"
            f"• **Bot Account:** `{is_bot}`\n"
            f"• **Restricted:** `{is_restricted}`\n\n"
            f"📝 **About / Bio:**\n_{bio}_"
        )
        await status.edit(msg, link_preview=False)
    except Exception as e:
        await status.edit(f"❌ Error fetching user info: `{e}`")


@omni_cmd(
    pattern="sg",
    desc="Searches SangMata for name and username changes history.",
    usage=".sg [user] or reply to user",
    category="Tools"
)
async def sangmata_cmd(event):
    client = event.client
    user = None
    args = event.text_args.strip()

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user = await reply.get_sender()
    elif args:
        try:
            target = int(args) if args.lstrip("-").isdigit() else args
            user = await client.get_entity(target)
        except Exception:
            user = None
    else:
        user = client.me

    if not user:
        await event.reply_or_edit("⚠️ Please specify a user or reply to a message.")
        return

    status = await event.reply_or_edit("⏳ Querying SangMata history...")
    try:
        # Query via SangMata bot conversation
        async with client.conversation("@SangMata_BOT", timeout=10) as conv:
            await conv.send_message(f"/search_id {user.id}")
            response = await conv.get_response()
            await conv.mark_read()
            if response and response.text:
                await status.edit(f"📜 **SangMata History for [{user.first_name}](tg://user?id={user.id})**:\n\n{response.text}")
            else:
                await status.edit(f"ℹ️ No recorded name changes found for `{user.id}`.")
    except Exception as e:
        # Graceful fallback showing basic user identity
        await status.edit(f"ℹ️ SangMata query unavailable: `{e}`\n\nUser ID: `{user.id}` | First Name: `{user.first_name}`")
