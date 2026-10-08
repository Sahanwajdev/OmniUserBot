# ⚡ OmniUserBot

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Telethon](https://img.shields.io/badge/Telethon-v1.45+-orange.svg)](https://github.com/LonamiWebs/Telethon)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Ultra--Fast%20%26%20Active-brightgreen.svg)](#)

**The Most Powerful Telegram Userbot on GitHub — Built for Supercharged Web Search, Media Automation, Group Moderation, and Developer Tooling.**

[Features](#-key-features) • [Command Reference](#-complete-command-matrix) • [Quick Start](#-quick-start) • [Deployment](#-deployment-options) • [Architecture](#-project-structure)

</div>

---

## 🌟 Why OmniUserBot?

Most classic Telegram userbots on GitHub (CatUserBot, Paperplane, Ultroid, Userge) suffer from **"dead commands"**:
* ❌ Dead pastebins (hastebin/dogbin endpoints shut down).
* ❌ Broken Google scraping caused by IP bans and captcha blockers.
* ❌ Expired weather/crypto tokens from defunct third-party APIs.
* ❌ Broken dependencies due to breaking changes in newer Python & Telethon versions.

**OmniUserBot fixes this once and for all:**
* ✅ **100% Active, Resilient Endpoints:** Zero dependence on transient third-party tokens. Uses DuckDuckGo, Wikimedia REST APIs, public GitHub REST APIs, wttr.in, CoinGecko, and resilient multi-engine translation fallbacks.
* ✅ **Reader Mode Web Scraping:** Extracts clean article text from any link directly within Telegram without clutter.
* ✅ **Modern Telethon Async Engine:** Built on the latest, high-performance Telethon async framework compatible with modern Python (3.10 - 3.14+).
* ✅ **Zero-Downtime Hot Reloading:** Modify or add plugins and reload them instantly with `.reload` without restarting Python!

---

## 🚀 Key Features

* 🌐 **Supercharged Web Suite:** DuckDuckGo instant search, Google search, Wikipedia deep extracts, GitHub repository & user inspection, StackOverflow developer search, lyrics scraper (Genius/DDG), news headlines, DNS over HTTPS, real-time weather, live cryptocurrency tracking, Urban Dictionary, IP/domain geolocation, URL shortener/expander, and instant web pasting.
* 🛡️ **Group Moderation & Admin Powers:** High-speed bulk purge (up to 200 messages at once), granular chat permission locks (`.lock` / `.unlock` media, stickers, links, etc.), auto-zombie cleaner (removes deleted accounts), ban, unban, timed mute, unmuting, admin listing, kick, and customizable promote titles.
* 🚫 **DM Protect & Instant Direct Block:** Ultra-strict anti-spam direct message defense. In `block` mode, **any unauthorized stranger who DMs you is directly and instantly blocked**! Includes an allowed whitelist system (`.allow`, `.disallow`, `.allowed`), customizable rejection notice, and warning mode.
* 🔐 **Telegram Account Security & Anti-Theft:** Inspect all active devices and sessions logged into your account (`.sessions`), terminate/kill all other active sessions with a single command (`.killall`), and clear unread badges (`.readall`).
* 📝 **Persistent Notes & Chat Keyword Filters:** Save custom text/media snippets (`.save`, `.get`, `.notes`) and configure keyword triggers (`.filter`, `.stop`, `.filters`) that automatically reply when triggered.
* 🎭 **Profile Controls & Cloning:** Change your name (`.setname`), bio (`.setbio`), profile photo (`.setpfp`), or temporarily clone any user's profile (`.clone`) and restore with `.revert`.
* 🤖 **Smart AFK Mode:** Tracks time away from keyboard, automatically notifies anyone who mentions or private messages you with anti-flood rate limiting, and deactivates the moment you send a message.
* 🛠️ **Utility & Media Tools:** Multi-language translation with fallback, Google Text-to-Speech audio notes, custom QR code generator, safe mathematical expression evaluator, sticker-to-image/image-to-sticker conversion, and direct YouTube search & download.
* 💻 **Developer Execution:** Live asynchronous Python code REPL (`.eval`) with full Telegram client context and asynchronous terminal shell command runner (`.sh`).

---

## 📖 Complete Command Matrix

All commands use the configurable prefix (default: `.`). You can configure multiple prefixes like `.!` in `.env`.

### 🌐 1. Web Search & Intelligence
| Command | Arguments | Description | Example |
| :--- | :--- | :--- | :--- |
| `.ddg` | `<query>` | Searches DuckDuckGo for top web results with snippets | `.ddg python async tutorial` |
| `.google` | `<query>` | Fast web search aggregator | `.google telegram bot api` |
| `.wiki` | `<topic>` | Queries Wikipedia for encyclopedic article summaries | `.wiki Quantum Computing` |
| `.gh` | `<owner/repo>` | Inspects GitHub repository (stars, forks, issues, license) | `.gh LonamiWebs/Telethon` |
| `.ghuser` | `<username>` | Fetches public GitHub user profile details | `.ghuser torvalds` |
| `.so` | `<question>` | Searches StackOverflow for top-voted solutions | `.so python dict sort` |
| `.webread`| `<url>` | Scrapes article into clean markdown reader mode | `.webread https://example.com/article` |
| `.weather`| `<city>` | Real-time global weather, humidity, and wind stats | `.weather Tokyo` |
| `.crypto` | `<symbol>` | Live crypto prices in USD, EUR, INR + 24h change | `.crypto btc` |
| `.ud` | `<term>` | Looks up slang and definitions on Urban Dictionary | `.ud yeet` |
| `.ip` | `<ip/domain>` | Geolocation, ISP, ASN, and timezone lookup | `.ip 1.1.1.1` |
| `.paste` | `<text/reply>` | Uploads long text or code to permanent web paste | `.paste (reply to text)` |

### ⚡ 2. System & Core Controls
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.alive` | _None_ | Displays rich status card, owner, uptime, CPU, RAM, and versions |
| `.ping` | _None_ | Measures sub-millisecond round-trip Telegram server latency |
| `.sysinfo` | _None_ | Complete hardware breakdown (OS, CPU cores, RAM, Disk usage) |
| `.reload` | _None_ | **Hot-reloads all plugins dynamically** without restarting the process |
| `.restart` | _None_ | Gracefully restarts the userbot process |

### 🛡️ 3. Admin & Group Moderation
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.purge` | `[count/reply]` | Rapidly deletes messages up to the replied target or by count |
| `.del` | _Reply_ | Deletes the replied message |
| `.pin` | `[loud]` | Pins replied message (silent by default; add `loud` to notify) |
| `.unpin` | `[all]` | Unpins replied message or all pinned messages |
| `.ban` | `<user> [reason]` | Bans user from current group |
| `.unban` | `<user>` | Unbans user in current group |
| `.mute` | `<user> [duration]` | Mutes user indefinitely or with duration (e.g. `10m`, `2h`, `1d`) |
| `.unmute`| `<user>` | Unmutes user in current group |
| `.kick` | `<user>` | Kicks user from group |
| `.promote`| `<user> [title]` | Promotes user with custom admin title |
| `.demote`| `<user>` | Demotes admin back to normal member |
| `.admins`| _None_ | Lists all group administrators and bots |
| `.zombies`| `[clean]` | Detects (or removes with `clean`) deleted accounts |

### 😴 4. Automation & AFK
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.afk` | `[reason]` | Activates Away-From-Keyboard mode with auto-reply to tags & PMs |
| _Any Message_ | _Any_ | **Auto-disables AFK** the moment you type any message in any chat! |

### 🛠️ 5. Tools & Utilities
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.tr` | `<lang> [text/reply]` | Multi-engine text translation (e.g. `.tr es hello world`) |
| `.tts` | `[lang] <text>` | Generates Google Text-to-Speech audio voice message |
| `.qr` | `<text/link>` | Generates custom QR code image directly in chat |
| `.calc` | `<expression>` | Evaluates mathematical expressions safely |
| `.id` | `[reply]` | Returns IDs of Chat, User, and replied Message |
| `.info` | `[user/reply]` | Fetches full Telegram user profile details and DC ID |

### 🎥 6. Media & Transfer
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.yt` | `<query>` | Searches YouTube videos with titles, duration, and URLs |
| `.ytdl` | `<url> [audio/video]`| Downloads YouTube media via `yt-dlp` and sends to Telegram |
| `.stoi` | _Reply_ | Converts a Telegram sticker to PNG image |
| `.itos` | _Reply_ | Converts a photo to WebP Telegram sticker |
| `.upload` | `<filepath>` | Uploads local file from host machine to Telegram with progress bar |
| `.download`| _Reply_ | Downloads Telegram media to local disk with progress bar |

### 🎮 7. Fun & Expressions
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.type` | `<text>` | Live typewriter animation editing effect |
| `.slap` | `[user/reply]` | Comical slap generator with randomized items |
| `.shrug` | _None_ | Sends `¯\_(ツ)_/¯` |
| `.tableflip` | _None_ | Sends `(╯°□°)╯︵ ┻━┻` |
| `.unflip` | _None_ | Sends `┬─┬ノ( º _ ºノ)` |
| `.facepalm` | _None_ | Sends `🤦‍♂️` |

### 💻 8. Developer Execution
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.eval` | `<code>` | Asynchronous live Python evaluation with stdout & context capture |
| `.sh` | `<command>` | Live asynchronous terminal / shell command runner |

### ❓ 9. Help Center
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `.help` | _None_ | Displays interactive categorized listing of all loaded modules |
| `.help` | `<command>` | Displays detailed syntax, description, and aliases for a command |

---

## ⚡ Quick Start

### 1. Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/OmniUserBot.git
cd OmniUserBot

# Install Python requirements
pip install -r requirements.txt
```

### 2. Configure Environment

1. Get your **API_ID** and **API_HASH** from [https://my.telegram.org](https://my.telegram.org) under "API development tools".
2. Run the interactive StringSession generator:

```bash
python generate_session.py
```

Follow the prompts to enter your phone number, verification code, and 2FA password (if enabled). The script will automatically generate your `STRING_SESSION` and offer to save it directly into `.env`.

Alternatively, manually copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
And fill in:
```env
API_ID=12345678
API_HASH=your_telegram_api_hash
STRING_SESSION=your_generated_string_session
COMMAND_PREFIX=.
```

### 3. Launch OmniUserBot

```bash
python main.py
```

Test it by sending `.alive` or `.help` in any Telegram chat!

---

## 🐳 Deployment Options

### Option A: Docker / Docker Compose (Recommended for 24/7 VPS)

```bash
# 1. Ensure .env is populated with credentials
# 2. Start container in background
docker compose up -d --build

# 3. View live logs
docker compose logs -f
```

### Option B: Systemd Service (Linux VPS)

Create `/etc/systemd/system/omniuserbot.service`:

```ini
[Unit]
Description=OmniUserBot Telegram Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/OmniUserBot
ExecStart=/usr/bin/python3 /root/OmniUserBot/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable omniuserbot
systemctl start omniuserbot
```

### Option C: Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install python git clang ffmpeg -y
git clone https://github.com/yourusername/OmniUserBot.git
cd OmniUserBot
pip install -r requirements.txt
python generate_session.py
python main.py
```

---

## 📁 Project Structure

```text
OmniUserBot/
├── config.py                 # Central configuration loader
├── main.py                   # Bot entrypoint & lifecycle management
├── generate_session.py       # Interactive Telethon StringSession generator
├── requirements.txt          # Production dependencies
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Docker compose service setup
├── .env.example              # Environment variables template
├── core/
│   ├── client.py             # OmniClient wrapper & Telegram methods
│   ├── decorators.py         # @omni_cmd decorator & permission enforcement
│   ├── loader.py             # Dynamic plugin discovery & hot-reload engine
│   └── logger.py             # Colorized logging system
├── helpers/
│   ├── formatting.py         # Progress bars, time/byte formatters, HTML cleaner
│   ├── http_client.py        # Asynchronous HTTP pooling & fetchers
│   ├── system_info.py        # CPU, RAM, Disk, OS hardware metrics
│   └── telegram_tools.py     # User resolver, admin checks, time delta parser
└── plugins/
    ├── web_search.py         # DuckDuckGo, Google, Wiki, GitHub, SO, Weather, etc.
    ├── system.py             # .alive, .ping, .reload, .restart, .sysinfo
    ├── admin.py              # .purge, .del, .ban, .mute, .promote, .zombies
    ├── afk.py                # Smart AFK tracking & auto-responses
    ├── tools.py              # .tr, .tts, .qr, .calc, .id, .info
    ├── media.py              # .yt, .ytdl, .stoi, .itos, .upload, .download
    ├── fun.py                # .type, .slap, .shrug, kaomojis
    ├── exec.py               # .eval (Python REPL), .sh (Terminal executor)
    └── help.py               # Dynamic categorized help menu & command manual
```

---

## 🛡️ Security & Anti-Ban Best Practices

1. **Keep Sessions Private:** Never share your `STRING_SESSION` or `.session` file with anyone. It grants access to your Telegram account.
2. **FloodWait Respect:** OmniUserBot includes built-in sleeps and batching for bulk commands (such as purge) to respect Telegram's rate limits.
3. **Use Common Sense:** Avoid spamming public groups with automated commands.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
