# ---------------------------------------------------
# File Name: __init__.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: ❉ Sᴛꪮʟᴇɴ Hᴀᴘᴘɪɴᴇss
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------

import asyncio
import logging

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import pyromod
from pyrogram import Client
from pyrogram.enums import ParseMode 
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, OWNER_ID
from telethon.sync import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient
import time

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

app = Client(
    "RestrictBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    parse_mode=ParseMode.MARKDOWN
)

pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)

# Simplified pyromod listeners safety check to prevent RecursionError and KeyError
from pyromod.listen.client import ListenerTypes
for client in [app, pro]:
    if client:
        if not hasattr(client, 'listeners'):
            client.listeners = {lt: {} for lt in ListenerTypes}
        else:
            # Only add missing keys, do not replace the dict or use defaultdict if risky
            for lt in ListenerTypes:
                if lt not in client.listeners:
                    client.listeners[lt] = {}



from telethon.errors import FloodWaitError
import sys

# Initialize Telethon Client with FloodWait handling
try:
    sex = TelegramClient('sexrepo', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
except FloodWaitError as f:
    print(f"TELETHON FLOODWAIT: A wait of {f.seconds} seconds is required.")
    print(f"The bot will sleep for 60 seconds and then exit to prevent a restart loop.")
    time.sleep(60)
    sys.exit(1)
except Exception as e:
    print(f"TELETHON ERROR: {e}")
    sex = None # Fallback if possible, though bot might fail later




# MongoDB setup
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]  # Your database
token = tdb["tokens"]  # Your tokens collection

async def create_ttl_index():
    """Ensure the TTL index exists for the `tokens` collection."""
    await token.create_index("expires_at", expireAfterSeconds=0)

# Run the TTL index creation when the bot starts
async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")

# You can call this in your main bot file before starting the bot

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await setup_database()
    await app.start()
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name
    if STRING:
        await pro.start()
    
    for owner in OWNER_ID:
        try:
            await app.send_message(owner, f"Bot started successfully! @{BOT_USERNAME}")
        except Exception as e:
            logging.error(f"Failed to send message to owner {owner}: {e}")

# loop.run_until_complete(restrict_bot())
