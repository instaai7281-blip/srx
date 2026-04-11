# ---------------------------------------------------
# File Name: settings.py
# Description: Settings module for the bot to manage user preferences.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------

import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from devgagan import app
from devgagan.core.mongo import db

def get_settings_keyboard(user_data):
    filters_data = user_data.get("filters", {})
    
    # helper for toggle text
    def toggle_text(key):
        return "✅ ON" if filters_data.get(key, True) else "❌ OFF"

    buttons = [
        [
            InlineKeyboardButton("🎬 Video", callback_data="toggle_video"),
            InlineKeyboardButton(toggle_text("video"), callback_data="toggle_video")
        ],
        [
            InlineKeyboardButton("📁 Document", callback_data="toggle_document"),
            InlineKeyboardButton(toggle_text("document"), callback_data="toggle_document")
        ],
        [
            InlineKeyboardButton("🎵 Audio", callback_data="toggle_audio"),
            InlineKeyboardButton(toggle_text("audio"), callback_data="toggle_audio")
        ],
        [
            InlineKeyboardButton("🖼️ Photo", callback_data="toggle_photo"),
            InlineKeyboardButton(toggle_text("photo"), callback_data="toggle_photo")
        ],
        [
            InlineKeyboardButton("📝 Text", callback_data="toggle_text"),
            InlineKeyboardButton(toggle_text("text"), callback_data="toggle_text")
        ],
        [
            InlineKeyboardButton("🔄 Reset to Default", callback_data="reset_filters")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

@app.on_message(filters.command("settings"))
async def settings_command(client, message):
    user_id = message.from_user.id
    user_data = await db.get_data(user_id) or {}
    
    await message.reply_text(
        "⚙️ **Bot Settings**\n\nToggle which media types you want the bot to extract during batch or single processes:",
        reply_markup=get_settings_keyboard(user_data)
    )

@app.on_callback_query(filters.regex(r"^toggle_(video|document|audio|photo|text)$"))
async def toggle_filter(client, callback_query: CallbackQuery):
    media_type = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    
    user_data = await db.get_data(user_id) or {}
    filters_data = user_data.get("filters", {})
    current_status = filters_data.get(media_type, True)
    
    new_status = not current_status
    await db.set_filter(user_id, media_type, new_status)
    
    # Reload data for UI
    updated_data = await db.get_data(user_id) or {}
    await callback_query.message.edit_reply_markup(reply_markup=get_settings_keyboard(updated_data))
    await callback_query.answer(f"{media_type.capitalize()} turned {'ON' if new_status else 'OFF'}")

@app.on_callback_query(filters.regex("reset_filters"))
async def reset_filters(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    for media_type in ["video", "document", "audio", "photo", "text"]:
        await db.set_filter(user_id, media_type, True)
    
    updated_data = await db.get_data(user_id) or {}
    await callback_query.message.edit_reply_markup(reply_markup=get_settings_keyboard(updated_data))
    await callback_query.answer("All filters reset to ON")
