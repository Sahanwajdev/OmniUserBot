import random
import asyncio
from core.decorators import omni_cmd


@omni_cmd(
    pattern="coin",
    desc="Flips a coin with realistic Heads or Tails result.",
    usage=".coin",
    category="Fun",
    aliases=["toss"]
)
async def coin_cmd(event):
    status = await event.reply_or_edit("🪙 Flipping coin...")
    await asyncio.sleep(1)
    outcome = random.choice(["Heads", "Tails"])
    await status.edit(f"🪙 **Coin Landed On:** **{outcome}**!")


@omni_cmd(
    pattern="mock",
    desc="Converts text to MoCkInG sPoNgEbOb text.",
    usage=".mock <text> or reply to message",
    category="Fun"
)
async def mock_cmd(event):
    text = event.text_args.strip()
    if not text and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        text = reply.raw_text or ""

    if not text:
        await event.reply_or_edit("⚠️ Usage: `.mock <text>`")
        return

    mocked = "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
    await event.reply_or_edit(mocked)


@omni_cmd(
    pattern="vapor",
    desc="Converts text into aesthetic ｖａｐｏｒｗａｖｅ full-width text.",
    usage=".vapor <text> or reply to message",
    category="Fun"
)
async def vapor_cmd(event):
    text = event.text_args.strip()
    if not text and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        text = reply.raw_text or ""

    if not text:
        await event.reply_or_edit("⚠️ Usage: `.vapor <text>`")
        return

    result = "".join(chr(ord(c) + 0xFEE0) if 0x21 <= ord(c) <= 0x7E else c for c in text)
    await event.reply_or_edit(result)


@omni_cmd(
    pattern="zal",
    desc="Transforms text into chaotic Zalgo corrupted text.",
    usage=".zal <text> or reply to message",
    category="Fun"
)
async def zalgo_cmd(event):
    text = event.text_args.strip()
    if not text and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        text = reply.raw_text or ""

    if not text:
        await event.reply_or_edit("⚠️ Usage: `.zal <text>`")
        return

    zalgo_marks = [chr(i) for i in range(0x0300, 0x036F)]
    out = "".join(c + "".join(random.sample(zalgo_marks, min(3, len(zalgo_marks)))) for c in text)
    await event.reply_or_edit(out[:2000])
