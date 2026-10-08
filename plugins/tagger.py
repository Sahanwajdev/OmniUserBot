import asyncio
import random
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.errors import FloodWaitError
from core.decorators import omni_cmd
from config import config

# Active tagging sessions by chat_id
ACTIVE_TAGGERS = set()

# Curated quotes databases
SHAYARIS = [
    "✨ *Kuch to baat hai teri fitrat mein zalim, warna hum kisi ko itni shiddat se yaad nahi karte.*",
    "🌹 *Khushbu ban kar teri saanso mein sama jayenge, sukoon ban kar tere dil mein utar jayenge.*",
    "💫 *Waqt mile to kabhi humari dosti ka hisaab kar lena, har lamhe mein sirf tera hi zikr milega.*",
    "🌙 *Chandni raat mein taare ginte ginte so gaye hum, teri yaadon ki mehfil sajate sajate kho gaye hum.*",
    "🍂 *Dil se chaho to har manzil aasan ho jati hai, sachhi dosti se har mushkil meharban ho jati hai.*",
    "🔥 *Hum apni dosti par kabhi gumaan nahi karte, doston ko kabhi waqt ke hawale nahi karte.*",
    "🌸 *Muskurahat ka koi mol nahi hota, kuch rishton ka koi tol nahi hota.*",
    "💎 *Heere ki pehchan johri ko hoti hai, sachhe doston ki qadar dilon ko hoti hai.*",
    "🌺 *Tere aane se mehki hai zindagi meri, teri dosti hi to hai bandagi meri.*",
    "🕊️ *Khwaabon ki duniya mein hum kho nahi sakte, sachhe doston ko hum bhool nahi sakte.*",
    "🌟 *Roshni ban kar ujaala kar denge, dosti ki raahon ko gulzar kar denge.*",
    "🥀 *Phool to murjha jate hain par dosti hamesha taaza rehti hai.*",
]

GOOD_MORNING_WISHES = [
    "🌅 **Good Morning!** May your day be filled with endless smiles and positive energy! ☀️",
    "☕ **Rise & Shine!** A fresh day, fresh opportunities, and fresh coffee await you! 🌸",
    "🌻 **Subah Bakhair / Good Morning!** Utho aur naye sapno ko sach karne ki shuruat karo! 🚀",
    "🌞 **Wake up!** The sun is out, the birds are singing, have an amazing day ahead! 🌈",
    "💐 **Sweet Morning!** May peace and success accompany every step you take today! ✨",
    "🌤️ **Good Morning Champions!** Keep smiling and keep conquering your goals! 🏆",
    "☀️ **Nayi Subah, Nayi Umang!** May today bring happiness and blessings to you! 🌼",
    "🥞 **Morning vibes!** Take a deep breath, drink your tea, and enjoy the day! ☕",
]

GOOD_NIGHT_WISHES = [
    "🌙 **Good Night!** Close your eyes, let go of worries, and dream peacefully! 💤",
    "⭐ **Shubh Ratri / Good Night!** May the stars guide your dreams to sweet serenity! 🌌",
    "🛌 **Time to rest!** Sleep tight, recharge your mind, and wake up refreshed! 😴",
    "🌟 **Sweet Dreams!** Tomorrow is a blank page waiting for your bright story! 🌠",
    "🕊️ **Good Night everyone!** Leave today's stress behind, peace awaits you in sleep! 🌙",
    "💤 **Chalo so jao sab!** Rest well, good night and sweetest dreams! 🧸",
    "🌌 **Silent night, sweet rest.** May tomorrow bring even brighter joy! ✨",
]

LOVE_QUOTES = [
    "❤️ *In a world full of temporary things, you are my favorite forever.*",
    "💖 *Dil ki har dhadkan mein tera hi naam hai, meri subah aur meri shaam hai.*",
    "🌹 *You are the poetry I never knew how to write.*",
    "💞 *Mohabbat unse nahi hoti jo khoobsurat ho, khoobsurat wo lagte hain jinse mohabbat ho.*",
    "💍 *Every love story is beautiful, but ours is my absolute favorite.*",
    "💌 *Teri ek muskurahat mere saare dukh mita deti hai.*",
]

DOSTI_QUOTES = [
    "🤝 *Dosti wo nahi jo jaan deti hai, dosti wo hai jo jeena sikhati hai!*",
    "🔥 *A true friend is someone who knows all about you and still loves you.*",
    "🍻 *Kaminey dost na ho to zindagi bilkul boring ho jati hai!*",
    "💎 *Dosti ek anmol heera hai, ise sambhal kar rakhna chahiye.*",
    "🎉 *Dosti ka rishta sabse khaas hai, har dukh mein dost hi paas hai.*",
]

FUNNY_QUOTES = [
    "👀 *Kaun kaun zinda hai is group mein? Attendance lagao jaldi!*",
    "📢 *Hello mute janta! Phone rakh kar thoda yahan bhi bol lo!*",
    "🍕 *Doston ki dosti par shaq mat karo, bas unse pizza ki party maango!*",
    "👻 *Bhoot ban kar ghoomne walo, thoda reply bhi kar diya karo!*",
    "💤 *Kumbhakaran ki auladon, group mein bhi thodi roshni dalo!*",
    "🍿 *Popcorn le aao sab, yahan sab log silent movie dekh rahe hain!*",
]


async def _run_tagger(event, user_pool_text: str, custom_quote_func=None):
    client = event.client
    chat = event.chat_id

    if not (event.is_group or event.is_channel):
        await event.reply("❌ This command can only be used in groups.")
        return

    if chat in ACTIVE_TAGGERS:
        await event.reply_or_edit("⚠️ A tagging session is already running in this chat. Use `.tagstop` to cancel it first.")
        return

    ACTIVE_TAGGERS.add(chat)
    msg = await event.reply_or_edit("🔍 **Gathering group members for tagging...**")

    # Collect active human members
    users = []
    async for u in client.iter_participants(chat):
        if not u.bot and not u.deleted:
            users.append(u)

    if not users:
        ACTIVE_TAGGERS.discard(chat)
        await msg.edit("❌ No eligible members found to tag.")
        return

    total = len(users)
    await msg.edit(f"🚀 **Starting tagger for {total} members...**\n_Use `.tagstop` anytime to stop._")

    # Process in batches of 5 users per message
    batch_size = 5
    tagged_count = 0

    for i in range(0, total, batch_size):
        if chat not in ACTIVE_TAGGERS:
            break

        batch = users[i:i + batch_size]
        mentions = []
        for u in batch:
            name = (u.first_name or "User").replace("[", "").replace("]", "")
            mentions.append(f"[{name}](tg://user?id={u.id})")

        # Pick quote or custom text
        header = custom_quote_func() if custom_quote_func else user_pool_text
        text = f"{header}\n\n👥 " + " • ".join(mentions)

        try:
            await client.send_message(chat, text)
            tagged_count += len(batch)
            await asyncio.sleep(2.0)  # Safe delay between mentions
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 1)
        except Exception:
            pass

    ACTIVE_TAGGERS.discard(chat)
    await client.send_message(
        chat,
        f"✅ **Tagging Finished!** Successfully mentioned `{tagged_count}/{total}` members."
    )


@omni_cmd(
    pattern="tagall",
    desc="Tags all group members with a custom message or alert.",
    usage=".tagall [message]",
    category="Tagger",
    aliases=["all", "mentionall"],
    only_groups=True
)
async def tag_all_members(event):
    custom_msg = event.text_args.strip() or "👋 **Attention Everyone! Check this out!**"
    await _run_tagger(event, custom_msg)


@omni_cmd(
    pattern="tagshari",
    desc="Tags group members with beautiful poetic Hindi/Urdu Shayaris.",
    usage=".tagshari",
    category="Tagger",
    aliases=["shayaritag", "tagshayari", "shari"],
    only_groups=True
)
async def tag_shayari(event):
    await _run_tagger(event, "", custom_quote_func=lambda: random.choice(SHAYARIS))


@omni_cmd(
    pattern="taggm",
    desc="Tags group members with fresh, uplifting Good Morning wishes.",
    usage=".taggm",
    category="Tagger",
    aliases=["tagmorning", "gmtag", "morningtag"],
    only_groups=True
)
async def tag_good_morning(event):
    await _run_tagger(event, "", custom_quote_func=lambda: random.choice(GOOD_MORNING_WISHES))


@omni_cmd(
    pattern="taggn",
    desc="Tags group members with peaceful Good Night wishes.",
    usage=".taggn",
    category="Tagger",
    aliases=["tagnight", "gntag", "nighttag"],
    only_groups=True
)
async def tag_good_night(event):
    await _run_tagger(event, "", custom_quote_func=lambda: random.choice(GOOD_NIGHT_WISHES))


@omni_cmd(
    pattern="taglove",
    desc="Tags group members with sweet romantic & love quotes.",
    usage=".taglove",
    category="Tagger",
    aliases=["lovetag", "tagpyaar"],
    only_groups=True
)
async def tag_love(event):
    await _run_tagger(event, "", custom_quote_func=lambda: random.choice(LOVE_QUOTES))


@omni_cmd(
    pattern="tagdosti",
    desc="Tags group members with friendship & Dosti quotes.",
    usage=".tagdosti",
    category="Tagger",
    aliases=["dostitag", "tagfriend"],
    only_groups=True
)
async def tag_dosti(event):
    await _run_tagger(event, "", custom_quote_func=lambda: random.choice(DOSTI_QUOTES))


@omni_cmd(
    pattern="tagfunny",
    desc="Tags group members with funny banter and humorous roast lines.",
    usage=".tagfunny",
    category="Tagger",
    aliases=["funnytag", "tagroast"],
    only_groups=True
)
async def tag_funny(event):
    await _run_tagger(event, "", custom_quote_func=lambda: random.choice(FUNNY_QUOTES))


@omni_cmd(
    pattern="tagadmin",
    desc="Tags all administrators in the group for urgent attention.",
    usage=".tagadmin [message]",
    category="Tagger",
    aliases=["tagadmins"],
    only_groups=True
)
async def tag_admins(event):
    client = event.client
    chat = event.chat_id
    custom_msg = event.text_args.strip() or "🚨 **Attention Admins! Immediate action needed!**"

    msg = await event.reply_or_edit("👮 **Fetching group administrators...**")
    admins = await client.get_participants(chat, filter=ChannelParticipantsAdmins)

    mentions = []
    for a in admins:
        if not a.bot and not a.deleted:
            name = (a.first_name or "Admin").replace("[", "").replace("]", "")
            mentions.append(f"[{name}](tg://user?id={a.id})")

    if not mentions:
        await msg.edit("❌ No human admins found.")
        return

    text = f"{custom_msg}\n\n🛡️ **Admins:**\n" + " • ".join(mentions)
    await msg.edit(text)


@omni_cmd(
    pattern="tagstop",
    desc="Instantly stops any currently running tagging process in this chat.",
    usage=".tagstop",
    category="Tagger",
    aliases=["tagcancel", "stoptag"],
    only_groups=True
)
async def tag_stop(event):
    chat = event.chat_id
    if chat in ACTIVE_TAGGERS:
        ACTIVE_TAGGERS.discard(chat)
        await event.reply_or_edit("🛑 **Tagging session stopped!**")
    else:
        await event.reply_or_edit("ℹ️ No active tagging session is running in this chat.")
