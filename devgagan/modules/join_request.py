# ---------------------------------------------------
# File Name: join_request.py
# Description: Automatically approves pending join requests based on 
#              multiple auth/updates channel membership, and sends welcoming rich messages.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# Created: 2026-07-05
# License: MIT License
# ---------------------------------------------------

import random
import logging
import asyncio
from pyrogram import Client, filters, ContinuePropagation
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import PeerIdInvalid, UserNotMutualContact
from devgagan import app
from config import OWNER_ID
from devgagan.core.mongo.db import (
    add_auth_channel,
    remove_auth_channel,
    get_auth_channels,
    clear_auth_channels,
    set_log_channel,
    get_log_channel
)

logger = logging.getLogger(__name__)

# State dict to track adding channel action
ADD_AUTH_STATE = {}  # user_id -> action_name


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
        f"<i>If you leave Updates Channel! our system will automatically remove u from <b>ALL</b> channels and groups.\n"
        f"Keep your membership active to maintain lifetime access!</i> 💀\n\n"
        f"<i>⚡ Need to save restricted content, download videos, or bypass copy restrictions? Tap 'Start Bot' below to begin!</i> 👇"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔮 Enter Channel 🔗", url=invite_link),
            InlineKeyboardButton("🚀 Start Bot 🤖", url=f"https://t.me/{bot_info.username}?start=True")
        ]
    ])
    
    try:
        await client.send_message(
            chat_id=user_id,
            text=approve_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.warning(f"Could not DM approved user {user_id}: {e}")

    # Read log channel dynamically from DB
    log_channel_id = await get_log_channel()
    if log_channel_id:
        try:
            await client.send_message(
                chat_id=log_channel_id,
                text=approve_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.warning(f"Could not send log to channel {log_channel_id}: {e}")


async def build_auth_menu_keyboard(client: Client):
    channels = await get_auth_channels()
    buttons = []
    
    # Row 1: Add Channel | Remove Channel
    buttons.append([
        InlineKeyboardButton("➕ Add Channel", callback_data="auth_add_prompt"),
        InlineKeyboardButton("❌ Remove Channel", callback_data="auth_remove_list")
    ])
    
    # Row 2: Clear All | Close
    buttons.append([
        InlineKeyboardButton("🚫 Disable All", callback_data="auth_clear_all"),
        InlineKeyboardButton("🔄 Close", callback_data="auth_close")
    ])
    
    return InlineKeyboardMarkup(buttons)


async def get_auth_menu_text(client: Client):
    channels = await get_auth_channels()
    if not channels:
        return (
            "🛡️ **Forcesub / Updates Channels Settings** 🛡️\n\n"
            "❌ **No auth channels configured!**\n"
            "Users will be approved immediately without any verification check."
        )
        
    text = "🛡️ **Forcesub / Updates Channels Settings** 🛡️\n\n"
    text += "Here are the channels users must join to get approved:\n"
    
    for idx, chat_id in enumerate(channels, 1):
        try:
            chat = await client.get_chat(chat_id)
            title = chat.title
            username = f" (@{chat.username})" if chat.username else ""
        except Exception:
            title = "Unknown Channel"
            username = ""
        text += f"{idx}. **{title}**{username}\n🆔 `{chat_id}`\n\n"
        
    text += "💡 *Users will be checked against all channels above.*"
    return text


@app.on_message(filters.command("setauth") & filters.user(OWNER_ID) & filters.private)
async def handle_set_auth(client: Client, message: Message):
    text = await get_auth_menu_text(client)
    keyboard = await build_auth_menu_keyboard(client)
    await message.reply(text, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"^auth_(.+)"))
async def handle_auth_callbacks(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id != OWNER_ID:
        await callback_query.answer("⚠️ Only the bot owner can access this!", show_alert=True)
        return
        
    data = callback_query.data.split("_")[1]
    
    if data == "menu":
        ADD_AUTH_STATE.pop(user_id, None)
        text = await get_auth_menu_text(client)
        keyboard = await build_auth_menu_keyboard(client)
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
        
    elif data == "add_prompt":
        ADD_AUTH_STATE[user_id] = "awaiting_channel"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="auth_menu")]
        ])
        await callback_query.message.edit_text(
            "📝 **Awaiting Input...**\n\n"
            "Please send the channel username (e.g. `@team_spy_pro`) or ID (e.g. `-100123456789`) in this chat.\n\n"
            "⚠️ *Make sure the bot is an Administrator in that channel!*",
            reply_markup=keyboard
        )
        await callback_query.answer()
        
    elif data == "remove_list":
        channels = await get_auth_channels()
        if not channels:
            await callback_query.answer("❌ No channels to remove!", show_alert=True)
            return
            
        buttons = []
        for chat_id in channels:
            try:
                chat = await client.get_chat(chat_id)
                title = chat.title
            except Exception:
                title = f"ID: {chat_id}"
            buttons.append([InlineKeyboardButton(f"🗑️ Delete {title}", callback_data=f"auth_delete:{chat_id}")])
            
        buttons.append([InlineKeyboardButton("🔙 Back to Settings", callback_data="auth_menu")])
        
        await callback_query.message.edit_text(
            "🗑️ **Select a channel to remove from forcesub list:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback_query.answer()
        
    elif data.startswith("delete:"):
        target_id = int(data.split(":")[1])
        await remove_auth_channel(target_id)
        
        # Go back to remove list or menu
        channels = await get_auth_channels()
        if channels:
            await callback_query.answer("🗑️ Channel removed!", show_alert=True)
            # Rebuild list
            buttons = []
            for chat_id in channels:
                try:
                    chat = await client.get_chat(chat_id)
                    title = chat.title
                except Exception:
                    title = f"ID: {chat_id}"
                buttons.append([InlineKeyboardButton(f"🗑️ Delete {title}", callback_data=f"auth_delete:{chat_id}")])
            buttons.append([InlineKeyboardButton("🔙 Back to Settings", callback_data="auth_menu")])
            await callback_query.message.edit_text(
                "🗑️ **Select a channel to remove from forcesub list:**",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await callback_query.answer("🗑️ Channel removed! Forcesub disabled.", show_alert=True)
            text = await get_auth_menu_text(client)
            keyboard = await build_auth_menu_keyboard(client)
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            
    elif data == "clear_all":
        await clear_auth_channels()
        await callback_query.answer("🗑️ All channels removed. Forcesub disabled!", show_alert=True)
        text = await get_auth_menu_text(client)
        keyboard = await build_auth_menu_keyboard(client)
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        
    elif data == "close":
        ADD_AUTH_STATE.pop(user_id, None)
        await callback_query.message.delete()
        await callback_query.answer()


@app.on_message(filters.private & filters.user(OWNER_ID))
async def handle_owner_input(client: Client, message: Message):
    user_id = message.from_user.id
    if ADD_AUTH_STATE.get(user_id) == "awaiting_channel":
        if message.text and message.text.startswith('/'):
            ADD_AUTH_STATE.pop(user_id, None)
            raise ContinuePropagation
            
        target = message.text.strip()
        ADD_AUTH_STATE.pop(user_id, None)
        
        try:
            if target.startswith("-100") or (target.startswith("-") and target[1:].isdigit()) or target.isdigit():
                chat_id = int(target)
            else:
                chat_id = target
                
            chat = await client.get_chat(chat_id)
            await add_auth_channel(chat.id)
            
            await message.reply(
                f"✅ **Channel Added Successfully!**\n\n"
                f"📌 **Title:** {chat.title}\n"
                f"🆔 **ID:** `{chat.id}`\n\n"
                f"Use `/setauth` to manage all channels."
            )
        except Exception as e:
            await message.reply(f"❌ **Failed to add channel:** {str(e)}\n\nMake sure the bot is added as an administrator in the channel!")
    else:
        raise ContinuePropagation


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
    
    auth_channels = await get_auth_channels()
    if not auth_channels:
        try:
            await client.approve_chat_join_request(chat_id=target_chat_id, user_id=user_id)
            await callback_query.answer("✅ Approved successfully!", show_alert=True)
            await callback_query.message.edit_text(
                text="🎉 <b>Approved! Welcome to the channel!</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)
        return
        
    # Check all configured auth channels
    missing_channels = []
    for auth_channel_id in auth_channels:
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
            
        if not is_member:
            missing_channels.append(auth_channel_id)
            
    if not missing_channels:
        try:
            chat = await client.get_chat(target_chat_id)
            invite_link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else "https://t.me")
            full_name = f"{callback_query.from_user.first_name or ''} {callback_query.from_user.last_name or ''}".strip()
            
            await client.approve_chat_join_request(chat_id=target_chat_id, user_id=user_id)
            await callback_query.answer("✅ Verification successful! Your request has been approved.", show_alert=True)
            await callback_query.message.edit_text(
                text="🎉 <b>Approved! Welcome to the channel!</b>",
                parse_mode=ParseMode.HTML
            )
            
            # Send rich welcome message
            await send_rich_approval_message(client, user_id, chat, invite_link, full_name)
        except Exception as e:
            await callback_query.answer(f"❌ Failed to approve: {str(e)}", show_alert=True)
    else:
        await callback_query.answer("❌ You haven't joined all updates channels yet! Please check the buttons and try again.", show_alert=True)


@app.on_chat_join_request()
async def join_request_handler(client: Client, m: ChatJoinRequest):
    try:
        chat = await client.get_chat(m.chat.id)
        auth_channels = await get_auth_channels()
        
        missing_channels = []
        
        if auth_channels:
            for auth_channel_id in auth_channels:
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
                    missing_channels.append(auth_channel_id)

        # ALWAYS send a message first in DM
        try:
            if not missing_channels:
                # User has joined all auth channels (or no auth channels set)
                welcome_text = (
                    f"✨ <b>Hello {m.from_user.first_name}!</b> ✨\n\n"
                    f"Your request to join <b>{chat.title}</b> is currently <b>pending</b>... ⏳\n\n"
                    f"👇 Please click the button below to verify and approve your request instantly!"
                )
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🟢 Approve Me! ⚡", callback_data=f"join_app:{chat.id}")]
                ])
            else:
                # User has NOT joined some/all updates channels
                welcome_text = (
                    f"✨ <b>Hello {m.from_user.first_name}!</b> ✨\n\n"
                    f"Your request to join <b>{chat.title}</b> is currently <b>pending</b>... ⏳\n\n"
                    f"📢 <b><u>Verification Required</u>:</b>\n"
                    f"To gain access, you must first join our updates channels! This helps us keep you informed about important updates. 😉\n\n"
                    f"👇 Please click the buttons below to join, then tap <b>Verify & Approve</b> to unlock access instantly!"
                )
                
                # Build join buttons dynamically for missing channels
                buttons = []
                for idx, auth_channel_id in enumerate(missing_channels, 1):
                    try:
                        auth_chat = await client.get_chat(auth_channel_id)
                        title = auth_chat.title
                        invite_link = auth_chat.invite_link or (f"https://t.me/{auth_chat.username}" if auth_chat.username else None)
                        if not invite_link:
                            try:
                                invite_link = (await client.create_chat_invite_link(auth_channel_id)).invite_link
                            except Exception:
                                invite_link = "https://t.me"
                    except Exception:
                        title = f"Updates Channel {idx}"
                        invite_link = "https://t.me"
                        
                    buttons.append([InlineKeyboardButton(f"📢 Join {title}", url=invite_link)])
                    
                buttons.append([InlineKeyboardButton("🟢 Verify & Approve ⚡", callback_data=f"join_app:{chat.id}")])
                keyboard = InlineKeyboardMarkup(buttons)
                
            await client.send_message(
                chat_id=m.from_user.id,
                text=welcome_text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        except Exception as pm_error:
            logger.warning(f"Verification message could not be sent to {m.from_user.id}: {pm_error}")
            
    except Exception as e:
        logger.error(f"Join request handler error: {e}")
