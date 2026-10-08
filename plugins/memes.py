import random
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from core.decorators import omni_cmd


@omni_cmd(
    pattern="mock",
    desc="Converts text to SpOnGeBoB mOcKiNg format.",
    usage=".mock <text or reply>",
    category="Fun",
    aliases=["sponge"]
)
async def mock_text(event):
    text = event.text_args
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text

    if not text:
        await event.reply_or_edit("🤪 **Usage:** `.mock <text>` or reply to a message.")
        return

    mocked = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
    await event.reply_or_edit(mocked)


@omni_cmd(
    pattern="reverse",
    desc="Reverses the given text.",
    usage=".reverse <text>",
    category="Fun"
)
async def reverse_text(event):
    text = event.text_args
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text

    if not text:
        await event.reply_or_edit("🙃 **Usage:** `.reverse <text>`")
        return

    await event.reply_or_edit(text[::-1])


@omni_cmd(
    pattern="vapor",
    desc="Converts text to full-width vaporwave aesthetic font.",
    usage=".vapor <text>",
    category="Fun",
    aliases=["aesthetic"]
)
async def vaporwave_text(event):
    text = event.text_args
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text

    if not text:
        await event.reply_or_edit("🌸 **Usage:** `.vapor <text>`")
        return

    result = []
    for char in text:
        code = ord(char)
        if 0x21 <= code <= 0x7E:
            result.append(chr(code + 0xFEE0))
        elif code == 0x20:
            result.append("\u3000")
        else:
            result.append(char)

    await event.reply_or_edit("".join(result))


@omni_cmd(
    pattern="scramble",
    desc="Randomly scrambles letters inside words while keeping readability.",
    usage=".scramble <text>",
    category="Fun"
)
async def scramble_text(event):
    text = event.text_args
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text

    if not text:
        await event.reply_or_edit("🎲 **Usage:** `.scramble <text>`")
        return

    words = text.split()
    scrambled_words = []
    for word in words:
        if len(word) > 3:
            middle = list(word[1:-1])
            random.shuffle(middle)
            scrambled_words.append(word[0] + "".join(middle) + word[-1])
        else:
            scrambled_words.append(word)

    await event.reply_or_edit(" ".join(scrambled_words))


@omni_cmd(
    pattern="react",
    desc="Reacts to replied message with specified emoji.",
    usage=".react <emoji> (as reply)",
    category="Fun"
)
async def react_message(event):
    emoji = event.text_args.strip() or "🔥"
    reply = await event.get_reply_message()
    if not reply:
        await event.reply_or_edit("❌ Reply to a message to react.")
        return

    try:
        await event.client(SendReactionRequest(
            peer=event.chat_id,
            msg_id=reply.id,
            reaction=[ReactionEmoji(emoticon=emoji)]
        ))
        if event.out:
            await event.delete()
    except Exception as e:
        await event.reply_or_edit(f"❌ Failed to react: `{e}`")
