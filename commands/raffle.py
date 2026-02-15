import asyncio
import time
import random
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from db import get_user, update_coins, add_user
from config import ADMINS 
active_giveaways = {}

# ------------------------------
# /giveaway <amount> (ADMIN ONLY)
# ------------------------------
async def giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id not in ADMINS:
        await update.message.reply_text("❌ This command is admin-only.")
        return

    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /giveaway <amount>")
        return

    if chat_id in active_giveaways:
        await update.message.reply_text("❌ A giveaway is already running.")
        return

    # Initialize giveaway
    active_giveaways[chat_id] = {
        "amount": amount,
        "participants": set(),  # now storing tuples (user_id, username)
        "ends_at": time.time() + 15,
    }

    await update.message.reply_text(
        f"🎁 GIVEAWAY STARTED!\n"
        f"💰 Total prize: {amount} coins\n"
        f"⏳ Ends in 15 seconds\n"
        f"Players type /rjoin to participate!"
    )

    # Run countdown in background so /rjoin works
    asyncio.create_task(giveaway_countdown(chat_id, context))


# ------------------------------
# Background countdown
# ------------------------------
async def giveaway_countdown(chat_id, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(15)
    await resolve_giveaway(chat_id, context)


# ------------------------------
# /rjoin
# ------------------------------
async def rjoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    chat_id = update.effective_chat.id

    giveaway = active_giveaways.get(chat_id)
    if not giveaway:
        await update.message.reply_text("❌ No active giveaway in this chat.")
        return

    if time.time() > giveaway["ends_at"]:
        await update.message.reply_text("❌ Giveaway already ended.")
        return

    participant = (user_id, username)

    if participant in giveaway["participants"]:
        await update.message.reply_text("⚠️ You already joined!")
        return

    giveaway["participants"].add(participant)
    await update.message.reply_text(f"✅ You joined the giveaway, {username}!")


# ------------------------------
# Resolve giveaway
# ------------------------------
async def resolve_giveaway(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    giveaway = active_giveaways.pop(chat_id, None)
    if not giveaway:
        return

    participants = list(giveaway["participants"])
    total_amount = giveaway["amount"]

    if not participants:
        await context.bot.send_message(chat_id, "❌ No one joined the giveaway.")
        return

    # Random split
    num_players = len(participants)
    splits = [random.randint(1, 100) for _ in range(num_players)]
    total_splits = sum(splits)
    coins_list = [int(total_amount * s / total_splits) for s in splits]

    # Fix rounding
    diff = total_amount - sum(coins_list)
    if diff != 0:
        coins_list[0] += diff

    # Build final message
    message = "🎉 Giveaway ended! Coins distributed:\n\n"

    for (uid, username), coins in zip(participants, coins_list):
        user = get_user(uid)
        if not user:
            add_user(uid)
            user = get_user(uid)

        update_coins(uid, user["coins"] + coins)
        message += f"{username} → {coins} coins\n"

        # DM participant
        try:
            await context.bot.send_message(uid, f"🎁 You received {coins} coins from the giveaway!")
        except:
            pass

    await context.bot.send_message(chat_id, message)
