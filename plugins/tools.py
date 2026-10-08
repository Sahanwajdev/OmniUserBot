import os
import math
import io
import asyncio
from telethon import events
from telethon.tl.types import User
import qrcode
from gtts import gTTS

from core.decorators import omni_cmd
from helpers.telegram_tools import get_target_user
from config import config

try:
    from deep_translator import MyMemoryTranslator, GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False


@omni_cmd(
    pattern="tr",
    desc="Translates text or replied message into specified language code.",
    usage=".tr <lang_code> [text or reply]",
    category="Tools",
    aliases=["translate"]
)
async def translate_text(event):
    args = event.text_args.strip()
    reply = await event.get_reply_message()

    target_lang = "en"
    text_to_tr = ""

    if args:
        parts = args.split(maxsplit=1)
        if len(parts[0]) in (2, 5) and parts[0].isalpha():
            target_lang = parts[0]
            text_to_tr = parts[1] if len(parts) > 1 else ""
        else:
            text_to_tr = args

    if not text_to_tr and reply:
        text_to_tr = reply.text or ""

    if not text_to_tr:
        await event.reply_or_edit("🌐 **Usage:** `.tr <lang_code> [text]` or `.tr <lang_code>` as reply.")
        return

    msg = await event.reply_or_edit(f"🌐 **Translating into `{target_lang}`...**")
    translated = None

    if HAS_TRANSLATOR:
        # Multi-engine fallback: Try MyMemory first, fallback to GoogleTranslator
        try:
            translated = MyMemoryTranslator(source="auto", target=target_lang).translate(text_to_tr)
        except Exception:
            try:
                translated = GoogleTranslator(source="auto", target=target_lang).translate(text_to_tr)
            except Exception as e:
                translated = None

    if not translated:
        await msg.edit("❌ Failed to translate text. Check language code (e.g. `en`, `es`, `fr`, `de`, `hi`, `ar`).")
        return

    out = (
        f"🌐 **Translated to `{target_lang}`:**\n\n"
        f"**Original:**\n_{text_to_tr}_\n\n"
        f"**Translation:**\n{translated}"
    )
    await msg.edit(out)


@omni_cmd(
    pattern="tts",
    desc="Converts text to speech audio note using Google TTS.",
    usage=".tts [lang_code] <text>",
    category="Tools",
    aliases=["voice"]
)
async def text_to_speech(event):
    args = event.text_args.strip()
    reply = await event.get_reply_message()

    lang = "en"
    text = ""

    if args:
        parts = args.split(maxsplit=1)
        if len(parts[0]) == 2 and parts[0].isalpha():
            lang = parts[0]
            text = parts[1] if len(parts) > 1 else ""
        else:
            text = args

    if not text and reply:
        text = reply.text or ""

    if not text:
        await event.reply_or_edit("🗣️ **Usage:** `.tts <text>` or `.tts <lang> <text>`")
        return

    msg = await event.reply_or_edit("🗣️ **Generating voice note...**")

    out_file = config.DOWNLOAD_DIR / f"tts_{event.id}.mp3"
    try:
        loop = asyncio.get_event_loop()
        tts = await loop.run_in_executor(None, lambda: gTTS(text=text, lang=lang))
        await loop.run_in_executor(None, lambda: tts.save(str(out_file)))

        await event.client.send_file(
            event.chat_id,
            file=str(out_file),
            voice_note=True,
            reply_to=reply.id if reply else event.id,
            caption=f"🗣️ **TTS [{lang}]:** _{text[:100]}..._" if len(text) > 100 else f"🗣️ **TTS [{lang}]:** _{text}_"
        )
        if event.out:
            await event.delete()
        else:
            await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ Failed to generate TTS: `{e}`")
    finally:
        if out_file.exists():
            try:
                os.remove(out_file)
            except Exception:
                pass


@omni_cmd(
    pattern="qr",
    desc="Generates a QR code image from text or URL.",
    usage=".qr <text or link>",
    category="Tools"
)
async def generate_qr(event):
    text = event.text_args.strip()
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text

    if not text:
        await event.reply_or_edit("📱 **Usage:** `.qr <text or URL>`")
        return

    msg = await event.reply_or_edit("📱 **Generating QR Code...**")

    buf = io.BytesIO()
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(buf, format="PNG")
    buf.seek(0)
    buf.name = "qrcode.png"

    await event.client.send_file(
        event.chat_id,
        file=buf,
        caption=f"📱 **QR Code for:**\n`{text[:150]}`",
        reply_to=event.id
    )
    if event.out:
        await event.delete()
    else:
        await msg.delete()


@omni_cmd(
    pattern="calc",
    desc="Evaluates a mathematical expression safely.",
    usage=".calc <expression>",
    category="Tools",
    aliases=["math"]
)
async def calculate_math(event):
    expr = event.text_args.strip()
    if not expr:
        await event.reply_or_edit("🧮 **Usage:** `.calc <expression>`\nExample: `.calc (25 * 4) + sqrt(144)`")
        return

    # Whitelist math scope
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "tan": math.tan, "log": math.log, "log10": math.log10,
        "exp": math.exp, "pi": math.pi, "e": math.e, "pow": pow,
    }

    try:
        # Compile and evaluate without builtins
        code = compile(expr, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"Function or variable '{name}' is not permitted.")
        result = eval(code, {"__builtins__": {}}, allowed_names)

        await event.reply_or_edit(
            f"🧮 **Calculation:**\n"
            f"**Expression:** `{expr}`\n"
            f"**Result:** `{result}`"
        )
    except Exception as e:
        await event.reply_or_edit(f"❌ **Math Error:** `{e}`")


@omni_cmd(
    pattern="id",
    desc="Displays ID of user, chat, channel, and replied message.",
    usage=".id (or as reply)",
    category="Tools"
)
async def get_ids(event):
    reply = await event.get_reply_message()
    chat = await event.get_chat()
    
    out = [
        "🆔 **Telegram IDs:**",
        f"• **Chat ID:** `{event.chat_id}`",
        f"• **Message ID:** `{event.id}`",
    ]

    if reply:
        sender = await reply.get_sender()
        out.append(f"• **Replied Message ID:** `{reply.id}`")
        if sender:
            name = getattr(sender, "first_name", "Unknown")
            out.append(f"• **Replied User:** [{name}](tg://user?id={sender.id}) (`{sender.id}`)")

    await event.reply_or_edit("\n".join(out))


@omni_cmd(
    pattern="info",
    desc="Fetches complete public Telegram profile info for a user.",
    usage=".info [user or reply]",
    category="Tools",
    aliases=["whois_user", "userinfo"]
)
async def user_info(event):
    target, _ = await get_target_user(event)
    if not target:
        target = await event.get_sender()

    if not target:
        await event.reply_or_edit("❌ Target user not found.")
        return

    full = await event.client.get_entity(target.id)
    first_name = full.first_name or "N/A"
    last_name = full.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    username = f"@{full.username}" if full.username else "None"
    dc_id = getattr(full.photo, "dc_id", "N/A") if hasattr(full, "photo") and full.photo else "N/A"
    is_bot = "Yes" if getattr(full, "bot", False) else "No"
    is_verified = "Yes" if getattr(full, "verified", False) else "No"
    is_scam = "Yes" if getattr(full, "scam", False) else "No"
    is_premium = "Yes" if getattr(full, "premium", False) else "No"

    out = (
        f"👤 **User Information:**\n\n"
        f"• **Name:** [{full_name}](tg://user?id={full.id})\n"
        f"• **User ID:** `{full.id}`\n"
        f"• **Username:** {username}\n"
        f"• **Data Center (DC):** `{dc_id}`\n"
        f"• **Premium:** `{is_premium}`\n"
        f"• **Bot:** `{is_bot}`\n"
        f"• **Verified:** `{is_verified}`\n"
        f"• **Scam Flag:** `{is_scam}`\n"
        f"• **Permanent Link:** [Profile Link](tg://user?id={full.id})"
    )
    await event.reply_or_edit(out)
