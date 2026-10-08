import asyncio
import random
from core.decorators import omni_cmd
from helpers.telegram_tools import get_target_user

SLAPS = [
    "{victim} was slapped by {sender} with a giant rubber duck! 🦆",
    "{sender} threw a wet sponge at {victim}'s face! 🧽",
    "{victim} got hit with a dictionary for bad grammar! 📚",
    "{sender} slapped {victim} into another dimension! 🚀",
    "{victim} stepped on a Lego placed by {sender}! 🧱",
    "{sender} smacked {victim} with a frozen fish! 🐟",
]


@omni_cmd(
    pattern="type",
    desc="Simulates animated typewriter text effect.",
    usage=".type <text>",
    category="Fun"
)
async def typewriter_text(event):
    text = event.text_args
    if not text:
        await event.reply_or_edit("⌨️ **Usage:** `.type <message>`")
        return

    display = ""
    for char in text:
        display += char
        try:
            await event.edit(display + "▌")
            await asyncio.sleep(0.08)
        except Exception:
            pass
    await event.edit(display)


@omni_cmd(
    pattern="slap",
    desc="Playfully slaps a user with random comical objects.",
    usage=".slap [user or reply]",
    category="Fun"
)
async def slap_user(event):
    target, _ = await get_target_user(event)
    sender = await event.get_sender()

    sender_name = sender.first_name if sender else "Someone"
    victim_name = target.first_name if target else "the air"

    chosen = random.choice(SLAPS).format(sender=sender_name, victim=victim_name)
    await event.reply_or_edit(f"💥 {chosen}")


@omni_cmd(pattern="shrug", desc="Sends shrug kaomoji.", usage=".shrug", category="Fun")
async def shrug_cmd(event):
    await event.reply_or_edit(r"¯\_(ツ)_/¯")


@omni_cmd(pattern="tableflip", desc="Flips the table.", usage=".tableflip", category="Fun")
async def flip_table_cmd(event):
    await event.reply_or_edit("(╯°□°)╯︵ ┻━┻")


@omni_cmd(pattern="unflip", desc="Puts table back.", usage=".unflip", category="Fun")
async def unflip_table_cmd(event):
    await event.reply_or_edit("┬─┬ノ( º _ ºノ)")


@omni_cmd(pattern="facepalm", desc="Facepalm reaction.", usage=".facepalm", category="Fun", aliases=["faceplam"])
async def facepalm_cmd(event):
    await event.reply_or_edit("🤦‍♂️")
