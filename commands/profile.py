from config import ADMINS
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from db import get_user, add_user
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    db_user = get_user(user_id)
    if not db_user:
        add_user(user_id, user.username, starter_coins=0)
        db_user = get_user(user_id)

    # Admins always show as Admin
    rank = "ADMINISTRATOR" if user_id in ADMINS else db_user.get("rank", "Member")
    coins = db_user.get("coins", 0)
    fullname = user.full_name or user.username

    text = (
        f"👤 Your Profile:\n\n"
        f"📝Name: {fullname}\n"
        f"Rank: {rank}\n"
        f"💰Balance: {coins}\n\n"
    )

    await update.message.reply_text(text)

