# ---------------------------------------------------
# File Name: start.py (Lite Version)
# Description: Helper commands for the Lite version.
# ---------------------------------------------------

from pyrogram import filters
from devgagan import app
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

HELP_TEXT = """
**🚀 Lite Content Saver Bot**

Commands:
/start - Check if bot is alive
/batch - Bulk extraction (Max 5000)
/login - Private content login
/logout - Clear session
/cancel - Stop ongoing batch
/settings - Manage your settings (Thumbnail, Caption, rename)
"""

@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    await message.reply_text(
        f"Hi {message.from_user.first_name}!\nI am a Lite version of Content Saver Bot. Fast and Clean.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help ❓", callback_data="help")]])
    )

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(_, message):
    await message.reply_text(HELP_TEXT)

@app.on_callback_query(filters.regex("help"))
async def help_cb(_, query):
    await query.message.edit_text(HELP_TEXT)

# Simplified Settings (Placeholder - full implementation requires copying existing settings logic)
@app.on_message(filters.command("settings") & filters.private)
async def settings(_, message):
    await message.reply_text("Settings are available. Use original bot logic for detailed configuration.")
