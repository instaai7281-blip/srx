# ---------------------------------------------------
# File Name: __init__.py (Lite Version)
# Description: Minimal initialization for the Lite version.
# ---------------------------------------------------

import asyncio
import logging
import time
from pyrogram import Client
from telethon.sync import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, OWNER_ID

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

# Main Pyrogram Client
app = Client(
    "LiteRestrictBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50
)

# Telethon Client for fast-upload/extraction
from telethon.errors import FloodWaitError
import sys

# Telethon Client for fast-upload/extraction with FloodWait handling
try:
    sex = TelegramClient('sexrepo_lite', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
except FloodWaitError as f:
    print(f"TELETHON FLOODWAIT: A wait of {f.seconds} seconds is required.")
    print(f"The lite bot will sleep for 60 seconds and then exit to prevent a restart loop.")
    time.sleep(60)
    sys.exit(1)
except Exception as e:
    print(f"TELETHON ERROR: {e}")
    sex = None


# Optional Premium Client
pro = Client("pro_client", api_id=API_ID, api_hash=API_HASH, session_string=STRING) if STRING else None

# MongoDB setup (Minimal)
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["lite_bot_db"]

async def start_lite_bot():
    global BOT_ID, BOT_USERNAME
    await app.start()
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    if pro: await pro.start()
    print(f"🚀 Lite Bot started as @{BOT_USERNAME}")
    for owner in OWNER_ID:
        try: await app.send_message(owner, f"🚀 Lite Bot @{BOT_USERNAME} is Online!")
        except: pass

# Start the bot
loop = asyncio.get_event_loop()
loop.run_until_complete(start_lite_bot())
