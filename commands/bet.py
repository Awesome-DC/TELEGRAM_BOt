import asyncio
import random
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, update_coins

open_bets = {}  # {chat_id: {creator_id, amount, participants, timeout_task}}

BET_TIMEOUT = 10  # seconds

async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ You need to /start first!")
        return

    # Parse amount
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /bet <amount> (positive number)")
        return

    if user["coins"] < amount:
        await update.message.reply_text(f"❌ You only have {user['coins']} coins.")
        return

    if chat_id in open_bets:
        await update.message.reply_text("❌ A bet is already open. Wait for it to finish.")
        return

    # Deduct stake from creator
    update_coins(user_id, user["coins"] - amount)

    # Create bet
    open_bets[chat_id] = {
        "creator_id": user_id,
        "amount": amount,
        "participants": [user_id]
    }

    await update.message.reply_text(
        f"🎲 Bet of {amount} coins opened by {update.effective_user.full_name}!\n"
        "Others have 10 seconds to join with /join"
    )

    # Start timeout
    async def resolve_bet():
        await asyncio.sleep(BET_TIMEOUT)
        if chat_id not in open_bets:
            return
        bet_info = open_bets.pop(chat_id)
        participants = bet_info["participants"]
        total_pot = bet_info["amount"] * len(participants)
        winner_id = random.choice(participants)
        winner_user = get_user(winner_id)
        new_balance = winner_user["coins"] + total_pot
        update_coins(winner_id, new_balance)
        await context.bot.send_message(
            chat_id,
            f"🏆 Bet ended!\nWinner: {winner_user['username'] or winner_id}\n"
            f"Pot: {total_pot} coins\nNew balance: {new_balance} coins"
        )

    asyncio.create_task(resolve_bet())

# --------------------
# /join command
# --------------------
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = get_user(user_id)

    if chat_id not in open_bets:
        await update.message.reply_text("❌ No active bet to join.")
        return

    bet_info = open_bets[chat_id]

    if user_id in bet_info["participants"]:
        await update.message.reply_text("❌ You already joined this bet.")
        return

    if user["coins"] < bet_info["amount"]:
        await update.message.reply_text(f"❌ You only have {user['coins']} coins.")
        return

    # Deduct stake from joiner
    update_coins(user_id, user["coins"] - bet_info["amount"])
    bet_info["participants"].append(user_id)

    await update.message.reply_text(
        f"✅ {update.effective_user.full_name} joined the bet of {bet_info['amount']} coins!"
    )
