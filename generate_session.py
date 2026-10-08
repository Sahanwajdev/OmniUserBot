#!/usr/bin/env python3
"""
OmniUserBot - Telethon String Session Generator
Run this script to authenticate your Telegram account and obtain a StringSession.
"""

import os
import sys
import asyncio
from pathlib import Path

# Ensure UTF-8 stdout on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv, set_key

ENV_PATH = Path(__file__).resolve().parent / ".env"


async def main():
    print("=" * 60)
    print("   ⚡ OmniUserBot - Telethon StringSession Generator ⚡")
    print("=" * 60)
    print("\nTo obtain your API_ID and API_HASH, visit:")
    print("👉 https://my.telegram.org -> 'API development tools'\n")

    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)

    env_api_id = os.getenv("API_ID", "").strip()
    env_api_hash = os.getenv("API_HASH", "").strip()

    # Get API_ID
    while True:
        default_prompt = f" [{env_api_id}]" if env_api_id else ""
        raw_id = input(f"Enter API_ID{default_prompt}: ").strip() or env_api_id
        if raw_id.isdigit():
            api_id = int(raw_id)
            break
        print("❌ Invalid API_ID. It must be an integer.")

    # Get API_HASH
    default_prompt = f" [{env_api_hash[:6]}...]" if env_api_hash else ""
    api_hash = input(f"Enter API_HASH{default_prompt}: ").strip() or env_api_hash
    while not api_hash:
        api_hash = input("Enter API_HASH: ").strip()

    print("\nConnecting to Telegram servers...")
    client = TelegramClient(StringSession(), api_id, api_hash)

    try:
        await client.start()
    except Exception as e:
        print(f"\n❌ Login Failed: {e}")
        return

    me = await client.get_me()
    session_string = client.session.save()

    print("\n" + "=" * 60)
    print(f"🎉 Successfully authenticated as: {me.first_name} [ID: {me.id}]")
    print("=" * 60)
    print("\n🔑 YOUR TELETHON STRING SESSION:\n")
    print(session_string)
    print("\n⚠️ WARNING: Treat this string like your password. Never share it!\n")

    save_env = input("Would you like to automatically save this to your .env file? (Y/n): ").strip().lower()
    if save_env in ("", "y", "yes"):
        if not ENV_PATH.exists():
            example_path = Path(__file__).resolve().parent / ".env.example"
            if example_path.exists():
                ENV_PATH.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                ENV_PATH.touch()

        set_key(str(ENV_PATH), "API_ID", str(api_id))
        set_key(str(ENV_PATH), "API_HASH", str(api_hash))
        set_key(str(ENV_PATH), "STRING_SESSION", session_string)
        print("✅ Credentials and StringSession saved to .env!")

    print("\n🚀 You can now start OmniUserBot by running: python main.py\n")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
