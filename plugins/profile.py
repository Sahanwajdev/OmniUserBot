import os
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from core.decorators import omni_cmd
from helpers.telegram_tools import get_target_user
from config import config

SAVED_ORIGINAL_PROFILE = {}


@omni_cmd(
    pattern="setname",
    desc="Changes your Telegram display name.",
    usage=".setname <first_name> [last_name]",
    category="Profile"
)
async def set_name(event):
    parts = event.text_args.split(maxsplit=1)
    if not parts:
        await event.reply_or_edit("👤 **Usage:** `.setname <first_name> [last_name]`")
        return

    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""

    try:
        await event.client(UpdateProfileRequest(first_name=first_name, last_name=last_name))
        await event.reply_or_edit(f"✅ Name updated to: **{first_name} {last_name}**")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to update name: `{e}`")


@omni_cmd(
    pattern="setbio",
    desc="Changes your Telegram about / biography.",
    usage=".setbio <text>",
    category="Profile"
)
async def set_bio(event):
    bio_text = event.text_args.strip()
    if not bio_text:
        await event.reply_or_edit("📝 **Usage:** `.setbio <biography text>`")
        return

    try:
        await event.client(UpdateProfileRequest(about=bio_text))
        await event.reply_or_edit(f"✅ Bio updated to:\n_{bio_text}_")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to update bio: `{e}`")


@omni_cmd(
    pattern="setpfp",
    desc="Sets replied image as your Telegram profile photo.",
    usage=".setpfp (as reply to photo)",
    category="Profile"
)
async def set_profile_photo(event):
    reply = await event.get_reply_message()
    if not reply or not (reply.photo or reply.media):
        await event.reply_or_edit("❌ Reply to a photo or image to set it as profile picture.")
        return

    msg = await event.reply_or_edit("🔄 **Uploading profile photo...**")
    file_path = config.DOWNLOAD_DIR / f"pfp_{event.id}.jpg"
    try:
        await reply.download_media(file=str(file_path))
        uploaded = await event.client.upload_file(str(file_path))
        await event.client(UploadProfilePhotoRequest(file=uploaded))
        await msg.edit("✅ **Profile photo updated successfully!**")
    except Exception as e:
        await msg.edit(f"❌ Failed to set profile picture: `{e}`")
    finally:
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception:
                pass


@omni_cmd(
    pattern="clone",
    desc="Temporarily clones target user's profile (name, bio, photo).",
    usage=".clone <user or reply>",
    category="Profile"
)
async def clone_user_profile(event):
    target, _ = await get_target_user(event)
    if not target:
        await event.reply_or_edit("❌ **Usage:** Reply to user or specify `@username`.")
        return

    msg = await event.reply_or_edit(f"🎭 **Cloning profile of:** [{target.first_name}](tg://user?id={target.id})...")
    client = event.client

    # Save original if not already saved
    if "first_name" not in SAVED_ORIGINAL_PROFILE:
        me = await client.get_me()
        me_full = await client(GetFullUserRequest(me.id))
        SAVED_ORIGINAL_PROFILE["first_name"] = me.first_name or ""
        SAVED_ORIGINAL_PROFILE["last_name"] = me.last_name or ""
        SAVED_ORIGINAL_PROFILE["about"] = me_full.full_user.about or ""

    try:
        target_full = await client(GetFullUserRequest(target.id))
        first_name = target.first_name or ""
        last_name = target.last_name or ""
        about = target_full.full_user.about or ""

        # Update name & bio
        await client(UpdateProfileRequest(first_name=first_name, last_name=last_name, about=about))

        # Update photo if target has one
        photos = await client.get_profile_photos(target.id, limit=1)
        if photos:
            pfp_path = config.DOWNLOAD_DIR / f"clone_pfp_{target.id}.jpg"
            await client.download_media(photos[0], file=str(pfp_path))
            uploaded = await client.upload_file(str(pfp_path))
            await client(UploadProfilePhotoRequest(file=uploaded))
            if pfp_path.exists():
                os.remove(pfp_path)

        await msg.edit(f"🎭 **Profile Cloned!** Use `.revert` anytime to restore original profile.")
    except Exception as e:
        await msg.edit(f"❌ Clone failed: `{e}`")


@omni_cmd(
    pattern="revert",
    desc="Restores your original profile name and bio after cloning.",
    usage=".revert",
    category="Profile"
)
async def revert_profile(event):
    if "first_name" not in SAVED_ORIGINAL_PROFILE:
        await event.reply_or_edit("❌ No saved original profile state to revert to.")
        return

    msg = await event.reply_or_edit("🔄 **Restoring original profile...**")
    try:
        await event.client(UpdateProfileRequest(
            first_name=SAVED_ORIGINAL_PROFILE["first_name"],
            last_name=SAVED_ORIGINAL_PROFILE["last_name"],
            about=SAVED_ORIGINAL_PROFILE["about"]
        ))
        await msg.edit("✅ **Original profile restored!**")
    except Exception as e:
        await msg.edit(f"❌ Failed to revert: `{e}`")
