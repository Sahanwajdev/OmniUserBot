import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
PLUGIN_DIR = BASE_DIR / "plugins"

DOWNLOAD_DIR.mkdir(exist_ok=True)
PLUGIN_DIR.mkdir(exist_ok=True)

# Load .env file
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


class Config:
    """Central configuration for OmniUserBot."""

    BASE_DIR = BASE_DIR
    DOWNLOAD_DIR = DOWNLOAD_DIR
    PLUGIN_DIR = PLUGIN_DIR

    # Telegram API Credentials
    API_ID_RAW = os.getenv("API_ID", "").strip()
    try:
        API_ID = int(API_ID_RAW) if API_ID_RAW else None
    except ValueError:
        API_ID = None

    API_HASH = os.getenv("API_HASH", "").strip() or None

    # Telethon Session String or file name
    STRING_SESSION = os.getenv("STRING_SESSION", "").strip() or None
    SESSION_NAME = os.getenv("SESSION_NAME", "omni_userbot").strip()

    # Command prefixes: defaults to ['.', '!']
    RAW_PREFIXES = os.getenv("COMMAND_PREFIX", ".").strip()
    COMMAND_PREFIXES = list(RAW_PREFIXES) if RAW_PREFIXES else ["."]

    # Sudo users allowed to invoke commands
    RAW_SUDO = os.getenv("SUDO_USERS", "").strip()
    SUDO_USERS = set()
    if RAW_SUDO:
        for uid in RAW_SUDO.split():
            try:
                SUDO_USERS.add(int(uid))
            except ValueError:
                pass

    # Optional Log Chat
    RAW_LOG_CHAT = os.getenv("LOG_CHAT_ID", "").strip()
    try:
        LOG_CHAT_ID = int(RAW_LOG_CHAT) if RAW_LOG_CHAT else None
    except ValueError:
        LOG_CHAT_ID = None

    # Appearance & Branding
    BOT_NAME = os.getenv("BOT_NAME", "OmniUserBot").strip()
    ALIVE_EMOJI = os.getenv("ALIVE_EMOJI", "⚡").strip()
    ALIVE_TEXT = os.getenv("ALIVE_TEXT", "OmniUserBot is online and ultra-fast.").strip()

    # Assistant Bot for Inline Features & Buttons
    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip() or None
    BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip() or None

    # Max Telegram text message length
    MAX_MESSAGE_LENGTH = 4096


# Global config instance
config = Config()
