<div align="center">

<img src="https://files.catbox.moe/iiwd58.jpg" alt="OmniUserBot Banner" width="700" style="border-radius: 10px;" />

# OMNIUSERBOT

**High-Performance Modular Telegram Userbot Powered by Telethon & MTProto**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Telethon-v1.36+-2BA3D0.svg?style=for-the-badge&logo=telegram&logoColor=white" alt="Telethon" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready" />
  <img src="https://img.shields.io/badge/License-MIT-success.svg?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <a href="https://render.com/deploy?repo=https://github.com/Sahanwajdev/OmniUserBot">
    <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" />
  </a>
  <a href="https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FSahanwajdev%2FOmniUserBot">
    <img src="https://railway.app/button.svg" alt="Deploy on Railway" />
  </a>
  <a href="https://app.koyeb.com/deploy?type=git&repository=Sahanwajdev%2FOmniUserBot&branch=main">
    <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb" />
  </a>
  <a href="https://heroku.com/deploy?template=https://github.com/Sahanwajdev/OmniUserBot">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" />
  </a>
</p>

</div>

---

## Overview

OmniUserBot is an enterprise-grade Telegram automation framework built on Telethon. It features an integrated inline helper bot for native Telegram inline keyboard buttons, real-time direct message security with automated blocking, high-performance multimedia downloading, advanced profile cloning and restoration, and mass tagging utilities.

---

## Core Capabilities

<div align="center">

| Component | Technical Specification |
| :--- | :--- |
| **Inline Command Hub** | Dual-client architecture combining user session with an inline helper bot to deliver responsive 3-column inline keyboards. |
| **DM Guard Engine** | Real-time incoming private message gatekeeper supporting immediate blocking or configurable warning thresholds. |
| **Media Pipeline** | Integrated yt-dlp multimedia processor with automatic resolution selection, audio extraction, and audio-video format segregation. |
| **Identity Management** | Snapshot-based profile replication with one-command rollback of name, bio, and avatar. |
| **Chat Pruning** | High-speed departure routine that identifies and vacates non-owned groups while protecting owned assets. |
| **Mass Communication** | Multi-threaded tagger supporting customizable message themes and interval-regulated member mentions. |

</div>

---

## Cloud Deployment

### Method 1: Deploy on Render

1. Fork or clone this repository to your GitHub account.
2. Sign in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** and select **Blueprint**.
4. Connect your GitHub repository containing OmniUserBot.
5. Render detects `render.yaml` automatically and configures a **Background Worker**.
6. Set the required environment variables in the Render console:
   - `API_ID`
   - `API_HASH`
   - `STRING_SESSION`
   - `BOT_TOKEN`
   - `BOT_USERNAME`
7. Click **Apply**. Render will install dependencies and launch `python main.py`.

---

### Method 2: Deploy with Docker & Docker Compose

```bash
# Clone the repository
git clone https://github.com/Sahanwajdev/OmniUserBot.git
cd OmniUserBot

# Create environment configuration
cp .env.example .env
# Edit .env with your credentials

# Launch via Docker Compose
docker compose up -d --build

# View operational logs
docker compose logs -f
```

---

### Method 3: Deploy on Linux / VPS (Systemd Service)

```bash
# Clone repository
git clone https://github.com/Sahanwajdev/OmniUserBot.git /opt/OmniUserBot
cd /opt/OmniUserBot

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Create Systemd unit file
sudo tee /etc/systemd/system/omniuserbot.service > /dev/null <<EOF
[Unit]
Description=OmniUserBot Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/OmniUserBot
ExecStart=/opt/OmniUserBot/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable omniuserbot
sudo systemctl start omniuserbot
```

---

## Configuration Reference

Configure parameters in `.env` or as environment variables in your cloud provider:

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `API_ID` | Yes | - | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Yes | - | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `STRING_SESSION` | Yes | - | Telethon String Session generated via `generate_session.py` |
| `BOT_TOKEN` | Yes | - | Bot Token from [@BotFather](https://t.me/BotFather) for inline buttons |
| `BOT_USERNAME` | Yes | - | Assistant bot username without leading `@` |
| `COMMAND_PREFIX` | No | `.` | Command prefix character |
| `SUDO_USERS` | No | - | Space-separated Telegram user IDs with administrative privileges |
| `LOG_CHAT_ID` | No | - | Channel or group ID for real-time diagnostic reporting |
| `BOT_NAME` | No | `OmniUserBot` | Bot name identifier across menus and headers |

---

## Module Index

The system includes 102 integrated commands organized into 13 modules:

<div align="center">

| Module | Count | Command Highlights |
| :--- | :---: | :--- |
| **Admin** | 17 | `.del`, `.purge`, `.pin`, `.unpin`, `.ban`, `.unban`, `.mute`, `.unmute`, `.kick`, `.promote`, `.demote`, `.zombies`, `.title`, `.invite`, `.gban`, `.ungban` |
| **Security** | 8 | `.dmprotect on/off/mode`, `.allow`, `.disallow`, `.allowed`, `.sessions`, `.killall` |
| **Media** | 8 | `.ytdl [url]`, `.song [query]`, `.video [query]`, `.yt [query]`, `.stoi` |
| **Tools** | 12 | `.leftall`, `.readall`, `.cat`, `.dns`, `.shorten`, `.unshorten`, `.paste`, `.speedtest` |
| **Tagger** | 9 | `.tagall`, `.tagshari`, `.taggm`, `.taggn`, `.taglove`, `.tagcancel` |
| **Profile** | 6 | `.clone [user]`, `.revert`, `.setname`, `.setbio`, `.setpfp`, `.delpfp` |
| **Web Search** | 14 | `.ddg`, `.google`, `.wiki`, `.lyrics`, `.news`, `.weather`, `.ud` |
| **Notes & Filters** | 7 | `.save`, `.get`, `.clear`, `.notes`, `.filter`, `.stop`, `.filters` |
| **Fun & Memes** | 16 | `.type`, `.slap`, `.shrug`, `.tableflip`, `.unflip`, `.dice`, `.meme`, `.pat` |
| **System** | 6 | `.alive`, `.ping`, `.sysinfo`, `.setprefix`, `.reload`, `.restart` |
| **Automation** | 1 | `.afk [reason]` |
| **Developer** | 2 | `.eval [code]`, `.sh [cmd]` |
| **General** | 1 | `.help [category/command/all]` |

</div>

---

## Session String Generation

To generate your Telethon String Session securely on your local workstation:

```bash
python generate_session.py
```

Follow the interactive prompt to log in with your phone number and 2FA password. Copy the resulting session key into your `.env` or cloud service dashboard.

---

## License

Distributed under the terms of the **MIT License**. Refer to [LICENSE](LICENSE) for additional information.
