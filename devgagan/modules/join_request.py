# ---------------------------------------------------
# File Name: join_request.py
# Description: Automatically approves pending join requests based on 
#              auth/updates channel membership, and sends welcoming rich messages.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# Created: 2026-07-05
# License: MIT License
# ---------------------------------------------------

import random
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import PeerIdInvalid, UserNotMutualContact
from devgagan import app
from config import OWNER_ID
from devgagan.core.mongo.db import set_auth_channel, get_auth_channel, set_log_channel, get_log_channel

logger = logging.getLogger(__name__)


async def send_rich_approval_message(client: Client, user_id: int, chat, invite_link: str, full_name: str):
    stickers = [
        "CAACAgUAAxkBAAEB8BlosDGCxtVBNBGV3vK2CKmR87rstQACwxoAAit2eVeMbZ7zpZHiGB4E",
        "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
        "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
    ]
    bot_info = await client.get_me()
    
    approve_text = (
        f"<b>🔓 Access Granted! Welcome to {chat.title}! 🎉</b>\n\n"
        f"<blockquote><b>Cheers, <a href='https://t.me/{bot_info.username}'>{full_name}</a>! 🥂</b></blockquote>\n\n"
        f"Your request to join the channel <b><a href='{invite_link}'>{chat.title}</a></b> has been <b>approved</b> successfully! ✅\n\n"
        f"⚠️ <b><u>CRITICAL WARNING</u></b> ⚠️\n"
        f"<i>Do NOT leave our main Updates Channel! If you leave, our system will automatically revoke your access and remove you from <b>ALL</b> channels and groups linked to this bot. Keep your membership active to maintain lifetime access!</i> 💀\n\n"
        f"<i>⚡ Need to save restricted content, download videos, or bypass copy restrictions? Tap 'Start Bot' below to begin!</i> 👇"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔮 Enter Channel 🔗", url=invite_link),
            InlineKeyboardButton("🚀 Start Bot 🤖", url=f"https://t.me/{bot_info.username}?start=True")
        ]
    ])
    
    try:
        await client.send_message(user_id, approve_text, disable_web_page_preview=True, reply_markup=keyboard)
        await client.send_sticker(user_id, random.choice(stickers))
    except Exception as e:
        logger.warning(f"Could not DM approved user {user_id}: {e}")

    # Read log channel dynamically from DB
    log_channel_id = await get_log_channel()
    if log_channel_id:
        try:
            await client.send_message(log_channel_id, approve_text, disable_web_page_preview=True)
            await client.send_sticker(log_channel_id, random.choice(stickers))
        except Exception as e:
            logger.warning(f"Could not send log to channel {log_channel_id}: {e}")


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
        if target.startswith("-100") or (target.startswith("-") and target[1:].isdigit()) or target.isdigit():
            chat_id = int(target)
        else:
            chat_id = target
            
        chat = await client.get_chat(chat_id)
        await set_auth_channel(chat.id)
        
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


@app.on_message(filters.command("setlog") & filters.user(OWNER_ID) & filters.private)
async def handle_set_log(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply(
            "❌ **Usage:** `/setlog <channel_id_or_username>`\n\n"
            "Example:\n"
            "- `/setlog -100123456789`\n"
            "- `/setlog @my_log_channel`\n"
            "- `/setlog none` (to disable logs)"
        )
        return
        
    target = message.command[1]
    if target.lower() == "none":
        await set_log_channel(None)
        await message.reply("✅ **Approval Log Channel has been disabled!**")
        return
        
    try:
        if target.startswith("-100") or (target.startswith("-") and target[1:].isdigit()) or target.isdigit():
            chat_id = int(target)
        else:
            chat_id = target
            
        chat = await client.get_chat(chat_id)
        await set_log_channel(chat.id)
        
        invite_link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else None)
        if not invite_link:
            try:
                invite_link = (await client.create_chat_invite_link(chat.id)).invite_link
            except Exception:
                pass
                
        reply_msg = f"✅ **Approval Log Channel updated successfully!**\n\n📌 **Title:** {chat.title}\n🆔 **ID:** `{chat.id}`"
        if invite_link:
            reply_msg += f"\n🔗 **Link:** {invite_link}"
            
        await message.reply(reply_msg)
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}\n\nMake sure the bot is an administrator in the channel so it can post logs!")


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
        is_member = member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
            ChatMemberStatus.RESTRICTED
        ]
    except Exception:
        is_member = False
        
    if is_member:
        try:
            chat = await client.get_chat(target_chat_id)
            invite_link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else "https://t.me")
            full_name = f"{callback_query.from_user.first_name or ''} {callback_query.from_user.last_name or ''}".strip()
            
            await client.approve_chat_join_request(chat_id=target_chat_id, user_id=user_id)
            await callback_query.answer("✅ Verification successful! Your request has been approved.", show_alert=True)
            await callback_query.message.edit_text("🎉 **Approved! Welcome to the channel!**")
            
            # Send rich welcome message
            await send_rich_approval_message(client, user_id, chat, invite_link, full_name)
        except Exception as e:
            await callback_query.answer(f"❌ Failed to approve: {str(e)}", show_alert=True)
    else:
        await callback_query.answer("❌ You haven't joined the updates channel yet! Please join and try again.", show_alert=True)


@app.on_chat_join_request()
async def join_request_handler(client: Client, m: ChatJoinRequest):
    try:
        chat = await client.get_chat(m.chat.id)
        auth_channel_id = await get_auth_channel()
        
        is_member = False
        invite_link = None
        
        if auth_channel_id:
            try:
                member = await client.get_chat_member(chat_id=auth_channel_id, user_id=m.from_user.id)
                is_member = member.status in [
                    ChatMemberStatus.MEMBER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                    ChatMemberStatus.RESTRICTED
                ]
            except Exception:
                is_member = False
                
            if not is_member:
                try:
                    auth_chat = await client.get_chat(auth_channel_id)
                    invite_link = auth_chat.invite_link or (f"https://t.me/{auth_chat.username}" if auth_chat.username else None)
                    if not invite_link:
                        try:
                            invite_link = (await client.create_chat_invite_link(auth_channel_id)).invite_link
                        except Exception:
                            invite_link = "https://t.me"
                except Exception:
                    invite_link = "https://t.me"
        else:
            # If no auth channel is set, treat them as a member to show direct "Approve Me" button
            is_member = True

        # ALWAYS send a message first in DM
        try:
            if is_member:
                # User has joined auth channel (or no auth channel set)
                welcome_text = (
                    f"✨ **Hello {m.from_user.first_name}!** ✨\n\n"
                    f"Your request to join **{chat.title}** is currently **pending**... ⏳\n\n"
                    f"👇 Please click the button below to verify and approve your request instantly!"
                )
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🟢 Approve Me! ⚡", callback_data=f"join_app:{chat.id}")]
                ])
            else:
                # User has NOT joined the updates channel
                welcome_text = (
                    f"✨ **Hello {m.from_user.first_name}!** ✨\n\n"
                    f"Your request to join **{chat.title}** is currently **pending**... ⏳\n\n"
                    f"📢 **Verification Required:**\n"
                    f"To gain access, you must first join our updates channel! This helps us keep you informed about important updates. 😉\n\n"
                    f"👇 Please click the button below to join, then tap **Verify & Approve** to unlock access instantly!"
                )
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔴 Join Updates Channel 📢", url=invite_link)],
                    [InlineKeyboardButton("🟢 Verify & Approve ⚡", callback_data=f"join_app:{chat.id}")]
                ])
                
            await client.send_message(
                chat_id=m.from_user.id,
                text=welcome_text,
                reply_markup=keyboard
            )
        except Exception as pm_error:
            logger.warning(f"Verification message could not be sent to {m.from_user.id}: {pm_error}")
            
    except Exception as e:
        logger.error(f"Join request handler error: {e}")
