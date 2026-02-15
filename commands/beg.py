import random
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, update_coins

# Define min and max coins for beg
MIN_COINS = -50
MAX_COINS = 100

async def beg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    user = get_user(user_id)
    if not user:
        await update.message.reply_text("❌ You need to /start first!")
        return

    # Random coin change
    coins_change = random.randint(MIN_COINS, MAX_COINS)

    new_balance = user["coins"] + coins_change
    update_coins(user_id, new_balance)

    if coins_change > 0:
        reply = (
            f"🙏 You begged and got {coins_change} coins!\n"
            f"💰 New balance: {new_balance} coins"
        )
    elif coins_change < 0:
        reply = (
            f"😢 You begged but lost {abs(coins_change)} coins...\n"
            f"💰 New balance: {new_balance} coins"
        )
    else:
        reply = (
            f"😐 You begged but got nothing this time...\n"
            f"💰 Balance remains: {new_balance} coins"
        )

    await update.message.reply_text(reply)
