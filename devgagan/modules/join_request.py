# ---------------------------------------------------
# File Name: join_request.py
# Description: Automatically approves pending join requests in admin channels/groups 
#              if they have joined the specified auth channel, and sends welcoming messages.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# Created: 2026-07-05
# License: MIT License
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message
from devgagan import app
from config import OWNER_ID
from devgagan.core.mongo.db import set_auth_channel, get_auth_channel

@app.on_message(filters.command("setauth") & filters.user(OWNER_ID) & filters.private)
async def handle_set_auth(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply(
            "❌ **Usage:** `/setauth <channel_id_or_username>`\n\n"
            "Example:\n"
            "- `/setauth -100123456789`\n"
            "- `/setauth @team_spy_pro`\n"
            "- `/setauth none` (to disable auth check)"
        )
        return
        
    target = message.command[1]
    if target.lower() == "none":
        await set_auth_channel(None)
        await message.reply("✅ **Auth Channel check has been disabled!**")
        return
        
    try:
        # Resolve target to get Chat ID
        if target.startswith("-100") or (target.startswith("-") and target[1:].isdigit()) or target.isdigit():
            chat_id = int(target)
        else:
            chat_id = target
            
        chat = await client.get_chat(chat_id)
        # Store resolved integer ID
        await set_auth_channel(chat.id)
        
        # Try to get invite link or username
        invite_link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else None)
        if not invite_link:
            try:
                invite_link = (await client.create_chat_invite_link(chat.id)).invite_link
            except Exception:
                pass
                
        reply_msg = f"✅ **Auth Channel updated successfully!**\n\n📌 **Title:** {chat.title}\n🆔 **ID:** `{chat.id}`"
        if invite_link:
            reply_msg += f"\n🔗 **Link:** {invite_link}"
            
        await message.reply(reply_msg)
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}\n\nMake sure the bot is an administrator in the channel!")

@app.on_callback_query(filters.regex(r"^join_app:(.+)"))
async def handle_join_verification(client: Client, callback_query):
    user_id = callback_query.from_user.id
    target_chat_id = int(callback_query.data.split(":")[1])
    
    auth_channel_id = await get_auth_channel()
    if not auth_channel_id:
        try:
            await client.approve_chat_join_request(chat_id=target_chat_id, user_id=user_id)
            await callback_query.answer("✅ Approved successfully!", show_alert=True)
            await callback_query.message.edit_text("🎉 **Approved! Welcome to the channel!**")
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)
        return
        
    try:
        member = await client.get_chat_member(chat_id=auth_channel_id, user_id=user_id)
        is_member = member.status in ["member", "administrator", "creator", "restricted"]
    except Exception:
        is_member = False
        
    if is_member:
        try:
            await client.approve_chat_join_request(chat_id=target_chat_id, user_id=user_id)
            await callback_query.answer("✅ Verification successful! Your request has been approved.", show_alert=True)
            await callback_query.message.edit_text("🎉 **Approved! Welcome to the channel!**")
        except Exception as e:
            await callback_query.answer(f"❌ Failed to approve: {str(e)}", show_alert=True)
    else:
        await callback_query.answer("❌ You haven't joined the updates channel yet! Please join and try again.", show_alert=True)

@app.on_chat_join_request()
async def auto_approve_requests(client: Client, request: ChatJoinRequest):
    chat = request.chat  # Chat where request was received
    user = request.from_user  # User who sent the join request
    
    auth_channel_id = await get_auth_channel()
    
    if auth_channel_id:
        try:
            # Check user membership
            member = await client.get_chat_member(chat_id=auth_channel_id, user_id=user.id)
            is_member = member.status in ["member", "administrator", "creator", "restricted"]
        except Exception:
            is_member = False
            
        if not is_member:
            # User is not a member, tell them to join first
            try:
                auth_chat = await client.get_chat(auth_channel_id)
                invite_link = auth_chat.invite_link or (f"https://t.me/{auth_chat.username}" if auth_chat.username else None)
                if not invite_link:
                    try:
                        invite_link = (await client.create_chat_invite_link(auth_channel_id)).invite_link
                    except Exception:
                        invite_link = "https://t.me"
                        
                welcome_text = (
                    f"👋 **Hello {user.first_name}!**\n\n"
                    f"To join the channel **{chat.title}**, you must first join our updates channel! 📢\n\n"
                    f"Please click the button below to join, then click the **Verify & Approve** button to complete! 👇"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Join Updates Channel", url=invite_link)],
                    [InlineKeyboardButton("🔄 Verify & Approve", callback_data=f"join_app:{chat.id}")]
                ])
                
                await client.send_message(
                    chat_id=user.id,
                    text=welcome_text,
                    reply_markup=keyboard
                )
            except Exception as pm_error:
                print(f"[INFO] Verification message could not be sent to {user.id}: {pm_error}")
            return

    # If auth channel check passes or is not set, approve immediately
    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        print(f"[SUCCESS] Approved join request for {user.id} in chat {chat.id}")
        
        # Prepare welcome message
        welcome_text = (
            f"✨ **Welcome to {chat.title}, {user.first_name}!** ✨\n\n"
            f"🎉 Your request to join the channel has been **automatically approved** successfully! ✅\n\n"
            f"🤖 *Need to save restricted content, download videos, or bypass copy restrictions?* I can help you with that! Feel free to start me. 😉\n\n"
            f"⚡ **Powered by CHOSEN ONE ⚝**"
        )
        
        bot_info = await client.get_me()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Start Me", url=f"https://t.me/{bot_info.username}?start=True")]
        ])
        
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
