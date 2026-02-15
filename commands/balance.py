from telegram import Update
from telegram.ext import ContextTypes
from db import add_user, get_user

# 3️⃣ /balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    user = get_user(user_id)
    if not user:
        # Auto-add if they never typed /start
        add_user(user_id, username, starter_coins=0)
        coins = 0
    else:
        coins = user["coins"]

    await update.message.reply_text(
        f"💰 {update.effective_user.first_name}, your current balance is: {coins} coins"
    )