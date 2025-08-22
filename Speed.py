import logging
import re
import aiohttp
from urllib.parse import quote
from pymongo import MongoClient  
from telegram.ext import CallbackQueryHandler  # 📌 Add this if not already
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Message
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, filters
)

# Configuration
BOT_TOKEN = "7636087687:AAHnAy6ywGGhzUSlXq7s_DTp-UfE-Y2wbhQ"  # 🔐 Replace with your actual bot token
API_BASE = "https://test-api.gaurav281833.workers.dev"
ADMIN_IDS = [7372592479]  # Optional: Add your Telegram user IDs here

# ✅ MongoDB Setup (add this before main() or inside your config section)
client = MongoClient("")  # Change to your actual MongoDB URI
db = client["terabox_bot"]
all_users_collection = db["users"]

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# TeraBox URL pattern
TERABOX_URL_REGEX = r'^https:\/\/(www\.)?(terabox\.com|1024terabox\.com|teraboxapp\.com|teraboxlink\.com)\/(s|sharing\/link)\/[A-Za-z0-9_\-]+'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # ✅ Save user if new
    if not all_users_collection.find_one({"user_id": user_id}):
        all_users_collection.insert_one({"user_id": user_id})

    welcome_msg = (
        f"👋 Hello {user.first_name}!\n\n"
        "🎥 I'm TeraBox Video Bot. Send me a TeraBox link and "
        "I'll stream the video directly in Telegram!\n\n"
        "🔗 Supported link formats:\n"
        "• https://terabox.com/s/xxxxxx\n"
        "• https://www.terabox.com/sharing/link?surl=xxxxxx"
    )
    await update.message.reply_text(welcome_msg)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if not re.match(TERABOX_URL_REGEX, text):
        await update.message.reply_text("❌ Invalid TeraBox link. Please send a valid sharing link.")
        return

    processing_msg = await update.message.reply_text("⏳ Processing your TeraBox link...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/api?url={text}") as resp:
                if resp.status != 200:
                    await processing_msg.edit_text(f"❌ API Error: {resp.status}")
                    return

                data = await resp.json()

                if "error" in data:
                    await processing_msg.edit_text(f"❌ Error: {data['error']}")
                    return

                for file in data.get("files", []):
                    if not file['file_name'].lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm')):
                        continue

                    caption = (
                        f"🎬 <b>{file['file_name']}</b>\n"
                        f"📦 <i>{file['file_size']}</i>\n\n"
                        "🔻 Tap below to watch or download"
                    )

                    stream_link = file['proxy_url']

                    # 🔸 Removed Direct Download button
                    buttons = [
                        [InlineKeyboardButton("▶️ Watch in Telegram", web_app=WebAppInfo(url=stream_link))]
                    ]
                    markup = InlineKeyboardMarkup(buttons)

                    async def send_text_response():
                        await update.message.reply_text(
                            text=caption,
                            parse_mode="HTML",
                            reply_markup=markup
                        )
                        await processing_msg.delete()

                    if file.get('thumbnail'):
                        try:
                            await update.message.reply_photo(
                                photo=file['thumbnail'],
                                caption=caption,
                                parse_mode="HTML",
                                reply_markup=markup
                            )
                            await processing_msg.delete()
                        except Exception as e:
                            logger.error(f"Error sending photo: {e}")
                            await send_text_response()
                    else:
                        await send_text_response()

                    break

    except Exception as e:
        logger.error(f"Error processing link: {e}")
        await processing_msg.edit_text("⚠️ An error occurred. Please try again later.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"⚠️ Error occurred:\n\n{context.error}"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

# Broadcast command handler
async def broadcast_message(self, message: Message, user_id: int):
    """Send a message to a single user"""
    try:
        caption = message.caption if message.caption else None
        reply_markup = message.reply_markup if message.reply_markup else None

        if message.text:
            await self.app.send_message(
                chat_id=user_id,
                text=message.text,
                entities=message.entities,
                reply_markup=reply_markup,
                disable_notification=True
            )
        elif message.photo:
            await self.app.send_photo(
                chat_id=user_id,
                photo=message.photo.file_id,
                caption=caption,
                caption_entities=message.caption_entities,
                reply_markup=reply_markup,
                disable_notification=True
            )
        elif message.video:
            await self.app.send_video(
                chat_id=user_id,
                video=message.video.file_id,
                caption=caption,
                caption_entities=message.caption_entities,
                reply_markup=reply_markup,
                disable_notification=True
            )
        elif message.audio:
            await self.app.send_audio(
                chat_id=user_id,
                audio=message.audio.file_id,
                caption=caption,
                caption_entities=message.caption_entities,
                reply_markup=reply_markup,
                disable_notification=True
            )
        elif message.document:
            await self.app.send_document(
                chat_id=user_id,
                document=message.document.file_id,
                caption=caption,
                caption_entities=message.caption_entities,
                reply_markup=reply_markup,
                disable_notification=True
            )
        elif message.animation:
            await self.app.send_animation(
                chat_id=user_id,
                animation=message.animation.file_id,
                caption=caption,
                caption_entities=message.caption_entities,
                reply_markup=reply_markup,
                disable_notification=True
            )
        elif message.sticker:
            await self.app.send_sticker(
                chat_id=user_id,
                sticker=message.sticker.file_id,
                disable_notification=True
            )
        elif message.voice:
            await self.app.send_voice(
                chat_id=user_id,
                voice=message.voice.file_id,
                caption=caption,
                caption_entities=message.caption_entities,
                reply_markup=reply_markup,
                disable_notification=True
            )
        elif message.video_note:
            await self.app.send_video_note(
                chat_id=user_id,
                video_note=message.video_note.file_id,
                disable_notification=True
            )

        return True, ""

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await self.broadcast_message(message, user_id)
    
    except InputUserDeactivated:
        return False, "deactivated"
    except UserIsBlocked:
        return False, "blocked"
    except PeerIdInvalid:
        return False, "invalid_id"
    except Exception as e:
        return False, f"other:{str(e)}"

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message

    if user_id not in ADMIN_IDS:

        await message.reply_text("⛔️ You are not authorized to use this command!")
        return

    # Get the message to broadcast
    if message.reply_to_message:
        broadcast_content = message.reply_to_message
    elif context.args:
        broadcast_content = " ".join(context.args)
    else:
        await message.reply_text("❗️ Please reply to a message or type a message to broadcast.")
        return

    status_msg = await message.reply_text("🚀 Starting broadcast...")

    total_users = all_users_collection.count_documents({})
    done = success = failed = blocked = deleted = invalid = 0
    failed_users = []

    users_list = list(all_users_collection.find({}, {'user_id': 1}))

    for user in users_list:
        done += 1
        try:
            if isinstance(broadcast_content, str):
                await context.bot.send_message(chat_id=user['user_id'], text=broadcast_content)
            else:
                # **Forward the original message** with "forwarded from" header
                await context.bot.forward_message(
                    chat_id=user['user_id'],
                    from_chat_id=broadcast_content.chat.id,
                    message_id=broadcast_content.message_id
                )
            success += 1
        except TelegramError as e:
            failed += 1
            failed_users.append((user['user_id'], str(e)))
            if "blocked" in str(e):
                blocked += 1
            elif "deactivated" in str(e):
                deleted += 1
            elif "invalid" in str(e):
                invalid += 1

        if done % 20 == 0:
            try:
                await status_msg.edit_text(
                    f"🚀 Broadcast in Progress...\n\n"
                    f"👥 Total Users: {total_users}\n"
                    f"✅ Completed: {done} / {total_users}\n"
                    f"✨ Success: {success}\n"
                    f"⚠️ Failed: {failed}\n\n"
                    f"🚫 Blocked: {blocked}\n"
                    f"❗️ Deleted: {deleted}\n"
                    f"📛 Invalid: {invalid}"
                )
            except Exception:
                pass

    await status_msg.edit_text(
        f"✅ Broadcast Completed!\n"
        f"👥 Total Users: {total_users}\n"
        f"✨ Success: {success}\n"
        f"⚠️ Failed: {failed}\n"
        f"🚫 Blocked: {blocked}\n"
        f"❗️ Deleted: {deleted}\n"
        f"📛 Invalid: {invalid}"
    )

    if failed_users:
        clean_msg = await message.reply_text("🧹 Cleaning database... Removing invalid users.")
        invalid_user_ids = [uid for uid, _ in failed_users]
        result = all_users_collection.delete_many({"user_id": {"$in": invalid_user_ids}})
        await clean_msg.edit_text(f"🧹 Database cleaned! Removed {result.deleted_count} invalid users.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    application.add_error_handler(error_handler)

    logger.info("🚀 Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()
