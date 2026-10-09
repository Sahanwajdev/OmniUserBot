import io
import json
import urllib.parse
import aiohttp
from core.decorators import omni_cmd


@omni_cmd(
    pattern="tr",
    desc="Translates text to any language using Google Translate.",
    usage=".tr [target_lang] <text> or reply to a message",
    category="Tools"
)
async def translate_cmd(event):
    target_lang = "en"
    text_to_translate = ""
    args = event.text_args.strip()

    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        text_to_translate = reply_msg.raw_text or ""
        if args:
            target_lang = args.split()[0].lower()
    else:
        parts = args.split(maxsplit=1)
        if len(parts) == 1:
            text_to_translate = parts[0]
        elif len(parts) >= 2:
            target_lang = parts[0].lower()
            text_to_translate = parts[1]

    if not text_to_translate:
        await event.reply_or_edit("⚠️ Usage: `.tr [lang_code] <text>` or reply to a message with `.tr [lang_code]`")
        return

    status = await event.reply_or_edit("⏳ Translating...")
    try:
        encoded = urllib.parse.quote(text_to_translate)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={encoded}"
        
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    translated = "".join([item[0] for item in data[0] if item[0]])
                    src_lang = data[2] if len(data) > 2 else "auto"

                    out = (
                        f"🌐 **Translation ({src_lang.upper()} ➔ {target_lang.upper()})**\n\n"
                        f"{translated}"
                    )
                    await status.edit(out)
                else:
                    await status.edit("❌ Failed to reach translation service.")
    except Exception as e:
        await status.edit(f"❌ Translation error: `{e}`")


@omni_cmd(
    pattern="tts",
    desc="Converts text to speech voice message.",
    usage=".tts [lang_code] <text> or reply to a message",
    category="Tools"
)
async def tts_cmd(event):
    lang = "en"
    text = ""
    args = event.text_args.strip()

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        text = reply.raw_text or ""
        if args:
            lang = args.split()[0].lower()
    else:
        parts = args.split(maxsplit=1)
        if len(parts) == 1:
            text = parts[0]
        elif len(parts) >= 2:
            lang = parts[0].lower()
            text = parts[1]

    if not text:
        await event.reply_or_edit("⚠️ Usage: `.tts [lang_code] <text>` or reply to a message with `.tts [lang]`")
        return

    status = await event.reply_or_edit("⏳ Generating voice audio...")
    try:
        encoded = urllib.parse.quote(text[:500])
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl={lang}&client=tw-ob"

        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    audio_bytes = await resp.read()
                    bio = io.BytesIO(audio_bytes)
                    bio.name = "voice.mp3"

                    await event.client.send_file(
                        event.chat_id,
                        bio,
                        voice_note=True,
                        reply_to=event.reply_to_msg_id or event.id
                    )
                    await status.delete()
                else:
                    await status.edit("❌ Failed to generate speech audio.")
    except Exception as e:
        await status.edit(f"❌ TTS Error: `{e}`")
