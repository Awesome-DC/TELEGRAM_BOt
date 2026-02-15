import random
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, update_coins

async def evenodd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("❌ You need to /start first!")
        return

    # Parse arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /evenodd <amount> <even|odd>")
        return

    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Amount must be a positive number")
        return

    choice = context.args[1].lower()
    if choice not in ["even", "odd"]:
        await update.message.reply_text("❌ Choice must be 'even' or 'odd'")
        return

    # Check user balance
    if user["coins"] < amount:
        await update.message.reply_text(f"❌ You only have {user['coins']} coins. Cannot bet {amount}.")
        return

    # Deduct stake
    new_balance = user["coins"] - amount
    update_coins(user_id, new_balance)

    # Generate random number
    result = random.randint(1, 10)
    result_type = "even" if result % 2 == 0 else "odd"

    if choice == result_type:
        winnings = amount * 2
        new_balance += winnings
        update_coins(user_id, new_balance)
        reply = (
            f"🎲 You bet {amount} coins on {choice}\n"
            f"The number is {result} ({result_type})\n"
            f"🎉 You won! You earned {winnings} coins\n"
            f"💰 New balance: {new_balance} coins"
        )
    else:
        reply = (
            f"🎲 You bet {amount} coins on {choice}\n"
            f"The number is {result} ({result_type})\n"
            f"❌ You lost {amount} coins\n"
            f"💰 New balance: {new_balance} coins"
        )

    await update.message.reply_text(reply)
