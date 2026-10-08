import asyncio
import urllib.parse
from telethon import events
from core.decorators import omni_cmd
from helpers.http_client import fetch_json, fetch_text, http_client
from helpers.formatting import clean_html_to_markdown

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        HAS_DDGS = True
    except ImportError:
        HAS_DDGS = False


@omni_cmd(
    pattern="ddg",
    desc="Searches DuckDuckGo for top web results with snippets.",
    usage=".ddg <search query>",
    category="Web Search",
    aliases=["search", "duck"]
)
async def ddg_search(event):
    query = event.text_args
    if not query:
        await event.reply_or_edit("🔍 **Usage:** `.ddg <search query>`")
        return

    msg = await event.reply_or_edit(f"🔎 **Searching DuckDuckGo for:** `{query}`...")

    results = []
    if HAS_DDGS:
        try:
            # Run ddgs in a thread pool to avoid blocking async loop
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, lambda: list(DDGS().text(query, max_results=5))
            )
        except Exception:
            pass

    # Fallback to DuckDuckGo instant API if library returned empty
    if not results:
        api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
        data = await fetch_json(api_url)
        if data and data.get("AbstractText"):
            results.append({
                "title": data.get("Heading", "Instant Answer"),
                "href": data.get("AbstractURL", ""),
                "body": data.get("AbstractText", ""),
            })
            for topic in data.get("RelatedTopics", [])[:3]:
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "title": topic["Text"][:50] + "...",
                        "href": topic["FirstURL"],
                        "body": topic["Text"],
                    })

    if not results:
        await msg.edit(f"❌ No web results found for: `{query}`")
        return

    out = [f"🌐 **DuckDuckGo Web Results for:** `{query}`\n"]
    for i, r in enumerate(results[:5], 1):
        title = r.get("title", "No Title").strip()
        link = r.get("href", "")
        body = r.get("body", "No description available.").strip()
        out.append(f"**{i}. [{title}]({link})**\n_{body}_\n")

    await msg.edit("\n".join(out), link_preview=False)


@omni_cmd(
    pattern="google",
    desc="Fast web search aggregator.",
    usage=".google <query>",
    category="Web Search",
    aliases=["g"]
)
async def google_search(event):
    query = event.text_args
    if not query:
        await event.reply_or_edit("🔍 **Usage:** `.google <query>`")
        return

    msg = await event.reply_or_edit(f"🔎 **Searching the Web for:** `{query}`...")

    results = []
    if HAS_DDGS:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, lambda: list(DDGS().text(query, max_results=5))
            )
        except Exception:
            pass

    if not results:
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        await msg.edit(f"🌐 **Search Direct:** [Google Search for '{query}']({google_url})")
        return

    out = [f"🔍 **Search Results for:** `{query}`\n"]
    for i, r in enumerate(results[:5], 1):
        title = r.get("title", "No Title").strip()
        link = r.get("href", "")
        body = r.get("body", "").strip()
        out.append(f"**{i}. [{title}]({link})**\n_{body}_\n")

    await msg.edit("\n".join(out), link_preview=False)


@omni_cmd(
    pattern="wiki",
    desc="Searches Wikipedia and returns direct encyclopedic summary.",
    usage=".wiki <topic>",
    category="Web Search",
    aliases=["wikipedia"]
)
async def wiki_search(event):
    query = event.text_args
    if not query:
        await event.reply_or_edit("📖 **Usage:** `.wiki <topic>`")
        return

    msg = await event.reply_or_edit(f"📖 **Querying Wikipedia for:** `{query}`...")
    encoded = urllib.parse.quote(query.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    wiki_headers = {"User-Agent": "OmniUserBot/1.0 (https://github.com/Sahanwajdev/OmniUserBot; contact: userbot@telegram.org)"}

    data = await fetch_json(url, headers=wiki_headers)
    if not data or data.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
        # Search API fallback
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=1&namespace=0&format=json"
        s_data = await fetch_json(search_url, headers=wiki_headers)
        if s_data and len(s_data) >= 4 and s_data[1]:
            first_title = s_data[1][0]
            enc2 = urllib.parse.quote(first_title.replace(" ", "_"))
            data = await fetch_json(f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc2}", headers=wiki_headers)

    if not data or not data.get("extract"):
        await msg.edit(f"❌ No Wikipedia article found for: `{query}`")
        return

    title = data.get("title", query)
    extract = data.get("extract", "")
    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{encoded}")

    out = (
        f"📚 **Wikipedia: [{title}]({page_url})**\n\n"
        f"{extract}\n\n"
        f"🔗 [Read full article]({page_url})"
    )
    await msg.edit(out, link_preview=False)


@omni_cmd(
    pattern="gh",
    desc="Inspects a GitHub repository (stars, forks, open issues, language, description).",
    usage=".gh <owner/repo>",
    category="Web Search",
    aliases=["github", "repo"]
)
async def github_repo(event):
    repo_arg = event.text_args.strip()
    if not repo_arg:
        await event.reply_or_edit("🐙 **Usage:** `.gh <owner/repo>`\nExample: `.gh LonamiWebs/Telethon`")
        return

    # Clean URL if full GitHub link pasted
    if "github.com/" in repo_arg:
        repo_arg = repo_arg.split("github.com/")[-1].strip("/")

    msg = await event.reply_or_edit(f"🐙 **Fetching GitHub repo:** `{repo_arg}`...")
    url = f"https://api.github.com/repos/{repo_arg}"
    headers = {"User-Agent": "OmniUserBot-Telegram"}

    data = await fetch_json(url, headers=headers)
    if not data or "message" in data and data["message"] == "Not Found":
        await msg.edit(f"❌ GitHub repository `{repo_arg}` not found.")
        return

    name = data.get("full_name", repo_arg)
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    issues = data.get("open_issues_count", 0)
    lang = data.get("language", "Unknown")
    license_name = data.get("license", {}).get("name", "None") if data.get("license") else "None"
    html_url = data.get("html_url", f"https://github.com/{repo_arg}")
    desc = data.get("description", "No description provided.") or "No description provided."
    updated = data.get("updated_at", "")[:10]

    out = (
        f"🐙 **GitHub Repository: [{name}]({html_url})**\n\n"
        f"📝 **Description:** {desc}\n\n"
        f"⭐ **Stars:** `{stars:,}` | 🍴 **Forks:** `{forks:,}`\n"
        f"🐛 **Open Issues:** `{issues:,}` | 💻 **Language:** `{lang}`\n"
        f"📜 **License:** `{license_name}` | 🕒 **Updated:** `{updated}`\n"
        f"🔗 [Visit Repository]({html_url})"
    )
    await msg.edit(out, link_preview=False)


@omni_cmd(
    pattern="ghuser",
    desc="Fetches public profile of a GitHub user.",
    usage=".ghuser <username>",
    category="Web Search"
)
async def github_user(event):
    username = event.text_args.strip().lstrip("@")
    if not username:
        await event.reply_or_edit("🐙 **Usage:** `.ghuser <username>`")
        return

    msg = await event.reply_or_edit(f"🐙 **Fetching GitHub profile:** `{username}`...")
    url = f"https://api.github.com/users/{username}"
    headers = {"User-Agent": "OmniUserBot-Telegram"}

    data = await fetch_json(url, headers=headers)
    if not data or data.get("message") == "Not Found":
        await msg.edit(f"❌ GitHub user `{username}` not found.")
        return

    name = data.get("name") or username
    bio = data.get("bio") or "No bio available."
    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    company = data.get("company") or "N/A"
    location = data.get("location") or "N/A"
    blog = data.get("blog") or "N/A"
    profile_url = data.get("html_url", f"https://github.com/{username}")

    out = (
        f"🐙 **GitHub User: [{name}]({profile_url})** (@{username})\n\n"
        f"💬 **Bio:** {bio}\n\n"
        f"📦 **Public Repos:** `{public_repos}`\n"
        f"👥 **Followers:** `{followers}` | **Following:** `{following}`\n"
        f"🏢 **Company:** `{company}` | 📍 **Location:** `{location}`\n"
        f"🌐 **Website:** {blog}\n"
        f"🔗 [View Profile]({profile_url})"
    )
    await msg.edit(out, link_preview=False)


@omni_cmd(
    pattern="so",
    desc="Searches StackOverflow for coding questions and top answers.",
    usage=".so <programming question>",
    category="Web Search",
    aliases=["stackoverflow"]
)
async def stackoverflow_search(event):
    query = event.text_args.strip()
    if not query:
        await event.reply_or_edit("💻 **Usage:** `.so <programming question>`")
        return

    msg = await event.reply_or_edit(f"💻 **Searching StackOverflow for:** `{query}`...")
    url = f"https://api.stackexchange.com/2.3/search?order=desc&sort=votes&intitle={urllib.parse.quote(query)}&site=stackoverflow"
    data = await fetch_json(url)

    if not data or not data.get("items"):
        await msg.edit(f"❌ No StackOverflow solutions found for: `{query}`")
        return

    out = [f"💻 **StackOverflow Solutions for:** `{query}`\n"]
    for i, item in enumerate(data["items"][:4], 1):
        title = item.get("title", "Question")
        link = item.get("link", "")
        score = item.get("score", 0)
        answered = "✅ Answered" if item.get("is_answered") else "❓ Unanswered"
        out.append(f"**{i}. [{title}]({link})**\n⭐ Score: `{score}` | {answered}\n")

    await msg.edit("\n".join(out), link_preview=False)


@omni_cmd(
    pattern="webread",
    desc="Extracts and summarizes readable content from any webpage (Reader Mode).",
    usage=".webread <url>",
    category="Web Search",
    aliases=["scrape", "readweb"]
)
async def web_reader(event):
    url = event.text_args.strip()
    if not url:
        reply = await event.get_reply_message()
        if reply and reply.text:
            for word in reply.text.split():
                if word.startswith("http://") or word.startswith("https://"):
                    url = word
                    break

    if not url:
        await event.reply_or_edit("📰 **Usage:** `.webread <url>`\nOr reply to a message containing a URL.")
        return

    msg = await event.reply_or_edit(f"📰 **Scraping and parsing article:** `{url}`...")
    html_content = await fetch_text(url)
    if not html_content:
        await msg.edit("❌ Failed to fetch webpage content. Site may be protected or unreachable.")
        return

    clean_text = clean_html_to_markdown(html_content, max_chars=3000)
    out = (
        f"📰 **Web Article Reader: [{url}]({url})**\n\n"
        f"{clean_text}"
    )
    await msg.edit(out, link_preview=False)


@omni_cmd(
    pattern="weather",
    desc="Gets real-time global weather report and forecast without API key.",
    usage=".weather <city>",
    category="Web Search",
    aliases=["wttr"]
)
async def weather_info(event):
    city = event.text_args.strip() or "London"
    msg = await event.reply_or_edit(f"🌦️ **Checking weather for:** `{city}`...")

    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
    weather_headers = {"User-Agent": "curl/7.68.0"}
    data = await fetch_json(url, headers=weather_headers)

    if not data or not data.get("current_condition"):
        await msg.edit(f"❌ Weather data unavailable for `{city}`.")
        return

    current = data["current_condition"][0]
    temp_c = current.get("temp_C", "?")
    temp_f = current.get("temp_F", "?")
    feels_c = current.get("FeelsLikeC", "?")
    humidity = current.get("humidity", "?")
    wind_kmph = current.get("windspeedKmph", "?")
    desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")

    loc = data.get("nearest_area", [{}])[0]
    area = loc.get("areaName", [{}])[0].get("value", city)
    country = loc.get("country", [{}])[0].get("value", "")

    out = (
        f"🌦️ **Weather in {area}, {country}**\n\n"
        f"• **Condition:** `{desc}`\n"
        f"• **Temperature:** `{temp_c}°C` / `{temp_f}°F` (Feels like `{feels_c}°C`)\n"
        f"• **Humidity:** `{humidity}%`\n"
        f"• **Wind Speed:** `{wind_kmph} km/h`\n"
        f"• **Forecast:** [Live Radar & Weather](https://wttr.in/{urllib.parse.quote(city)})"
    )
    await msg.edit(out, link_preview=False)


@omni_cmd(
    pattern="crypto",
    desc="Live cryptocurrency prices and 24-hour trends.",
    usage=".crypto <symbol/name>",
    category="Web Search",
    aliases=["coin"]
)
async def crypto_price(event):
    coin = (event.text_args.strip() or "bitcoin").lower()
    msg = await event.reply_or_edit(f"🪙 **Fetching crypto price for:** `{coin}`...")

    # Map common aliases
    alias_map = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "bnb": "binancecoin", "xrp": "ripple", "doge": "dogecoin", "ton": "the-open-network"}
    coin_id = alias_map.get(coin, coin)

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,inr,eur&include_24hr_change=true"
    data = await fetch_json(url)

    if not data or coin_id not in data:
        await msg.edit(f"❌ Cryptocurrency `{coin}` not found. Try full name (e.g., `bitcoin`, `ethereum`, `solana`).")
        return

    coin_data = data[coin_id]
    usd = coin_data.get("usd", 0)
    inr = coin_data.get("inr", 0)
    eur = coin_data.get("eur", 0)
    change = coin_data.get("usd_24h_change", 0.0)
    trend_emoji = "📈" if change >= 0 else "📉"

    out = (
        f"🪙 **Crypto: {coin.upper()}**\n\n"
        f"💵 **USD:** `${usd:,.2f}`\n"
        f"💶 **EUR:** `€{eur:,.2f}`\n"
        f"🇮🇳 **INR:** `₹{inr:,.2f}`\n\n"
        f"{trend_emoji} **24h Change:** `{change:+.2f}%`"
    )
    await msg.edit(out)


@omni_cmd(
    pattern="ud",
    desc="Looks up words or slang in Urban Dictionary.",
    usage=".ud <term>",
    category="Web Search",
    aliases=["urban"]
)
async def urban_dict(event):
    term = event.text_args.strip()
    if not term:
        await event.reply_or_edit("📖 **Usage:** `.ud <slang/word>`")
        return

    msg = await event.reply_or_edit(f"📖 **Searching Urban Dictionary for:** `{term}`...")
    url = f"https://api.urbandictionary.com/v0/define?term={urllib.parse.quote(term)}"
    data = await fetch_json(url)

    if not data or not data.get("list"):
        await msg.edit(f"❌ No Urban Dictionary definition found for `{term}`.")
        return

    top = data["list"][0]
    word = top.get("word", term)
    definition = top.get("definition", "").replace("[", "").replace("]", "")
    example = top.get("example", "").replace("[", "").replace("]", "")
    thumbs_up = top.get("thumbs_up", 0)
    thumbs_down = top.get("thumbs_down", 0)

    if len(definition) > 1000:
        definition = definition[:1000] + "..."

    out = (
        f"📖 **Urban Dictionary: {word}**\n\n"
        f"💡 **Definition:**\n{definition}\n\n"
        f"💬 **Example:**\n_{example}_\n\n"
        f"👍 `{thumbs_up}` | 👎 `{thumbs_down}`"
    )
    await msg.edit(out)


@omni_cmd(
    pattern="ip",
    desc="Inspects IP address or domain geolocation and network details.",
    usage=".ip <ip or domain>",
    category="Web Search",
    aliases=["whois"]
)
async def ip_lookup(event):
    target = event.text_args.strip()
    if not target:
        await event.reply_or_edit("🌐 **Usage:** `.ip <ip address or domain>`")
        return

    msg = await event.reply_or_edit(f"🌐 **Querying IP/Domain:** `{target}`...")
    url = f"http://ip-api.com/json/{urllib.parse.quote(target)}"
    data = await fetch_json(url)

    if not data or data.get("status") != "success":
        await msg.edit(f"❌ Failed to locate `{target}`. Make sure it is a valid IP or domain.")
        return

    query = data.get("query", target)
    country = data.get("country", "Unknown")
    region = data.get("regionName", "Unknown")
    city = data.get("city", "Unknown")
    isp = data.get("isp", "Unknown")
    org = data.get("org", "Unknown")
    as_info = data.get("as", "Unknown")
    timezone = data.get("timezone", "Unknown")

    out = (
        f"🌐 **IP Geolocation: `{query}`**\n\n"
        f"📍 **Location:** `{city}, {region}, {country}`\n"
        f"🏢 **ISP:** `{isp}`\n"
        f"🏢 **Org:** `{org}`\n"
        f"🌐 **ASN:** `{as_info}`\n"
        f"⏰ **Timezone:** `{timezone}`"
    )
    await msg.edit(out)


@omni_cmd(
    pattern="paste",
    desc="Pastes text or replied message to a clean web pastebin (dpaste).",
    usage=".paste <text or reply>",
    category="Web Search"
)
async def paste_text(event):
    text = event.text_args
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text

    if not text:
        await event.reply_or_edit("📋 **Usage:** `.paste <text>` or reply to a text message.")
        return

    msg = await event.reply_or_edit("📋 **Creating web paste...**")
    url = "https://dpaste.com/api/v2/"
    data = {"content": text, "syntax": "text", "expiry_days": 7}

    res = await http_client.post_form(url, data=data)
    if res and res.startswith("http"):
        paste_link = res.strip()
        await msg.edit(
            f"📋 **Paste Created Successfully!**\n"
            f"🔗 **URL:** [View Paste]({paste_link})\n"
            f"⏳ **Expires in:** `7 days`"
        )
    else:
        await msg.edit("❌ Failed to create paste. Please try again.")
