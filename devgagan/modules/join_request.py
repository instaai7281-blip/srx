# ---------------------------------------------------
# File Name: join_request.py
# Description: Automatically approves pending join requests based on bio-tags 
#              or auth channel membership, and sends welcoming rich messages.
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
from config import OWNER_ID, NEW_REQ_MODE, BIO_CHANNEL
from devgagan.core.mongo.db import set_auth_channel, get_auth_channel

logger = logging.getLogger(__name__)

# TAG MAP with multiple tags for bio checks
TAG_MAP = {
    "#movie": ["@real_pirates", "@drama_loverx"],
    "#drama": ["@drama_loverx"],
    "#study": ["@II_LevelUP_II"],
    "#success": ["@ii_way_to_success_ii"],
    "#skill": ["@II_LevelUP_II"],
    "#alone": ["@just_vibing_alone"],
}

def get_required_tags_from_description(description: str):
    description = description.lower()
    required_tags = []
    for hashtag, tags in TAG_MAP.items():
        if hashtag in description:
            required_tags.extend(tags)
    return list(dict.fromkeys(required_tags))

def has_required_tag_in_bio(user_bio: str, required_tags: list):
    if not user_bio or not required_tags:
        return False
    user_bio = user_bio.lower()
    return any(tag.lower() in user_bio for tag in required_tags)


async def send_rich_approval_message(client: Client, user_id: int, chat, invite_link: str, full_name: str):
    stickers = [
        "CAACAgUAAxkBAAEB8BlosDGCxtVBNBGV3vK2CKmR87rstQACwxoAAit2eVeMbZ7zpZHiGB4E",
        "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
        "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
    ]
    member_count = getattr(chat, 'members_count', 0) or 0
    
    approve_text = (
        f"🔓 <b>Access Granted ✅</b>\n\n"
        f"<b><blockquote> Cheers, <a href='https://t.me/II_LevelUP_II'>{full_name}</a> ! 🥂</blockquote></b>\n"
        f"Your Request To Join <b><a href='{invite_link}'> {chat.title} </a></b> Has Been Approved! 🎉\n"
        f"We’re happy to have you with us. 🥰\n\n"
        f"💎 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 𝐂𝐨𝐮𝐧𝐭: <b>{member_count:,}</b> 🚀\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
    )
    
    bot_info = await client.get_me()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Start Me", url=f"https://t.me/{bot_info.username}?start=True")]
    ])
    
    try:
        await client.send_message(user_id, approve_text, disable_web_page_preview=True, reply_markup=keyboard)
        await client.send_sticker(user_id, random.choice(stickers))
    except Exception as e:
        logger.warning(f"Could not DM approved user {user_id}: {e}")

    if BIO_CHANNEL:
        try:
            await client.send_message(BIO_CHANNEL, approve_text, disable_web_page_preview=True)
            await client.send_sticker(BIO_CHANNEL, random.choice(stickers))
        except Exception as e:
            logger.warning(f"Could not send to log group: {e}")


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
    if not NEW_REQ_MODE:
        return

    stickers = [
        "CAACAgUAAxkBAAEB8BlosDGCxtVBNBGV3vK2CKmR87rstQACwxoAAit2eVeMbZ7zpZHiGB4E",
        "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
        "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
    ]

    try:
        chat = await client.get_chat(m.chat.id)
        description = chat.description or ""
        required_tags = get_required_tags_from_description(description)

        # ----------------------------------------------------
        # FEATURE 1: BIO-TAG VERIFICATION CHECK (IF TAGS FOUND)
        # ----------------------------------------------------
        if required_tags:
            try:
                user = await client.get_chat(m.from_user.id)
                bio = user.bio or ""
            except Exception as e:
                logger.warning(f"Could not fetch user bio for {m.from_user.id}: {e}")
                bio = ""

            # Try to get invite link or generate one
            invite_link = chat.invite_link
            if not invite_link:
                try:
                    invite_link_obj = await client.create_chat_invite_link(
                        chat_id=m.chat.id,
                        name=f"Join {chat.title}",
                        creates_join_request=True
                    )
                    invite_link = invite_link_obj.invite_link
                except Exception:
                    invite_link = "https://t.me"

            full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()

            if has_required_tag_in_bio(bio, required_tags):
                # Approve join request
                await client.approve_chat_join_request(m.chat.id, m.from_user.id)
                
                # Send rich welcome message
                await send_rich_approval_message(client, m.from_user.id, chat, invite_link, full_name)

                # Send warning about tag removal
                warning_text = (
                    f"⚠️⚠️⚠️\n"
                    f"<b><i>"
                    f"||If you remove the tag(s) `{', '.join(required_tags)}` from your bio, you will be removed from the channel. 💀||\n\n"
                    f"These tags are required to remain a verified member of > ≫  {chat.title}.\n"
                    f"Make sure to keep that tag in your Bio to avoid removal. 😉"
                    f"</i></b>"
                )

                try:
                    await client.send_message(m.from_user.id, warning_text, disable_web_page_preview=True)
                except Exception as e:
                    logger.warning(f"Could not send bio warning: {e}")
            else:
                # User doesn't have the tag in bio -> instruct them
                tags_display = '\n'.join([f"<blockquote>● <code>{tag}</code> ♡</blockquote>" for tag in required_tags])

                reject_text = (
                    f"🔒 <b>Access Denied ❌</b>\n\n"
                    f"Dear <b>{m.from_user.mention}</b> 🌝 Your Request is Pending...\n\n" 
                    f"if you want To join ⇙ Quickly"
                    f"<blockquote><b><a href='{invite_link}'>{chat.title}</a></b></blockquote>"
                    f"follow these <b>2 Simple Steps 😊</b>:\n"
                    f"──────────────────\n"
                    f" 💡 <b><u>Step</u> 1️⃣</b>\n\n"
                    f"Add This 👇 Tag in <b>Your Bio</b>\n"           
                    f"{tags_display}\n"
                    f"<i>Tap to Copy 👆</i>\n\n"
                    f"𝐀𝐝𝐝 𝐐𝐮𝐢𝐜𝐤𝐥𝐲 𝐢𝐧 <b><a href='tg://settings'>Your Bio 👀</a></b>\n\n"                
                    f" 💡 <b><u>Step</u> 2️⃣</b>\n\n"
                    f"After updating your bio, try joining again by this Link 🔗 👇 \n<blockquote><b>{invite_link}</b></blockquote>\n"
                    f"──────────────────\n"
                    f"✨ I’ll Approve you instantly if i detect the tag. Let's go! 😉"
                )
                buttons = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("📢 Updates", url="https://t.me/II_Way_to_Success_II"),
                        InlineKeyboardButton("💬 Support", url="https://t.me/GeniusJunctionX")
                    ]
                ])

                try:
                    await client.send_message(m.from_user.id, reject_text, disable_web_page_preview=True, reply_markup=buttons)
                    await client.send_sticker(m.from_user.id, random.choice(stickers))
                except (UserNotMutualContact, PeerIdInvalid):
                    pass
                except Exception as e:
                    logger.warning(f"Could not DM rejected user: {e}")
            return

        # ----------------------------------------------------
        # FEATURE 2: FALLBACK TO AUTH CHANNEL MEMBERSHIP CHECK
        # ----------------------------------------------------
        auth_channel_id = await get_auth_channel()
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
                            
                    welcome_text = (
                        f"👋 **Hello {m.from_user.first_name}!**\n\n"
                        f"To join the channel **{chat.title}**, you must first join our updates channel! 📢\n\n"
                        f"Please click the button below to join, then click the **Verify & Approve** button to complete! 👇"
                    )
                    
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("📢 Join Updates Channel", url=invite_link)],
                        [InlineKeyboardButton("🔄 Verify & Approve", callback_data=f"join_app:{chat.id}")]
                    ])
                    
                    await client.send_message(
                        chat_id=m.from_user.id,
                        text=welcome_text,
                        reply_markup=keyboard
                    )
                except Exception as pm_error:
                    logger.warning(f"Verification message could not be sent to {m.from_user.id}: {pm_error}")
                return

        # Approve and welcome for standard join request
        await client.approve_chat_join_request(chat.id, m.from_user.id)
        
        invite_link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else "https://t.me")
        full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()
        
        await send_rich_approval_message(client, m.from_user.id, chat, invite_link, full_name)

    except Exception as e:
        logger.error(f"Join request handler error: {e}")
