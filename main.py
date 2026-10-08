#!/usr/bin/env python3
"""
OmniUserBot - Main Runner
The Ultimate, Modular Telegram Userbot with Supercharged Web Search.
"""

import sys
import asyncio
import signal
from pathlib import Path

# Ensure UTF-8 stdout on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import config
from core.logger import log
from core.client import OmniClient
from core.loader import load_plugins
import core.client as client_module

BANNER = r"""
  ___                  _ _   _              ___       _   
 / _ \ _ __ ___  _ __ (_) | | |___  ___ _ _| _ ) ___ | |_ 
| (_) | '  \ _ \| '_ \| | |_| (_-< / -_) '_| _ \/ _ \|  _|
 \___/|_|_|_|___/ .__/|_|\___//__/ \___|_| |___/\___/ \__|
                |_|                                        
          ⚡ The Ultimate Supercharged Userbot ⚡
"""


async def main():
    print(BANNER)

    # Validate essential configuration
    if not config.API_ID or not config.API_HASH:
        log.error("Missing API_ID or API_HASH in your configuration!")
        print("\n" + "=" * 65)
        print("❌ SETUP REQUIRED:")
        print("1. Copy `.env.example` to `.env`:")
        print("   cp .env.example .env (or copy on Windows)")
        print("2. Obtain API_ID & API_HASH from https://my.telegram.org")
        print("3. Run the interactive session generator to login:")
        print("   python generate_session.py")
        print("=" * 65 + "\n")
        sys.exit(1)

    log.info("Starting OmniUserBot...")

    # Initialize client
    try:
        bot = OmniClient()
        client_module.bot = bot
    except Exception as e:
        log.error(f"Failed to initialize client: {e}")
        sys.exit(1)

    # Start client session
    try:
        if config.STRING_SESSION:
            await bot.start()
        else:
            log.info("Starting local session login...")
            await bot.start()
    except Exception as e:
        log.error(f"Failed to start Telegram client: {e}")
        sys.exit(1)

    # Cache user profile and send log notification
    await bot.init_client()

    # Start assistant bot for inline queries and inline buttons
    await bot.start_assistant_bot()

    # Load all plugins
    loaded_count = load_plugins(bot)
    log.info(f"Successfully loaded {loaded_count} plugin modules with {len(bot.commands)} commands.")
    log.info(f"OmniUserBot is active! Active command prefix: '{config.COMMAND_PREFIXES[0]}'")
    log.info("Send .alive or .help in any Telegram chat to test.")

    # Graceful shutdown handler
    stop_event = asyncio.Event()

    def signal_handler():
        log.info("Received termination signal. Shutting down gracefully...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Signal handling on Windows
            pass

    try:
        # Run until disconnected
        await bot.run_until_disconnected()
    except (KeyboardInterrupt, SystemExit):
        log.info("Stopping OmniUserBot...")
    finally:
        if bot.is_connected():
            await bot.disconnect()
        log.info("OmniUserBot stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
