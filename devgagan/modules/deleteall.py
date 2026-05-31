import asyncio
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from devgagan import app
from config import OWNER_ID

@app.on_message(filters.command("deleteall"))
async def delete_all_cmd(_, message):
    chat_id = message.chat.id
    
    # 1. Direct check: only works in channels or groups
    if message.chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply("❌ **Error:** This command can only be used in channels or groups.")
        return

    # 2. Check authorization of the sender (if sent by a user)
    if message.from_user:
        user_id = message.from_user.id
        if user_id not in OWNER_ID:
            # Check if they are admin in this chat
            try:
                member = await app.get_chat_member(chat_id, user_id)
                if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                    await message.reply("❌ **Access Denied:** Only administrators can use this command.")
                    return
            except Exception:
                await message.reply("❌ **Access Denied:** You are not authorized here.")
                return

    # 3. Send confirmation message with buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗑️ Delete All", callback_data="confirm_delete_all"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete_all")
        ]
    ])
    
    await message.reply(
        "⚠️ **WARNING:**\n\n"
        "Are you absolutely sure you want to delete **all messages** in this chat?\n"
        "This action is permanent and cannot be undone!",
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex(r"^(confirm_delete_all|cancel_delete_all)$"))
async def delete_all_callback(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # Verify clicker's rights (Must be chat owner, chat administrator, or global bot owner)
    authorized = False
    if user_id in OWNER_ID:
        authorized = True
    else:
        try:
            member = await app.get_chat_member(chat_id, user_id)
            if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                authorized = True
        except Exception:
            pass

    if not authorized:
        await callback_query.answer("❌ Only administrators of this chat can perform this action!", show_alert=True)
        return

    if callback_query.data == "cancel_delete_all":
        await callback_query.message.edit_text("❌ **Operation cancelled.** No messages were deleted.")
        return

    # Confirm delete all
    await callback_query.message.edit_text("⌛ **Initializing mass deletion...**")
    
    try:
        current_id = callback_query.message.id
        # Generate message IDs from current_id - 1 down to 1 (limit to 10,000 messages)
        start_id = current_id - 1
        end_id = max(1, current_id - 10000)
        
        message_ids = list(range(start_id, end_id - 1, -1))
        deleted_count = 0
        batch_size = 100
        
        # Sequentially delete the IDs in batches
        for k in range(0, len(message_ids), batch_size):
            batch = message_ids[k:k+batch_size]
            try:
                await app.delete_messages(chat_id, batch)
                deleted_count += len(batch)
                await asyncio.sleep(0.3)  # Simple delay to avoid rate limits
            except Exception:
                pass

        await callback_query.message.edit_text(
            "✅ **Success!**\n\n"
            "Wiped the chat/channel history successfully."
        )
        
    except Exception as e:
        await callback_query.message.edit_text(f"❌ **An error occurred during deletion:** `{str(e)}`")
