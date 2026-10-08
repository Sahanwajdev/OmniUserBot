import os
import json
from pathlib import Path
from telethon import utils
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from core.decorators import omni_cmd
from helpers.telegram_tools import get_target_user
from config import config

PROFILE_BACKUP_FILE = config.BASE_DIR / "profile_backup.json"
SAVED_ORIGINAL_PROFILE = {}


def load_backup():
    global SAVED_ORIGINAL_PROFILE
    if PROFILE_BACKUP_FILE.exists():
        try:
            SAVED_ORIGINAL_PROFILE = json.loads(PROFILE_BACKUP_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass


def save_backup():
    try:
        PROFILE_BACKUP_FILE.write_text(json.dumps(SAVED_ORIGINAL_PROFILE, indent=2), encoding="utf-8")
    except Exception:
        pass


def clear_backup():
    global SAVED_ORIGINAL_PROFILE
    SAVED_ORIGINAL_PROFILE = {}
    if PROFILE_BACKUP_FILE.exists():
        try:
            PROFILE_BACKUP_FILE.unlink()
        except Exception:
            pass


load_backup()


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
    if "first_name" not in SAVED_ORIGINAL_PROFILE and not PROFILE_BACKUP_FILE.exists():
        me = await client.get_me()
        me_full = await client(GetFullUserRequest(me.id))
        SAVED_ORIGINAL_PROFILE["first_name"] = me.first_name or ""
        SAVED_ORIGINAL_PROFILE["last_name"] = me.last_name or ""
        SAVED_ORIGINAL_PROFILE["about"] = me_full.full_user.about or ""
        SAVED_ORIGINAL_PROFILE["cloned_photo_ids"] = []
        save_backup()

    try:
        target_full = await client(GetFullUserRequest(target.id))
        first_name = target.first_name or ""
        last_name = target.last_name or ""
        about = target_full.full_user.about or ""

        # Update name & bio
        await client(UpdateProfileRequest(first_name=first_name, last_name=last_name, about=about))

        # Update photo if target has one
        photos = await client.get_profile_photos(target.id, limit=1)
        photo_cloned = False
        if photos:
            pfp_path = config.DOWNLOAD_DIR / f"clone_pfp_{target.id}.jpg"
            await client.download_media(photos[0], file=str(pfp_path))
            uploaded = await client.upload_file(str(pfp_path))
            upload_res = await client(UploadProfilePhotoRequest(file=uploaded))
            photo_cloned = True

            # Track newly uploaded cloned photo ID for automatic deletion upon revert
            if hasattr(upload_res, "photo") and upload_res.photo:
                SAVED_ORIGINAL_PROFILE.setdefault("cloned_photo_ids", []).append(upload_res.photo.id)
            SAVED_ORIGINAL_PROFILE["photo_cloned"] = True
            save_backup()

            if pfp_path.exists():
                os.remove(pfp_path)

        pfp_text = " (with profile photo)" if photo_cloned else ""
        await msg.edit(f"🎭 **Profile Cloned!**{pfp_text}\n💡 Use `.revert` anytime to restore original name, bio, and auto-delete cloned photo.")
    except Exception as e:
        await msg.edit(f"❌ Clone failed: `{e}`")


@omni_cmd(
    pattern="revert",
    desc="Restores your original profile name, bio, and automatically deletes cloned profile photo.",
    usage=".revert",
    category="Profile",
    aliases=["restoreprofile", "unclone"]
)
async def revert_profile(event):
    load_backup()
    client = event.client

    if "first_name" not in SAVED_ORIGINAL_PROFILE and not PROFILE_BACKUP_FILE.exists():
        await event.reply_or_edit("❌ No saved original profile state to revert to.")
        return

    msg = await event.reply_or_edit("🔄 **Restoring original profile & deleting cloned photo...**")
    deleted_photos = 0

    try:
        # 1. Automatically delete the cloned profile photo(s)
        cloned_ids = set(SAVED_ORIGINAL_PROFILE.get("cloned_photo_ids", []))
        my_photos = await client.get_profile_photos("me", limit=10)

        to_delete = []
        if my_photos:
            if cloned_ids:
                for p in my_photos:
                    if p.id in cloned_ids:
                        to_delete.append(utils.get_input_photo(p))

            # Fallback: If cloned photo was uploaded but exact ID missed, delete the top active photo
            if not to_delete and SAVED_ORIGINAL_PROFILE.get("photo_cloned", False):
                to_delete.append(utils.get_input_photo(my_photos[0]))

        if to_delete:
            try:
                await client(DeletePhotosRequest(id=to_delete))
                deleted_photos = len(to_delete)
            except Exception as e:
                from core.logger import log
                log.error(f"Failed to delete cloned photo: {e}")

        # 2. Restore original name & bio
        orig_first = SAVED_ORIGINAL_PROFILE.get("first_name", "")
        orig_last = SAVED_ORIGINAL_PROFILE.get("last_name", "")
        orig_about = SAVED_ORIGINAL_PROFILE.get("about", "")

        await client(UpdateProfileRequest(
            first_name=orig_first,
            last_name=orig_last,
            about=orig_about
        ))

        # 3. Clear backup
        clear_backup()

        photo_status = f" Cloned profile photo was automatically deleted ({deleted_photos} photo)." if deleted_photos else " Profile picture restored."
        await msg.edit(
            f"✅ **Original Profile Restored!**\n\n"
            f"• **Name:** `{orig_first} {orig_last}`\n"
            f"• **Bio:** _{orig_about or 'None'}_\n"
            f"• **Profile Photo:** {photo_status}"
        )
    except Exception as e:
        await msg.edit(f"❌ Failed to revert: `{e}`")


@omni_cmd(
    pattern="delpfp",
    desc="Deletes your current Telegram profile photo.",
    usage=".delpfp [count]",
    category="Profile",
    aliases=["delphoto", "rmpfp"]
)
async def delete_profile_photo(event):
    client = event.client
    args = event.text_args.strip()
    count = int(args) if args.isdigit() else 1
    count = min(count, 10)

    my_photos = await client.get_profile_photos("me", limit=count)
    if not my_photos:
        await event.reply_or_edit("❌ You have no profile photos to delete.")
        return

    to_delete = [utils.get_input_photo(p) for p in my_photos]
    try:
        await client(DeletePhotosRequest(id=to_delete))
        await event.reply_or_edit(f"🗑️ **Deleted {len(to_delete)} profile photo(s) successfully!**")
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to delete profile photo: `{e}`")
