from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, update_coins, get_all_users
from config import ADMINS  # List of admin IDs in config.py

# ----------------------------
# /ur command - remove coins from specific user
# ----------------------------
async def ur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not allowed to use this command!")
        return

    # Check arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /ur <user_id or @username> <amount>")
        return

    target = context.args[0]
    try:
        amount = int(context.args[1])
        if amount < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Amount must be a positive number.")
        return

    # Remove @ if mention
    if target.startswith("@"):
        target = target[1:]

    # Find target user
    target_user = None
    if target.isdigit():  # user_id
        target_user = get_user(int(target))
    else:  # username
        all_users = get_all_users()
        for u in all_users:
            if u["username"] == target:
                target_user = u
                break

    if not target_user:
        await update.message.reply_text(f"❌ User {context.args[0]} not found in DB.")
        return

    # Subtract coins safely (balance cannot go below 0)
    new_balance = max(target_user["coins"] - amount, 0)
    update_coins(target_user["user_id"], new_balance)

    await update.message.reply_text(
        f"✅ Removed {amount} coins from {target_user.get('username') or target_user['user_id']}.\n"
        f"💰 New balance: {new_balance} coins"
    )

# ----------------------------
# /urall command - remove coins from everyone
# ----------------------------
async def urall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not allowed to use this command!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /urall <amount>")
        return

    try:
        amount = int(context.args[0])
        if amount < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Amount must be a positive number.")
        return

    all_users = get_all_users()
    for user in all_users:
        new_balance = max(user["coins"] - amount, 0)
        update_coins(user["user_id"], new_balance)

    await update.message.reply_text(f"✅ Removed {amount} coins from all users ({len(all_users)} total).")

from db import reset_all_coins

async def resetall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMINS:
        await update.message.reply_text("❌ This command is admin-only.")
        return

    reset_all_coins()
    await update.message.reply_text("✅ All users' coins have been reset to 0!")
