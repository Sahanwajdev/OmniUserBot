import os
import io
import asyncio
from pathlib import Path
from telethon import events
from PIL import Image
import yt_dlp

from core.decorators import omni_cmd
from helpers.formatting import progress_bar, format_bytes, format_time
from config import config


@omni_cmd(
    pattern="yt",
    desc="Searches YouTube for videos with duration and link.",
    usage=".yt <query>",
    category="Media",
    aliases=["youtube"]
)
async def youtube_search(event):
    query = event.text_args.strip()
    if not query:
        await event.reply_or_edit("🎥 **Usage:** `.yt <search query>`")
        return

    msg = await event.reply_or_edit(f"🎥 **Searching YouTube for:** `{query}`...")

    def search_sync():
        ydl_opts = {"quiet": True, "extract_flat": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"ytsearch5:{query}", download=False)

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, search_sync)
        entries = info.get("entries", [])
        if not entries:
            await msg.edit(f"❌ No YouTube videos found for: `{query}`")
            return

        out = [f"🎥 **YouTube Results for:** `{query}`\n"]
        for i, v in enumerate(entries[:5], 1):
            title = v.get("title", "Video")
            url = v.get("url") or f"https://www.youtube.com/watch?v={v.get('id')}"
            dur = format_time(v.get("duration", 0)) if v.get("duration") else "Live/Unknown"
            uploader = v.get("uploader", "Unknown Channel")
            out.append(f"**{i}. [{title}]({url})**\n⏱️ `{dur}` | 👤 `{uploader}`\n")

        await msg.edit("\n".join(out), link_preview=False)
    except Exception as e:
        await msg.edit(f"❌ YouTube Search error: `{e}`")


@omni_cmd(
    pattern="ytdl",
    desc="Downloads YouTube video or audio by URL or song name using yt-dlp.",
    usage=".ytdl <url or search query> [audio/video]",
    category="Media",
    aliases=["ytdlp", "song", "video", "yta"]
)
async def youtube_download(event):
    query = event.text_args.strip()
    if not query:
        await event.reply_or_edit("📥 **Usage:** `.ytdl <url or song name>`\nExamples:\n• `.ytdl tum hi ho`\n• `.ytdl https://youtu.be/... audio`")
        return

    # Check if audio format requested
    cmd_name = (event.raw_text or "").split()[0].lstrip("".join(config.COMMAND_PREFIXES)).lower()
    is_audio = cmd_name in ("song", "yta") or "audio" in query.lower()

    # Clean query if 'audio' was passed at the end
    clean_query = query
    if is_audio and clean_query.lower().endswith(" audio"):
        clean_query = clean_query[:-6].strip()

    # Determine whether input is URL or search query
    target = clean_query
    if not (target.startswith("http://") or target.startswith("https://")):
        target = f"ytsearch1:{clean_query}"

    media_type = "Audio (MP3)" if is_audio else "Video (MP4)"
    msg = await event.reply_or_edit(f"📥 **Downloading {media_type}:** `{clean_query[:50]}`...")
    out_tmpl = str(config.DOWNLOAD_DIR / f"%(id)s.%(ext)s")

    opts = {
        "outtmpl": out_tmpl,
        "quiet": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios"]
            }
        }
    }
    if is_audio:
        opts["format"] = "bestaudio/ba/b"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]/b/best"
        opts["merge_output_format"] = "mp4"

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(target, download=True))
            if "entries" in info and info["entries"]:
                info = info["entries"][0]
            filename = ydl.prepare_filename(info)

        base, _ = os.path.splitext(filename)
        candidates = [
            f"{base}.mp3" if is_audio else f"{base}.mp4",
            f"{base}.mp4",
            f"{base}.m4a",
            f"{base}.webm",
            filename
        ]
        actual_file = next((f for f in candidates if os.path.exists(f)), None)

        if not actual_file:
            await msg.edit("❌ Download finished but file was not found.")
            return

        title = info.get("title", "Audio" if is_audio else "Video")
        uploader = info.get("uploader", "YouTube")

        await msg.edit("📤 **Uploading to Telegram...**")
        if is_audio:
            await event.client.send_file(
                event.chat_id,
                file=actual_file,
                caption=f"🎵 **{title}**\n👤 `{uploader}`",
                reply_to=event.id
            )
        else:
            await event.client.send_file(
                event.chat_id,
                file=actual_file,
                caption=f"🎥 **{title}**\n👤 `{uploader}`",
                reply_to=event.id
            )

        if event.out:
            await event.delete()
        else:
            await msg.delete()

        if os.path.exists(actual_file):
            os.remove(actual_file)
    except Exception as e:
        await msg.edit(f"❌ Failed to download/send media: `{e}`")


@omni_cmd(
    pattern="stoi",
    desc="Converts replied sticker to PNG image.",
    usage=".stoi (as reply to sticker)",
    category="Media"
)
async def sticker_to_image(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sticker:
        await event.reply_or_edit("❌ Reply to a sticker to convert it to image.")
        return

    msg = await event.reply_or_edit("🔄 **Converting sticker to image...**")
    buf = io.BytesIO()
    await reply.download_media(file=buf)
    buf.seek(0)

    try:
        img = Image.open(buf)
        out_buf = io.BytesIO()
        img.save(out_buf, format="PNG")
        out_buf.seek(0)
        out_buf.name = "sticker.png"

        await event.client.send_file(
            event.chat_id,
            file=out_buf,
            caption="🖼️ **Sticker converted to PNG**",
            reply_to=reply.id
        )
        if event.out:
            await event.delete()
        else:
            await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ Conversion failed: `{e}`")


@omni_cmd(
    pattern="itos",
    desc="Converts replied image or photo to WebP sticker.",
    usage=".itos (as reply to photo)",
    category="Media"
)
async def image_to_sticker(event):
    reply = await event.get_reply_message()
    if not reply or not (reply.photo or reply.media):
        await event.reply_or_edit("❌ Reply to an image or photo to convert it to a sticker.")
        return

    msg = await event.reply_or_edit("🔄 **Converting image to sticker...**")
    buf = io.BytesIO()
    await reply.download_media(file=buf)
    buf.seek(0)

    try:
        img = Image.open(buf)
        img.thumbnail((512, 512))
        out_buf = io.BytesIO()
        img.save(out_buf, format="WEBP")
        out_buf.seek(0)
        out_buf.name = "sticker.webp"

        await event.client.send_file(
            event.chat_id,
            file=out_buf,
            reply_to=reply.id
        )
        if event.out:
            await event.delete()
        else:
            await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ Conversion failed: `{e}`")


@omni_cmd(
    pattern="download",
    desc="Downloads replied media file to bot host machine.",
    usage=".download (as reply)",
    category="Media"
)
async def download_media(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply_or_edit("❌ Reply to a message with media to download.")
        return

    msg = await event.reply_or_edit("📥 **Downloading media to host...**")
    
    last_update = [0]
    async def callback(current, total):
        import time
        now = time.time()
        if now - last_update[0] > 2:
            last_update[0] = now
            bar = progress_bar(current, total)
            try:
                await msg.edit(f"📥 **Downloading:**\n{bar}")
            except Exception:
                pass

    try:
        path = await reply.download_media(file=str(config.DOWNLOAD_DIR), progress_callback=callback)
        filename = os.path.basename(path)
        size = format_bytes(os.path.getsize(path))
        await msg.edit(f"✅ **Downloaded successfully!**\n📁 **File:** `{filename}`\n📦 **Size:** `{size}`")
    except Exception as e:
        await msg.edit(f"❌ Download failed: `{e}`")


@omni_cmd(
    pattern="upload",
    desc="Uploads a file from host machine to Telegram chat.",
    usage=".upload <filepath>",
    category="Media"
)
async def upload_file(event):
    path_str = event.text_args.strip()
    if not path_str:
        await event.reply_or_edit("📤 **Usage:** `.upload <local file path>`")
        return

    path = Path(path_str)
    if not path.exists() or not path.is_file():
        await event.reply_or_edit(f"❌ File not found at path: `{path_str}`")
        return

    msg = await event.reply_or_edit(f"📤 **Uploading `{path.name}`...**")
    total_size = path.stat().st_size

    last_update = [0]
    async def callback(current, total):
        import time
        now = time.time()
        if now - last_update[0] > 2:
            last_update[0] = now
            bar = progress_bar(current, total or total_size)
            try:
                await msg.edit(f"📤 **Uploading:**\n{bar}")
            except Exception:
                pass

    try:
        await event.client.send_file(
            event.chat_id,
            file=str(path),
            caption=f"📁 **File:** `{path.name}` ({format_bytes(total_size)})",
            progress_callback=callback,
            reply_to=event.id
        )
        if event.out:
            await event.delete()
        else:
            await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ Upload failed: `{e}`")
