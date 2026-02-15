from telegram import Update
from telegram.ext import ContextTypes
from db import get_all_users  # Your DB function that returns all users
from config import ADMINS

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    args = context.args

    if sender.id not in ADMINS:
        await update.message.reply_text("❌ You are not an admin.")
        return

    if not args:
        await update.message.reply_text("❌ Usage: /broadcast <message>")
        return

    message_text = " ".join(args)

    # Fetch all users from your database
    users = get_all_users()  # replace with your DB function that returns list of dicts

    count = 0
    for user in users:
        # Skip admins
        if user['user_id'] in ADMINS:
            continue
        try:
            await context.bot.send_message(
                chat_id=user['user_id'],  # make sure this is the correct field in your DB
                text=f"📢 *Broadcast message from Admin*\n\n{message_text}",
                parse_mode="Markdown"
            )
            count += 1
        except Exception as e:
            print(f"Failed to send to {user['user_id']}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")