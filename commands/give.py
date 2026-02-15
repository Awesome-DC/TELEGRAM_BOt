from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, update_coins, get_all_users

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    sender = get_user(sender_id)

    if not sender:
        await update.message.reply_text("❌ You need to /start first!")
        return

    # Check arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /give <user_id or @username> <amount>")
        return

    target = context.args[0]
    try:
        amount = int(context.args[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Amount must be a positive number")
        return

    # Check sender balance
    if sender["coins"] < amount:
        await update.message.reply_text(f"❌ You only have {sender['coins']} coins. Cannot give {amount} coins.")
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
        await update.message.reply_text(f"❌ User {context.args[0]} not found in the database.")
        return

    # Transfer coins
    new_sender_balance = sender["coins"] - amount
    new_target_balance = target_user["coins"] + amount

    update_coins(sender_id, new_sender_balance)
    update_coins(target_user["user_id"], new_target_balance)

    await update.message.reply_text(
        f"💸 You gave {amount} coins to {target_user.get('username') or target_user['user_id']}\n"
        f"💰 Your new balance: {new_sender_balance} coins"
    )
