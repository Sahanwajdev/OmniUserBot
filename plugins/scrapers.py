import urllib.parse
import urllib.request
import asyncio
from bs4 import BeautifulSoup
from core.decorators import omni_cmd
from helpers.http_client import fetch_json, fetch_text, http_client

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False


@omni_cmd(
    pattern="lyrics",
    desc="Searches and extracts song lyrics.",
    usage=".lyrics <song name and artist>",
    category="Web Search",
    aliases=["songlyrics"]
)
async def get_lyrics(event):
    query = event.text_args.strip()
    if not query:
        await event.reply_or_edit("🎵 **Usage:** `.lyrics <song name and artist>`")
        return

    msg = await event.reply_or_edit(f"🎵 **Searching lyrics for:** `{query}`...")

    results = []
    if HAS_DDGS:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, lambda: list(DDGS().text(f"{query} lyrics site:genius.com", max_results=2))
            )
        except Exception:
            pass

    genius_url = None
    if results and "genius.com" in results[0].get("href", ""):
        genius_url = results[0]["href"]

    lyrics = ""
    title = query

    if genius_url:
        try:
            html = await fetch_text(genius_url)
            if html:
                soup = BeautifulSoup(html, "html.parser")
                containers = soup.find_all("div", {"data-lyrics-container": "true"})
                if containers:
                    lyrics = "\n".join([c.get_text("\n") for c in containers]).strip()
                    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else query
        except Exception:
            pass

    if not lyrics and results:
        lyrics = results[0].get("body", "")

    if not lyrics:
        await msg.edit(f"❌ Lyrics not found for `{query}`.")
        return

    if len(lyrics) > 3500:
        lyrics = lyrics[:3400] + "\n\n... *(Lyrics truncated)*"

    out = f"🎶 **Lyrics: {title}**\n\n{lyrics}"
    await msg.edit(out)


@omni_cmd(
    pattern="news",
    desc="Fetches latest top headlines and breaking tech/world stories.",
    usage=".news",
    category="Web Search",
    aliases=["headlines"]
)
async def get_news(event):
    msg = await event.reply_or_edit("📰 **Fetching latest top headlines...**")
    
    # Use Hacker News official public Firebase API
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    top_ids = await fetch_json(url)

    if not top_ids:
        await msg.edit("❌ Failed to fetch news stories.")
        return

    stories = []
    for sid in top_ids[:5]:
        item = await fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if item:
            title = item.get("title", "Headline")
            link = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
            score = item.get("score", 0)
            stories.append(f"• [{title}]({link}) (⭐ `{score}`) ")

    out = "📰 **Top Tech & Global Headlines:**\n\n" + "\n\n".join(stories)
    await msg.edit(out, link_preview=False)


@omni_cmd(
    pattern="dns",
    desc="Resolves DNS records (A, AAAA, MX, TXT) via Google DNS over HTTPS.",
    usage=".dns <domain> [record_type]",
    category="Tools"
)
async def dns_lookup(event):
    args = event.text_args.strip().split()
    if not args:
        await event.reply_or_edit("🌐 **Usage:** `.dns <domain> [A/AAAA/MX/TXT]`")
        return

    domain = args[0]
    rtype = args[1].upper() if len(args) > 1 else "A"

    msg = await event.reply_or_edit(f"🌐 **Querying `{rtype}` records for:** `{domain}`...")
    url = f"https://dns.google/resolve?name={urllib.parse.quote(domain)}&type={rtype}"
    data = await fetch_json(url)

    if not data or not data.get("Answer"):
        await msg.edit(f"❌ No `{rtype}` records found for `{domain}`.")
        return

    records = [f"• `{a.get('data')}`" for a in data["Answer"]]
    out = (
        f"🌐 **DNS Query: `{domain}` [{rtype}]**\n\n"
        + "\n".join(records)
    )
    await msg.edit(out)


@omni_cmd(
    pattern="shorten",
    desc="Shortens long URLs via TinyURL.",
    usage=".shorten <url>",
    category="Tools"
)
async def shorten_url(event):
    url = event.text_args.strip()
    if not url:
        await event.reply_or_edit("🔗 **Usage:** `.shorten <url>`")
        return

    msg = await event.reply_or_edit("🔗 **Shortening URL...**")
    api_url = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}"
    res = await fetch_text(api_url)

    if res and res.startswith("http"):
        await msg.edit(f"🔗 **Shortened URL:**\n`{res.strip()}`")
    else:
        await msg.edit("❌ Failed to shorten URL.")


@omni_cmd(
    pattern="unshorten",
    desc="Expands a shortened URL to reveal destination.",
    usage=".unshorten <short_url>",
    category="Tools"
)
async def unshorten_url(event):
    url = event.text_args.strip()
    if not url:
        await event.reply_or_edit("🔗 **Usage:** `.unshorten <short_url>`")
        return

    msg = await event.reply_or_edit("🔍 **Tracing URL destination...**")
    session = await http_client.get_session()
    try:
        async with session.head(url, allow_redirects=True) as resp:
            dest = str(resp.url)
            await msg.edit(f"🎯 **Expanded URL:**\n`{dest}`")
    except Exception as e:
        await msg.edit(f"❌ Failed to expand URL: `{e}`")


@omni_cmd(
    pattern="fake",
    desc="Generates random fake identity profile data for testing.",
    usage=".fake",
    category="Tools",
    aliases=["fakeuser"]
)
async def generate_fake_user(event):
    msg = await event.reply_or_edit("👤 **Generating identity...**")
    data = await fetch_json("https://randomuser.me/api/")

    if not data or not data.get("results"):
        await msg.edit("❌ Failed to generate identity.")
        return

    u = data["results"][0]
    name = f"{u['name']['first']} {u['name']['last']}"
    email = u["email"]
    country = u["location"]["country"]
    city = u["location"]["city"]
    phone = u["phone"]
    age = u["dob"]["age"]
    gender = u["gender"].capitalize()

    out = (
        f"👤 **Random Identity Generator:**\n\n"
        f"• **Name:** `{name}`\n"
        f"• **Gender:** `{gender}` | **Age:** `{age}`\n"
        f"• **Location:** `{city}, {country}`\n"
        f"• **Email:** `{email}`\n"
        f"• **Phone:** `{phone}`"
    )
    await msg.edit(out)
