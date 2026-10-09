import calendar
import hashlib
import base64
import mimetypes
import io
import aiohttp
from datetime import datetime, timezone, timedelta
from core.decorators import omni_cmd


@omni_cmd(
    pattern="time",
    desc="Displays current global time across major cities and time zones.",
    usage=".time [city]",
    category="Tools",
    aliases=["clock"]
)
async def time_cmd(event):
    now_utc = datetime.now(timezone.utc)
    
    cities = [
        ("Delhi / Mumbai (IST)", timedelta(hours=5, minutes=30)),
        ("London (GMT/BST)", timedelta(hours=1)),
        ("New York (EDT)", timedelta(hours=-4)),
        ("Tokyo (JST)", timedelta(hours=9)),
        ("Dubai (GST)", timedelta(hours=4)),
        ("Sydney (AEST)", timedelta(hours=10)),
        ("San Francisco (PDT)", timedelta(hours=-7)),
    ]

    lines = ["🌍 **Global World Clock**\n"]
    for city, offset in cities:
        city_time = now_utc + offset
        time_str = city_time.strftime("%I:%M:%S %p (%a)")
        lines.append(f"• **{city}:** `{time_str}`")

    lines.append(f"\n🌐 **UTC Standard:** `{now_utc.strftime('%H:%M:%S UTC')}`")
    await event.reply_or_edit("\n".join(lines))


@omni_cmd(
    pattern="calendar",
    desc="Generates a formatted text calendar for any month and year.",
    usage=".calendar [month] [year] (default: current month)",
    category="Tools"
)
async def calendar_cmd(event):
    now = datetime.now()
    month = now.month
    year = now.year

    args = event.text_args.strip().split()
    if len(args) == 1:
        try:
            month = int(args[0])
        except ValueError:
            pass
    elif len(args) >= 2:
        try:
            month = int(args[0])
            year = int(args[1])
        except ValueError:
            pass

    if not (1 <= month <= 12):
        await event.reply_or_edit("❌ Invalid month. Must be between 1 and 12.")
        return

    cal_text = calendar.month(year, month)
    out = f"📅 **Calendar: {calendar.month_name[month]} {year}**\n\n```{cal_text}```"
    await event.reply_or_edit(out)


@omni_cmd(
    pattern="ss",
    desc="Captures a full screenshot of any web page.",
    usage=".ss <url>",
    category="Tools"
)
async def screenshot_cmd(event):
    url = event.text_args.strip()
    if not url:
        await event.reply_or_edit("⚠️ Usage: `.ss <url>` (e.g. `.ss https://telegram.org`)")
        return

    if not url.startswith("http"):
        url = "https://" + url

    status = await event.reply_or_edit(f"📸 Capturing screenshot of `{url}`...")
    try:
        ss_url = f"https://image.thum.io/get/width/1280/crop/800/noanimate/{url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(ss_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    bio = io.BytesIO(img_bytes)
                    bio.name = "screenshot.png"
                    await event.client.send_file(
                        event.chat_id,
                        bio,
                        caption=f"📸 **Webpage Screenshot**\n`{url}`",
                        reply_to=event.reply_to_msg_id or event.id
                    )
                    await status.delete()
                else:
                    await status.edit("❌ Failed to capture screenshot.")
    except Exception as e:
        await status.edit(f"❌ Screenshot error: `{e}`")


@omni_cmd(
    pattern="stats",
    desc="Computes real-time statistics of dialogs, groups, channels, and unread chats.",
    usage=".stats",
    category="Tools",
    aliases=["count"]
)
async def stats_cmd(event):
    client = event.client
    status = await event.reply_or_edit("⏳ Analyzing Telegram dialogs...")

    try:
        total_dialogs = 0
        private_chats = 0
        groups = 0
        channels = 0
        bots = 0
        unread_chats = 0

        async for dialog in client.iter_dialogs(limit=500):
            total_dialogs += 1
            if dialog.unread_count > 0:
                unread_chats += 1

            if dialog.is_user:
                if getattr(dialog.entity, "bot", False):
                    bots += 1
                else:
                    private_chats += 1
            elif dialog.is_group:
                groups += 1
            elif dialog.is_channel:
                channels += 1

        res = (
            f"📊 **Telegram Account Statistics**\n\n"
            f"• **Total Active Dialogs:** `{total_dialogs}`\n"
            f"• **Private Chats (DMs):** `{private_chats}`\n"
            f"• **Groups & Supergroups:** `{groups}`\n"
            f"• **Broadcast Channels:** `{channels}`\n"
            f"• **Bot Dialogs:** `{bots}`\n"
            f"• **Unread Conversations:** `{unread_chats}`"
        )
        await status.edit(res)
    except Exception as e:
        await status.edit(f"❌ Error computing stats: `{e}`")


@omni_cmd(
    pattern="hash",
    desc="Generates MD5, SHA-1, and SHA-256 cryptographic hashes for text.",
    usage=".hash <text>",
    category="Tools"
)
async def hash_cmd(event):
    text = event.text_args.strip()
    if not text and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        text = reply.raw_text or ""

    if not text:
        await event.reply_or_edit("⚠️ Usage: `.hash <text>`")
        return

    data = text.encode("utf-8")
    md5 = hashlib.md5(data).hexdigest()
    sha1 = hashlib.sha1(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()

    out = (
        f"🔐 **Cryptographic Hashes**\n\n"
        f"• **Input:** `{text[:100]}`\n\n"
        f"• **MD5:** `{md5}`\n"
        f"• **SHA-1:** `{sha1}`\n"
        f"• **SHA-256:** `{sha256}`"
    )
    await event.reply_or_edit(out)


@omni_cmd(
    pattern="base64",
    desc="Encodes or decodes text in Base64 format.",
    usage=".base64 enc <text> or .base64 dec <b64_string>",
    category="Tools"
)
async def base64_cmd(event):
    args = event.text_args.strip().split(maxsplit=1)
    if len(args) < 2:
        await event.reply_or_edit("⚠️ Usage:\n• Encode: `.base64 enc <text>`\n• Decode: `.base64 dec <encoded_string>`")
        return

    mode = args[0].lower()
    content = args[1]

    try:
        if mode in ("enc", "encode"):
            encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            await event.reply_or_edit(f"🔒 **Base64 Encoded:**\n`{encoded}`")
        elif mode in ("dec", "decode"):
            decoded = base64.b64decode(content.encode("utf-8")).decode("utf-8")
            await event.reply_or_edit(f"🔓 **Base64 Decoded:**\n`{decoded}`")
        else:
            await event.reply_or_edit("❌ Invalid mode. Use `enc` or `dec`.")
    except Exception as e:
        await event.reply_or_edit(f"❌ Base64 error: `{e}`")


@omni_cmd(
    pattern="direct",
    desc="Generates direct download links for cloud storage URLs (Google Drive, etc.).",
    usage=".direct <url>",
    category="Tools"
)
async def direct_link_cmd(event):
    url = event.text_args.strip()
    if not url:
        await event.reply_or_edit("⚠️ Usage: `.direct <cloud_url>`")
        return

    # Google Drive transformation
    if "drive.google.com" in url:
        import re
        file_id_match = re.search(r"[-_\w]{25,}", url)
        if file_id_match:
            f_id = file_id_match.group(0)
            direct_url = f"https://drive.google.com/uc?export=download&id={f_id}"
            await event.reply_or_edit(f"🔗 **Direct Google Drive Link:**\n`{direct_url}`")
            return

    await event.reply_or_edit(f"🔗 **Provided URL:**\n`{url}`")


@omni_cmd(
    pattern="fileext",
    desc="Looks up MIME type and details for a file extension.",
    usage=".fileext <extension> (e.g. .fileext mp4)",
    category="Tools"
)
async def file_ext_cmd(event):
    ext = event.text_args.strip().lstrip(".").lower()
    if not ext:
        await event.reply_or_edit("⚠️ Usage: `.fileext <extension>` (e.g. `.fileext pdf`)")
        return

    mime, _ = mimetypes.guess_type(f"file.{ext}")
    out = (
        f"📄 **File Extension:** `.{ext}`\n\n"
        f"• **MIME Type:** `{mime or 'Unknown / Binary'}`\n"
        f"• **Category:** `{'Video' if 'video' in str(mime) else 'Audio' if 'audio' in str(mime) else 'Image' if 'image' in str(mime) else 'Application/Data'}`"
    )
    await event.reply_or_edit(out)
