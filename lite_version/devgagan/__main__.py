# ---------------------------------------------------
# File Name: __main__.py (Lite Version)
# Description: Minimal entry point for the Lite version.
# ---------------------------------------------------

import asyncio
import importlib
from pyrogram import idle
from devgagan.modules import ALL_MODULES

async def devggn_boot():
    for all_module in ALL_MODULES:
        importlib.import_module("devgagan.modules." + all_module)
    print("""
---------------------------------------------------
🚀 Lite Content Saver Bot Deployed! 🚀
Description: Fast & Clean Content Extraction.
---------------------------------------------------
""")
    await idle()
    print("Bot stopped...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(devggn_boot())
