# ---------------------------------------------------
# File Name: get_func.py (Lite Version)
# Description: Core extraction logic for the Lite version.
# ---------------------------------------------------

import asyncio
import time
import os
import re
import unicodedata
import random
import pymongo
import shutil
import subprocess
import gc
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, RPCError
from pyrogram.enums import MessageMediaType, ParseMode
from telethon import TelegramClient
from devgagantools import fast_upload
from config import MONGO_DB, LOG_GROUP, OWNER_ID, STRING, API_ID, API_HASH
from devgagan import app
from devgagan.core.func import *

# Constants
THUMBNAIL_DIR = "./thumbnails"
os.makedirs(THUMBNAIL_DIR, exist_ok=True)
VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm', 'mpg', 'mpeg', '3gp', 'ts', 'm4v', 'f4v', 'vob'}

# Database Setup
mongo_client = pymongo.MongoClient(MONGO_DB)
db = mongo_client["smart_users"]
collection = db["super_user"]

# Premium Session Client (Optional)
if STRING:
    from devgagan import pro
else:
    pro = None

def clean_filename(text):
    if not text: return "file"
    text = unicodedata.normalize("NFKC", text)
    text = ''.join(c for c in text if not unicodedata.category(c).startswith(('S', 'C', 'P')) or c in ['.', '-', '_'])
    return re.sub(r'[_\s\-]+', ' ', text).strip()

def thumbnail(sender):
    path = os.path.join(THUMBNAIL_DIR, f"{sender}.jpg")
    return path if os.path.exists(path) else None

async def fetch_upload_method(user_id):
    user_data = collection.find_one({"user_id": user_id})
    return user_data.get("upload_method", "Pyrogram") if user_data else "Pyrogram"

async def upload_media(sender, target_chat_id, file, caption, edit, topic_id):
    try:
        method = await fetch_upload_method(sender)
        metadata = video_metadata(file)
        thumb_path = thumbnail(sender)
        
        # Determine file type
        ext = file.split('.')[-1].lower()
        if method == "Pyrogram":
            if ext in {'mp4', 'mkv', 'mov', 'avi'}:
                await app.send_video(
                    chat_id=target_chat_id,
                    video=file,
                    caption=caption,
                    thumb=thumb_path,
                    duration=metadata.get('duration', 0),
                    width=metadata.get('width', 0),
                    height=metadata.get('height', 0),
                    reply_to_message_id=topic_id,
                    progress=progress_bar,
                    progress_args=("⚡️ Uploading...", edit, time.time())
                )
            else:
                await app.send_document(
                    chat_id=target_chat_id,
                    document=file,
                    caption=caption,
                    thumb=thumb_path,
                    reply_to_message_id=topic_id,
                    progress=progress_bar,
                    progress_args=("⚡️ Uploading...", edit, time.time())
                )
        elif method == "Telethon":
            # Lite version Telethon simplified
            from devgagan import sex as gf
            await fast_upload(gf, file, reply=edit, name=os.path.basename(file))
            # ... additional telethon logic omitted for brevity in Lite version ...
            
    except Exception as e:
        await app.send_message(LOG_GROUP, f"❌ Upload Failed: {e}")
    finally:
        if file and os.path.exists(file): os.remove(file)
        gc.collect()

async def get_msg(userbot, sender, edit_id, msg_link, i=0, message=None):
    try:
        msg_link = msg_link.split("?")[0].rstrip("/")
        if 't.me/c/' in msg_link:
            parts = msg_link.split("/")
            chat = int('-100' + parts[parts.index('c') + 1])
            msg_id = int(parts[-1]) + i
        else:
            # Public link
            chat = msg_link.split("t.me/")[1].split("/")[0]
            msg_id = int(msg_link.split("/")[-1])
            edit = await app.edit_message_text(sender, edit_id, "Processing Public Link...")
            await copy_message_with_chat_id(app, userbot, sender, chat, msg_id, edit)
            return

        msg = await userbot.get_messages(chat, msg_id)
        if not msg or msg.empty: return

        edit = await app.edit_message_text(sender, edit_id, "📥 Downloading...")
        file = await userbot.download_media(msg, progress=progress_bar, progress_args=("📥 Downloading...", edit, time.time()))
        
        caption = await get_final_caption(msg, sender)
        await upload_media(sender, message.chat.id, file, caption, edit, None)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if edit: await edit.delete()

async def copy_message_with_chat_id(app, userbot, sender, chat_id, message_id, edit):
    try:
        await app.copy_message(sender, chat_id, message_id)
    except Exception:
        # If copy fails, try download/upload
        msg = await userbot.get_messages(chat_id, message_id)
        file = await userbot.download_media(msg)
        await upload_media(sender, sender, file, msg.caption, edit, None)

async def get_final_caption(msg, sender):
    return msg.caption or ""

# Additional helpers (Simplified)
async def get_media_filename(msg): return "file"
def get_message_file_size(msg): return 0
