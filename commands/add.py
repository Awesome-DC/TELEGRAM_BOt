from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, update_coins, get_all_users
from config import ADMINS

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not allowed to use this command!")
        return

    # Check arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add <user_id or @username> <amount>")
        return

    target = context.args[0]
    try:
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Amount must be a number.")
        return

    # Remove @ if mention
    if target.startswith("@"):
        target = target[1:]

    # Try to find user in DB
    target_user = None
    if target.isdigit():  # user_id
        target_user = get_user(int(target))
    else:  # username
        # search by username
        all_users = get_all_users()
        for u in all_users:
            if u["username"] == target:
                target_user = u
                break

    if not target_user:
        await update.message.reply_text(f"❌ User {context.args[0]} not found in DB.")
        return

    # Update coins
    new_balance = target_user["coins"] + amount
    update_coins(target_user["user_id"], new_balance)

    await update.message.reply_text(
        f"✅ Added {amount} coins to {target_user.get('username') or target_user['user_id']}. "
        f"New balance: {new_balance} coins"
    )

# ------------------------------

async def addall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not allowed to use this command!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /addall <amount>")
        return

    try:
        amount = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Amount must be a number.")
        return

    all_users = get_all_users()
    for user in all_users:
        new_balance = user["coins"] + amount
        update_coins(user["user_id"], new_balance)

    await update.message.reply_text(f"✅ Added {amount} coins to all users.")
