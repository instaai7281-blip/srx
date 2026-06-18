# ---------------------------------------------------
# File Name: plans.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------

from datetime import timedelta
import pytz
import datetime, time
from devgagan import app
import asyncio
from config import OWNER_ID
from devgagan.core.func import get_seconds
from devgagan.core.mongo import plans_db  
from pyrogram import filters 


# -*- coding: utf-8 -*-

@app.on_message(filters.command("rem") & filters.user(OWNER_ID))
async def remove_premium(client, message):
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ **Invalid user ID.** Please provide a numeric ID.")
            return

        user_mention = f"User (`{user_id}`)"
        try:
            user = await client.get_users(user_id)
            if user:
                user_mention = user.mention
        except Exception:
            pass

        data = await plans_db.check_premium(user_id)
        if data and data.get("_id"):
            await plans_db.remove_premium(user_id)
            await message.reply_text(
                f"🗑️ **PREMIUM ACCESS REVOKED**\n"
                f"╭───────────────────────────╮\n"
                f"  👤 **User:** {user_mention}\n"
                f"  ⚡ **ID:** `{user_id}`\n"
                f"  ❌ **Status:** Premium access terminated.\n"
                f"╰───────────────────────────╯"
            )
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        f"⚠️ **NOTICE: PREMIUM TERMINATED**\n"
                        f"╭───────────────────────────╮\n"
                        f"  Your premium subscription access \n"
                        f"  has been terminated/expired.\n"
                        f"╰───────────────────────────╯\n"
                        f"💬 Contact owner if you think this is a mistake."
                    )
                )
            except Exception:
                pass
        else:
            await message.reply_text("🤷 **Pointless.**\n\nThis user was never premium. Why bother?")
    else:
        await message.reply_text("💤 **Boring.**\n\nUsage: `/rem user_id`\n*(Try getting it right next time.)*")



@app.on_message(filters.command("myplan"))
async def myplan(client, message):
    user_id = message.from_user.id
    user = message.from_user.mention
    data = await plans_db.check_premium(user_id)  
    if data and data.get("expire_date"):
        expiry = data.get("expire_date")
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        expiry_str_in_ist = expiry_ist.strftime("%d-%m-%Y %I:%M:%S %p")            
        
        current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        time_left = expiry_ist - current_time
            
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
            
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        await message.reply_text(
            f"⚜️ **YOUR PREMIUM STATUS** ⚜️\n"
            f"╭───────────────────────────╮\n"
            f"  👤 **User:** {user}\n"
            f"  ⚡ **ID:** `{user_id}`\n"
            f"  ⏰ **Remaining:** {time_left_str}\n"
            f"  ⌛ **Expiry:** {expiry_str_in_ist} (IST)\n"
            f"╰───────────────────────────╯"
        )   
    else:
        await message.reply_text(f"ʜᴇʏ {user},\n\nʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴʏ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs")
        


@app.on_message(filters.command("check") & filters.user(OWNER_ID))
async def get_premium(client, message):
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ **Invalid user ID.** Please provide a numeric ID.")
            return

        user_mention = f"User (`{user_id}`)"
        try:
            user = await client.get_users(user_id)
            if user:
                user_mention = user.mention
        except Exception:
            pass

        data = await plans_db.check_premium(user_id)  
        if data and data.get("expire_date"):
            expiry = data.get("expire_date") 
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry_ist.strftime("%d-%m-%Y %I:%M:%S %p")            
            
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(
                f"⚜️ **PREMIUM USER DETAILS** ⚜️\n"
                f"╭───────────────────────────╮\n"
                f"  👤 **User:** {user_mention}\n"
                f"  ⚡ **ID:** `{user_id}`\n"
                f"  ⏰ **Remaining:** {time_left_str}\n"
                f"  ⌛ **Expiry:** {expiry_str_in_ist} (IST)\n"
                f"╰───────────────────────────╯"
            )
        else:
            await message.reply_text("ɴᴏ ᴀɴʏ ᴘʀᴇᴍɪᴜᴍ ᴅᴀᴛᴀ ᴏꜰ ᴛʜᴇ ᴡᴀꜱ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ !")
    else:
        await message.reply_text("ᴜꜱᴀɢᴇ : /check user_id")


@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def give_premium_cmd_handler(client, message):
    if len(message.command) == 4:
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y %I:%M:%S %p")
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ **Invalid user ID.** Please provide a numeric ID.")
            return

        user_mention = f"User (`{user_id}`)"
        user_name = "User"
        try:
            user = await client.get_users(user_id)
            if user:
                user_mention = user.mention
                user_name = user.mention
        except Exception:
            pass

        time_val = message.command[2]+" "+message.command[3]
        seconds = await get_seconds(time_val)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)  
            await plans_db.add_premium(user_id, expiry_time)  
            data = await plans_db.check_premium(user_id)
            expiry = data.get("expire_date")   
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M:%S %p")         
            await message.reply_text(
                f"🌟 **PREMIUM ACCESS ACTIVATED** 🌟\n"
                f"╭───────────────────────────╮\n"
                f"  👤 **User:** {user_mention}\n"
                f"  ⚡ **ID:** `{user_id}`\n"
                f"  ⏰ **Duration:** `{time_val}`\n"
                f"  📅 **Start:** {current_time} (IST)\n"
                f"  ⏳ **Expiry:** {expiry_str_in_ist} (IST)\n"
                f"╰───────────────────────────╯\n"
                f"✨ _Powered by CHOSEN ONE ⚝_", 
                disable_web_page_preview=True
            )
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        f"✨ **CONGRATULATIONS! PREMIUM ACTIVATED** ✨\n"
                        f"╭───────────────────────────╮\n"
                        f"  👋 Hey {user_name},\n"
                        f"  Thank you for purchasing premium!\n"
                        f"  Your account has been upgraded. Enjoy! 🎉\n\n"
                        f"  ⏰ **Duration:** `{time_val}`\n"
                        f"  📅 **Joined:** {current_time} (IST)\n"
                        f"  ⏳ **Expiry:** {expiry_str_in_ist} (IST)\n"
                        f"╰───────────────────────────╯\n"
                        f"🚀 _Enjoy the maximum speed & limit!_"
                    ), 
                    disable_web_page_preview=True              
                )
            except Exception:
                pass
                    
        else:
            await message.reply_text("Invalid time format. Please use '1 day for days', '1 hour for hours', or '1 min for minutes', or '1 month for months' or '1 year for year'")
    else:
        await message.reply_text("Usage : /add user_id time (e.g., '1 day for days', '1 hour for hours', or '1 min for minutes', or '1 month for months' or '1 year for year')")


@app.on_message(filters.command("transfer"))
async def transfer_premium(client, message):
    if len(message.command) == 2:
        new_user_id = int(message.command[1])  # The user ID to whom premium is transferred
        sender_user_id = message.from_user.id  # The current premium user issuing the command
        sender_user = await client.get_users(sender_user_id)
        new_user = await client.get_users(new_user_id)
        
        # Fetch sender's premium plan details
        data = await plans_db.check_premium(sender_user_id)
        
        if data and data.get("_id"):  # Verify sender is already a premium user
            expiry = data.get("expire_date")  
            
            # Remove premium for the sender
            await plans_db.remove_premium(sender_user_id)
            
            # Add premium for the new user with the same expiry date
            await plans_db.add_premium(new_user_id, expiry)
            
            # Convert expiry date to IST format for display
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )
            time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            current_time = time_zone.strftime("%d-%m-%Y %I:%M:%S %p")
            
            # Confirmation message to the sender
            await message.reply_text(
                f"🔄 **PREMIUM PLAN TRANSFERRED**\n"
                f"╭───────────────────────────╮\n"
                f"  👤 **From:** {sender_user.mention}\n"
                f"  👤 **To:** {new_user.mention}\n"
                f"  📅 **Transferred:** {current_time} (IST)\n"
                f"  ⏳ **Expiry:** {expiry_str_in_ist} (IST)\n"
                f"╰───────────────────────────╯\n"
                f"✨ _Powered by CHOSEN ONE ⚝_"
            )
            
            # Notification to the new user
            await client.send_message(
                chat_id=new_user_id,
                text=(
                    f"🎉 **PREMIUM PLAN RECEIVED** 🎉\n"
                    f"╭───────────────────────────╮\n"
                    f"  👋 Hey {new_user.mention},\n"
                    f"  A premium plan has been transferred to you!\n\n"
                    f"  🛡️ **From:** {sender_user.mention}\n"
                    f"  ⏳ **Expiry:** {expiry_str_in_ist} (IST)\n"
                    f"  📅 **Date:** {current_time} (IST)\n"
                    f"╰───────────────────────────╯\n"
                    f"🚀 _Enjoy the unlimited speed and features!_"
                )
            )
        else:
            await message.reply_text("⚠️ **You are not a Premium user!**\n\nOnly Premium users can transfer their plans.")
    else:
        await message.reply_text("⚠️ **Usage:** /transfer user_id\n\nReplace `user_id` with the new user's ID.")


async def premium_remover():
    all_users = await plans_db.premium_users()
    removed_users = []
    not_removed_users = []

    for user_id in all_users:
        try:
            user = await app.get_users(user_id)
            chk_time = await plans_db.check_premium(user_id)

            if chk_time and chk_time.get("expire_date"):
                expiry_date = chk_time["expire_date"]

                if expiry_date <= datetime.datetime.now():
                    name = user.first_name
                    await plans_db.remove_premium(user_id)
                    await app.send_message(user_id, text=f"Hello {name}, your premium subscription has expired.")
                    print(f"{name}, your premium subscription has expired.")
                    removed_users.append(f"{name} ({user_id})")
                else:
                    name = user.first_name
                    current_time = datetime.datetime.now()
                    time_left = expiry_date - current_time

                    days = time_left.days
                    hours, remainder = divmod(time_left.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    if days > 0:
                        remaining_time = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
                    elif hours > 0:
                        remaining_time = f"{hours} hours, {minutes} minutes, {seconds} seconds"
                    elif minutes > 0:
                        remaining_time = f"{minutes} minutes, {seconds} seconds"
                    else:
                        remaining_time = f"{seconds} seconds"

                    print(f"{name} : Remaining Time : {remaining_time}")
                    not_removed_users.append(f"{name} ({user_id})")
        except:
            await plans_db.remove_premium(user_id)
            print(f"Unknown users captured : {user_id} removed")
            removed_users.append(f"Unknown ({user_id})")

    return removed_users, not_removed_users


@app.on_message(filters.command("freez") & filters.user(OWNER_ID))
async def refresh_users(_, message):
    removed_users, not_removed_users = await premium_remover()
    # Create a summary message
    removed_text = "\n".join(removed_users) if removed_users else "No users removed."
    not_removed_text = "\n".join(not_removed_users) if not_removed_users else "No users remaining with premium."
    summary = (
        f"**Here is Summary...**\n\n"
        f"> **Removed Users:**\n{removed_text}\n\n"
        f"> **Not Removed Users:**\n{not_removed_text}"
    )
    await message.reply(summary)
    
