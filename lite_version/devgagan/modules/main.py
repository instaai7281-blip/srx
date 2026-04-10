# ---------------------------------------------------
# File Name: main.py (Lite Version)
# Description: Streamlined message handler for fast extraction.
# ---------------------------------------------------

import asyncio
from pyrogram import filters, Client
from devgagan import app
from config import API_ID, API_HASH, OWNER_ID
from devgagan.core.get_func import get_msg
from devgagan.core.func import *
from devgagan.core.mongo import db
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# Tracking loops
users_loop = {}
batch_mode = {}

async def process_and_upload_link(userbot, user_id, msg_id, link, retry_count, message):
    try:
        await get_msg(userbot, user_id, msg_id, link, retry_count, message)
        await asyncio.sleep(2) # Minimal delay for speed
    finally:
        pass

@app.on_message(
    filters.regex(r'https?://(?:www\.)?t\.me/[^\s]+|tg://openmessage\?user_id=\w+&message_id=\d+')
    & filters.private
)
async def single_link(_, message):
    user_id = message.chat.id

    # Join check
    if await subscribe(_, message) == 1:
        return

    if users_loop.get(user_id, False):
        await message.reply("Wait for the current process to finish or /cancel.")
        return

    users_loop[user_id] = True
    link = get_link(message.text) if "http" in message.text else message.text
    msg = await message.reply("🚀 Processing...")
    userbot = await initialize_userbot(user_id)

    try:
        await process_and_upload_link(userbot, user_id, msg.id, link, 0, message)
    except FloodWait as fw:
        await msg.edit_text(f'Floodwait: {fw.x}s')
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}")
    finally:
        users_loop[user_id] = False
        if userbot: await userbot.stop()

async def initialize_userbot(user_id):
    data = await db.get_data(user_id)
    if data and data.get("session"):
        try:
            userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=data.get("session"))
            await userbot.start()
            return userbot
        except: return None
    return None

@app.on_message(filters.command("batch") & filters.private)
async def batch_link(_, message):
    if await subscribe(_, message) == 1: return
    user_id = message.chat.id
    if users_loop.get(user_id, False):
        await message.reply("Process already running.")
        return

    # Batch inputs
    try:
        start_link = await app.ask(message.chat.id, "Send start link:")
        start_id = start_link.text.strip()
        cs = int(start_id.split("/")[-1])
        
        num_msg = await app.ask(message.chat.id, "How many messages? (Max 5000):")
        cl = int(num_msg.text.strip())
        if cl > 5000: cl = 5000
    except:
        await message.reply("Invalid input.")
        return

    users_loop[user_id] = True
    userbot = await initialize_userbot(user_id)
    
    try:
        for i in range(cs, cs + cl):
            if not users_loop.get(user_id, True): break
            url = f"{'/'.join(start_id.split('/')[:-1])}/{i}"
            await get_msg(userbot, user_id, message.id, url, 0, message)
            await asyncio.sleep(1)
        await message.reply("Batch Completed! 🎉")
    except Exception as e:
        await message.reply(f"Error: {e}")
    finally:
        users_loop.pop(user_id, None)
        if userbot: await userbot.stop()

@app.on_message(filters.command("cancel"))
async def stop_batch(_, message):
    users_loop[message.chat.id] = False
    await message.reply("Stopped.")
