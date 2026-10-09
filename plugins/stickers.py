import io
import os
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
from core.decorators import omni_cmd


def _create_text_sticker(text: str, color: str = "#FFFFFF", bg_color=None) -> io.BytesIO:
    # 512x512 canvas for Telegram stickers
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    lines = []
    words = text.split()
    cur = ""
    for w in words:
        if len(cur + " " + w) <= 20:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    total_h = len(lines) * 36
    y = max(40, (512 - total_h) // 2)

    for line in lines:
        draw.text((40, y), line, fill=color)
        y += 36

    bio = io.BytesIO()
    bio.name = "sticker.webp"
    img.save(bio, format="WEBP")
    bio.seek(0)
    return bio


@omni_cmd(
    pattern="sticklet",
    desc="Transforms text into a Telegram sticker.",
    usage=".sticklet <text> or reply to message",
    category="Fun",
    aliases=["srgb"]
)
async def sticklet_cmd(event):
    text = event.text_args.strip()
    if not text and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        text = reply.raw_text or ""

    if not text:
        await event.reply_or_edit("⚠️ Usage: `.sticklet <text>`")
        return

    color = "#FF007F" if "srgb" in event.raw_text else "#FFFFFF"
    bio = _create_text_sticker(text, color=color)

    await event.client.send_file(
        event.chat_id,
        bio,
        reply_to=event.reply_to_msg_id or event.id
    )
    if event.out:
        await event.delete()


@omni_cmd(
    pattern="q",
    desc="Converts replied message into a quote sticker.",
    usage=".q (reply to message)",
    category="Fun",
    aliases=["quotly"]
)
async def quote_cmd(event):
    if not event.reply_to_msg_id:
        await event.reply_or_edit("⚠️ Reply to a message to generate a quote sticker.")
        return

    reply = await event.get_reply_message()
    text = reply.raw_text or (reply.file.name if reply.file else "Media Message")
    sender = await reply.get_sender()
    sender_name = getattr(sender, "first_name", "User") or "User"

    status = await event.reply_or_edit("🎨 Generating quote sticker...")
    quote_text = f"\"{text}\"\n\n— {sender_name}"
    bio = _create_text_sticker(quote_text, color="#FFD700")

    await event.client.send_file(
        event.chat_id,
        bio,
        reply_to=reply.id
    )
    await status.delete()


@omni_cmd(
    pattern="packinfo",
    desc="Retrieves information about the replied sticker pack.",
    usage=".packinfo (reply to a sticker)",
    category="Fun"
)
async def packinfo_cmd(event):
    if not event.reply_to_msg_id:
        await event.reply_or_edit("⚠️ Reply to a sticker to get pack information.")
        return

    reply = await event.get_reply_message()
    if not reply.sticker:
        await event.reply_or_edit("⚠️ The replied message is not a sticker.")
        return

    status = await event.reply_or_edit("⏳ Fetching sticker pack info...")
    try:
        set_attr = next((a for a in reply.document.attributes if hasattr(a, "stickerset")), None)
        if not set_attr or not set_attr.stickerset:
            await status.edit("❌ This sticker does not belong to a public pack.")
            return

        sticker_set = await event.client(GetStickerSetRequest(set_attr.stickerset))
        s_set = sticker_set.set

        info = (
            f"📦 **Sticker Pack Information**\n\n"
            f"• **Title:** `{s_set.title}`\n"
            f"• **Short Name:** `{s_set.short_name}`\n"
            f"• **Total Stickers:** `{s_set.count}`\n"
            f"• **Animated:** `{'Yes' if s_set.animated else 'No'}`\n"
            f"• **Video:** `{'Yes' if getattr(s_set, 'videos', False) else 'No'}`\n"
            f"• **Pack Link:** https://t.me/addstickers/{s_set.short_name}"
        )
        await status.edit(info)
    except Exception as e:
        await status.edit(f"❌ Failed to fetch pack info: `{e}`")
