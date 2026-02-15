import os
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMINS

# -----------------------------
# /backup command
# -----------------------------
async def backup_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not admin.")
        return

    db_file = "bot.db"

    if not os.path.exists(db_file):
        await update.message.reply_text("❌ Database file not found.")
        return

    # Send the DB file to the admin
    with open(db_file, "rb") as f:
        await update.message.reply_document(document=f, filename="bot_backup.db")

    await update.message.reply_text("✅ Database backup sent.")