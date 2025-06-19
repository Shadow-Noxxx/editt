import html
import logging
import re
import asyncio
import time
from random import choice
from Null import *
from telegram import Update, Bot
from pyrogram import Client, filters
from pyrogram.types import Message
from telegram.utils.helpers import escape_markdown, mention_html
from telegram.utils.helpers import mention_markdown
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient
from config import LOGGER, MONGO_URI, DB_NAME, TELEGRAM_TOKEN, OWNER_ID, SUDO_ID, BOT_NAME, SUPPORT_ID, API_ID, API_HASH
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)


app = Client("AutoDelete", bot_token=TELEGRAM_TOKEN, api_id=API_ID, api_hash=API_HASH)
print("INFO: Starting Autodelete")
app.start()
bot = app
# Initialize your Pyrogram Client your bot's ID
# Define the text variables
texts = {
    "sudo_5": "Current Sudo Users:\n",
    "sudo_6": "Other Sudo Users:\n",
    "sudo_7": "No sudo users found."
}

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define StartTime at the beginning of the script
StartTime = time.time()

# MongoDB initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db['users']

# Define a list to store sudo user IDs
sudo_users = SUDO_ID.copy()  # Copy initial SUDO_ID list
sudo_users.append(OWNER_ID)  # Add owner to sudo users list initially

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time
def help(update: Update, context: CallbackContext):
    user = update.effective_user
    mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

SUPPORT_LINK = "https://t.me/+D2dATbDtZbNiNGJl"

# --- Helper Functions ---
async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Get the target user by:
    - Reply (preferred)
    - User ID (digits)
    - Username (@username or username)
    """
    chat_id = update.effective_chat.id
    # 1. If reply, return that user
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        return update.message.reply_to_message.from_user

    # 2. If argument is present, try to resolve as user_id or username
    if context.args and context.args[0]:
        arg = context.args[0]
        # Try user ID
        if arg.isdigit():
            try:
                member = await context.bot.get_chat_member(chat_id, int(arg))
                return member.user
            except Exception:
                pass
        # Try @username or username
        username = arg
        if username.startswith("@"):
            username = username[1:]
        # Try to get user from chat by username
        try:
            members = await context.bot.get_chat_administrators(chat_id)
            for m in members:
                if m.user.username and m.user.username.lower() == username.lower():
                    return m.user
        except Exception:
            pass
        try:
            member = await context.bot.get_chat_member(chat_id, username)
            return member.user
        except Exception:
            pass
        # Try to get user from chat admins
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            for m in admins:
                if m.user.username and m.user.username.lower() == username.lower():
                    return m.user
        except Exception:
            pass
        # Try get_chat with @username and username
        for uname in ("@" + username, username):
            try:
                user_obj = await context.bot.get_chat(uname)
                if user_obj:
                    return user_obj
            except Exception:
                continue
        # Try get_chat_member with username (rarely works)
        try:
            member = await context.bot.get_chat_member(chat_id, username)
            return member.user
        except Exception:
            pass

    await update.message.reply_text(
        "❌ <b>Couldn't find the user. Please reply or provide a valid user ID/username.</b>",
        parse_mode="HTML"
    )
    return None

def is_admin(member):
    return isinstance(member, ChatMemberAdministrator) or isinstance(member, ChatMemberOwner)
CHANNEL_USERNAME = "@federation_of_shadows"
# --- Command Handlers ---
async def is_user_in_channel(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logging.error(f"Error checking channel membership: {e}")
        return False

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        is_member = await is_user_in_channel(user.id, context.bot)
    except Exception as e:
        logging.error(f"start_handler: channel check failed: {e}")
        is_member = True  # fallback: allow

    if is_member:
        bot_me = await context.bot.get_me()
        processing_msg = await update.message.reply_text(
            "<b>⏳ Please wait while we process your request...</b>\n"
            "<i>Step 1: Initializing system modules...</i>",
            parse_mode="HTML"
        )
        await asyncio.sleep(0.8)
        try:
            await processing_msg.edit_text(
                "<b>⏳ Please wait while we process your request...</b>\n"
                "<i>Step 2: Verifying channel membership...</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(0.8)
        try:
            await processing_msg.edit_text(
                "<b>⏳ Please wait while we process your request...</b>\n"
                "<i>Step 3: Preparing your personalized welcome...</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(0.8)
        try:
            await processing_msg.edit_text(
                "<b>⏳ Please wait while we process your request...</b>\n"
                "<i>Step 4: Finalizing setup...</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(0.6)
        welcome_text = (
    f"<b>👋 Welcome, {user.mention_html()}!</b>\n"
    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
    f"<b>🛡 {bot_me.mention_html()} — Edit Guardian Bot</b>\n"
    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
    f"• ✏️ Monitors and Deletes Unauthorized Edits\n"
    f"• 🔐 Protects Group Integrity from Message Tampering\n"
    f"• 👤 Owner-Only Sudo Control & Admin Commands\n"
    f"• 📊 Real-Time Stats & Cloning Capabilities\n"
    f"• 🚨 Fast, Lightweight & Always on Duty\n"
    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
    f"<i>Use <code>/help</code> to view all available features & setup instructions.</i>"
)

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_me.username}?startgroup=true")],
            [
                InlineKeyboardButton("👑 Owner", url="https://t.me/FOS_FOUNDER"),
                InlineKeyboardButton("💬 Support", url=SUPPORT_LINK),
            ]
        ])
        try:
            with open("C:/Users/Anirudh/Desktop/ichizen.mp4", "rb") as video_file:
                await processing_msg.delete()
                await update.message.reply_video(
                    video=video_file,
                    caption=welcome_text,
                    parse_mode="HTML",
                    reply_markup=kb
                )
        except Exception:
            await processing_msg.edit_text(
                welcome_text,
                parse_mode="HTML",
                reply_markup=kb
            )
    else:
        keyboard = [
            [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"<b>Access Restricted</b>\n"
            f"Hello {user.mention_html()},\n\n"
            "To access the full features of this bot, please join our official channel first.\n"
            "Once you have joined, use /start again.",
            parse_mode="HTML",
            reply_markup=reply_markup
        )


def get_user_id(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /id <username>")
        return

    username = context.args[0]
    if not username.startswith('@'):
        update.message.reply_text("Please provide a valid username starting with '@'.")
        return
    try:
        user = context.bot.get_chat(username)
        user_id = user.id
        update.message.reply_text(f"User ID of {username} is {user_id}.")
    except Exception as e:
        update.message.reply_text(f"Failed to get user ID: {e}")
        logger.error(f"get_user_id error: {e}")


def check_edit(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    # Check if the update is an edited message
    if update.edited_message:
        edited_message = update.edited_message
        
        # Get the chat ID and message ID
        chat_id = edited_message.chat_id
        message_id = edited_message.message_id
        
        # Get the user who edited the message
        user_id = edited_message.from_user.id
        
        # Create the mention for the user
        user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(edited_message.from_user.first_name)}</a>"
        
        # Delete the message if the editor is not the owner
        if user_id not in sudo_users:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            
            # Send a message notifying about the deletion
            bot.send_message(chat_id=chat_id, text=f"{user_mention} 𝗷𝘂𝘀𝘁 𝗲𝗱𝗶𝘁 𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲. 𝗜 𝗱𝗲𝗹𝗲𝘁𝗲 𝗵𝗶𝘀 𝗲𝗱𝗶𝘁𝗲𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲.", parse_mode='HTML')


def add_sudo(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Check if the user is the owner
    if user.id != OWNER_ID:
        update.message.reply_text("𝗬𝗼𝘂 𝗱𝗼 𝗻𝗼𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")
        return
    
    # Check if a username or user ID is provided
    if len(context.args) != 1:
        update.message.reply_text("𝗨𝘀𝗮𝗴𝗲: /addsudo <username or user ID>")
        return
    
    sudo_user = context.args[0]
    
    # Resolve the user ID from username if provided
    try:
        sudo_user_obj = context.bot.get_chat_member(chat_id=chat_id, user_id=sudo_user)
        sudo_user_id = sudo_user_obj.user.id
    except Exception as e:
        update.message.reply_text(f"𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗿𝗲𝘀𝗼𝗹𝘃𝗲 𝘂𝘀𝗲𝗿: {e}")
        return
    
    # Add sudo user ID to the list if not already present
    if sudo_user_id not in sudo_users:
        sudo_users.append(sudo_user_id)
        update.message.reply_text(f"𝗔𝗱𝗱𝗲𝗱 {sudo_user_obj.user.username} 𝗮𝘀 𝗮 𝘀𝘂𝗱𝗼 𝘂𝘀𝗲𝗿.")
    else:
        update.message.reply_text(f"{sudo_user_obj.user.username} 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗮 𝘀𝘂𝗱𝗼 𝘂𝘀𝗲𝗿.")


def sudo_list(update: Update, context: CallbackContext):
    # Check if the user is the owner
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("𝗬𝗼𝘂 𝗱𝗼 𝗻𝗼𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")
        return

    # Prepare the response message with SUDO_ID users
    text = "𝗟𝗶𝘀𝘁 𝗼𝗳 𝘀𝘂𝗱𝗼 𝘂𝘀𝗲𝗿𝘀:\n"
    count = 1
    smex = 0

    # Add the owner
    try:
        owner = context.bot.get_chat(OWNER_ID)
        owner_mention = mention_markdown(OWNER_ID, owner.first_name)
        text += f"{count} {owner_mention}\n"
    except Exception as e:
        update.message.reply_text(f"Failed to get owner details: {e}")

    # Add other sudo users
    for user_id in SUDO_ID:
        if user_id != SUDO_ID:
            try:
                user = context.bot.get_chat(user_id)
                user_mention = mention_markdown(user_id, user.first_name)
                if smex == 0:
                    smex += 1
                count += 1                
                text += f"{count} {user_mention}\n"
            except Exception as e:
                update.message.reply_text(f"Failed to get user details for user_id {user_id}: {e}")

    if not text.strip():
        update.message.reply_text("No sudo users found.")
    else:
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# Register the sudo_list command hand

def send_stats(update: Update, context: CallbackContext):
    user = update.effective_user
    
    # Check if the user is the owner
    if user.id != OWNER_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return
    
    try:
        # Fetch all users who have interacted with the bot
        users_count = users_collection.count_documents({})
        
        # Fetch all unique chat IDs the bot is currently in
        chat_count = chats_collection.count_documents({})
        
        # Prepare the response message
        stats_msg = f"Total Users: {users_count}\n"
        stats_msg += f"Total Chats: {chat_count}\n"
        
        update.message.reply_text(stats_msg)
        
    except Exception as e:
        logger.error(f"Error in send_stats function: {e}")
        update.message.reply_text("Failed to fetch statistics.")
 
def clone(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Check if the user is the owner
    if user.id != OWNER_ID:
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼 𝗮𝘂𝘁𝗵𝗿𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")
        return

    # Get the bot token from the command
    if len(context.args) != 1:
        update.message.reply_text("𝗨𝘀𝗮𝗴𝗲: /clone <Your Bot Token>")
        return

    new_bot_token = context.args[0]

    try:
        # Create a new bot instance
        new_bot = Bot(token=new_bot_token)
        new_bot_info = new_bot.get_me()

        # Clone all handlers from the main bot to the new bot
        clone_updater = Updater(token=new_bot_token, use_context=True)
        clone_dispatcher = clone_updater.dispatcher

        # Add existing handlers to the cloned bot
        clone_dispatcher.add_handler(CommandHandler("start", start))
        clone_dispatcher.add_handler(MessageHandler(Filters.update.edited_message, check_edit))
        clone_dispatcher.add_handler(CommandHandler("addsudo", add_sudo))
        clone_dispatcher.add_handler(CommandHandler("sudolist", sudo_list))
        clone_dispatcher.add_handler(CommandHandler("stats", send_stats))
        clone_dispatcher.add_handler(CommandHandler("clone", clone))

        # Start the cloned bot
        clone_updater.start_polling()

        update.message.reply_text(
            f"𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗰𝗹𝗼𝗻𝗲𝗱 𝗯𝗼𝘁 {new_bot_info.username} ({new_bot_info.id})."
        )

    except Exception as e:
        update.message.reply_text(f"𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗰𝗹𝗼𝗻𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁: {e}")

# Command handler for /getid
def get_id(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    msg = update.effective_message
    user_id = extract_user(msg, args)

    if user_id:
        if msg.reply_to_message and msg.reply_to_message.forward_from:
            user1 = message.reply_to_message.from_user
            user2 = message.reply_to_message.forward_from

            msg.reply_text(
                f"<b>ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ:</b>,"
                f"• {html.escape(user2.first_name)} - <code>{user2.id}</code>.\n"
                f"• {html.escape(user1.first_name)} - <code>{user1.id}</code>.",
                parse_mode=ParseMode.HTML,
            )

        else:
            user = bot.get_chat(user_id)
            msg.reply_text(
                f"{html.escape(user.first_name)}'s ɪᴅ ɪs <code>{user.id}</code>.",
                parse_mode=ParseMode.HTML,
            )

    else:
        if chat.type == "private":
            msg.reply_text(
                f"ʏᴏᴜʀ ᴜsᴇʀ ɪᴅ ɪs <code>{chat.id}</code>.", parse_mode=ParseMode.HTML
            )

        else:
            msg.reply_text(
                f"ᴛʜɪs ɢʀᴏᴜᴩ's ɪᴅ ɪs <code>{chat.id}</code>.", parse_mode=ParseMode.HTML
            )

@app.on_message(filters.command("id"))
async def userid(client, message):
    chat = message.chat
    your_id = message.from_user.id
    message_id = message.message_id
    reply = message.reply_to_message

    text = f"**Message ID:** `{message_id}`\n"
    text += f"**Your ID:** `{your_id}`\n"
    
    if not message.command:
        message.command = message.text.split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**User ID:** `{user_id}`\n"
        except Exception:
            return await eor(message, text="This user doesn't exist.")

    text += f"**Chat ID:** `{chat.id}`\n\n"
    if not getattr(reply, "empty", True):
        id_ = reply.from_user.id if reply.from_user else reply.sender_chat.id
        text += (
            f"**Replied Message ID:** `{reply.message_id}`\n"
        )
        text += f"**Replied User ID:** `{id_}`"

    await eor(
        message,
        text=text,
        disable_web_page_preview=True,
        parse_mode="md",
            )

# Function to send message to SUPPORT_ID group


def main():

    if SUPPORT_ID is not None and isinstance(SUPPORT_ID, str):
        try:
            dispatcher.bot.sendphoto(
                f"{SUPPORT_ID}",
                photo=PM_START_IMG,               
                caption=f"""
𝗛𝗲𝗹𝗹𝗼 𝗜 𝗮𝗺 𝘀𝘁𝗮𝗿𝘁𝗲𝗱 𝘁𝗼 𝗺𝗮𝗻𝗮𝗴𝗲 𝗲𝗱𝗶𝘁𝗲𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 ! 𝗜 𝗮𝗺 𝗖𝗿𝗲𝗮𝘁𝗲 𝗯𝘆 @nullcrow""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to {SUPPORT_ID}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)    
    # Create the Updater and pass it your bot's token
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.update.edited_message, check_edit))
    dispatcher.add_handler(CommandHandler("addsudo", add_sudo))
    dispatcher.add_handler(CommandHandler("sudolist", sudo_list))
    dispatcher.add_handler(CommandHandler("clone", clone))
    dispatcher.add_handler(CommandHandler("stats", send_stats))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    # Start the bot




      
