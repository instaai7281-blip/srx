import re
from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.mongo.db import add_forward_mapping, remove_forward_mapping, get_all_forward_mappings

# Helper to check if sender is owner
def is_owner(user_id):
    owner_list = OWNER_ID if isinstance(OWNER_ID, list) else [OWNER_ID]
    return any(str(user_id) == str(o) for o in owner_list)

@app.on_message(filters.command("addforward") & filters.private)
async def add_forward_cmd(client, message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        await message.reply_text("❌ **Access Denied:** Only the bot owner can use this command.")
        return

    # Parse arguments: /addforward <user_id> <target_chat_id>
    parts = message.text.split()
    if len(parts) < 3:
        await message.reply_text(
            "📝 **Usage:** `/addforward <user_id> <target_chat_id>`\n\n"
            "**Examples:**\n"
            "• `/addforward 868659158 -100123456789` (Channel/Group)\n"
            "• `/addforward 868659158 -100123456789/42` (Group with Topic ID)"
        )
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await message.reply_text("❌ **Error:** User ID must be a valid integer.")
        return

    target_chat = parts[2].strip()
    
    # Simple validation of target chat ID
    if not target_chat.startswith("-100"):
        await message.reply_text("❌ **Error:** Target Chat ID must start with `-100`.")
        return

    await add_forward_mapping(target_user_id, target_chat)
    await message.reply_text(
        f"✅ **Success:** Mapped User `{target_user_id}` extractions to destination `{target_chat}`."
    )

@app.on_message(filters.command("removeforward") & filters.private)
async def remove_forward_cmd(client, message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        await message.reply_text("❌ **Access Denied:** Only the bot owner can use this command.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.reply_text("📝 **Usage:** `/removeforward <user_id>`")
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await message.reply_text("❌ **Error:** User ID must be a valid integer.")
        return

    await remove_forward_mapping(target_user_id)
    await message.reply_text(f"🗑️ **Success:** Removed forward mapping for User `{target_user_id}`.")

@app.on_message(filters.command("listforward") & filters.private)
async def list_forward_cmd(client, message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        await message.reply_text("❌ **Access Denied:** Only the bot owner can use this command.")
        return

    mappings = await get_all_forward_mappings()
    if not mappings:
        await message.reply_text("📋 **No active forward mappings configured.**")
        return

    response = "📋 **Active Auto-Forward Mappings:**\n\n"
    for uid, dest in mappings:
        response += f"• **User:** `{uid}` ➔ **Destination:** `{dest}`\n"

    await message.reply_text(response)
