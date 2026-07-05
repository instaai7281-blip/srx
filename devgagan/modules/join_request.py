# ---------------------------------------------------
# File Name: join_request.py
# Description: Automatically approves pending join requests in admin channels/groups 
#              and sends a welcoming message via the bot.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# Created: 2026-07-05
# License: MIT License
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from devgagan import app

@app.on_chat_join_request()
async def auto_approve_requests(client: Client, request: ChatJoinRequest):
    chat = request.chat  # Chat where request was received
    user = request.from_user  # User who sent the join request
    
    try:
        # Approve the join request
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        print(f"[SUCCESS] Approved join request for {user.id} in chat {chat.id}")
        
        # Prepare an elegant welcome message
        welcome_text = (
            f"✨ **Welcome to {chat.title}, {user.first_name}!** ✨\n\n"
            f"🎉 Your request to join the channel has been **automatically approved** successfully! ✅\n\n"
            f"🤖 *Need to save restricted content, download videos, or bypass copy restrictions?* I can help you with that! Feel free to start me. 😉\n\n"
            f"⚡ **Powered by CHOSEN ONE ⚝**"
        )
        
        # Inline button to start the bot
        bot_info = await client.get_me()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Start Me", url=f"https://t.me/{bot_info.username}?start=True")]
        ])
        
        # Attempt to send welcome message in private chat
        try:
            await client.send_message(
                chat_id=user.id,
                text=welcome_text,
                reply_markup=keyboard
            )
        except Exception as pm_error:
            print(f"[INFO] Welcome message could not be sent to {user.id} (probably hasn't started bot): {pm_error}")
            
    except Exception as e:
        print(f"[ERROR] Failed to approve join request: {e}")
