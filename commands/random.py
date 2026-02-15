# import asyncio
# import random
# from telegram import Update
# from telegram.ext import ContextTypes, CommandHandler
# from db import get_user, get_all_users, update_coins, update_last_chat
# from config import ADMINS
# # -----------------------------
# # /raffle - admin only
# # -----------------------------
# async def raffle(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.effective_chat.id
#     user_id = update.effective_user.id

#     # Admin list # replace with your Telegram ID(s)
#     if user_id not in ADMINS:
#         await update.message.reply_text("❌ Only admins can start a raffle.")
#         return

#     # Track user chat
#     update_last_chat(user_id, chat_id)

#     # Parse stake
#     try:
#         stake = int(context.args[0])
#         if stake <= 0:
#             raise ValueError
#     except (IndexError, ValueError):
#         await update.message.reply_text("Usage: /raffle <stake>")
#         return

#     await update.message.reply_text(
#         f"🎟️ Admin started a raffle!\n"
#         f"Prize: {stake} coins will go to a random user in 15 seconds..."
#     )

#     # Wait 15 seconds
#     await asyncio.sleep(15)

#     # Get all users
#     all_users = get_all_users()
#     # Filter by users who were in this chat
#     chat_users = [
#     u for u in all_users
#     if u.get("last_chat_id") == chat_id and u["user_id"] not in ADMINS
# ]

#     if not chat_users:
#         await update.message.reply_text("❌ No users found in this chat for the raffle.")
#         return

#     # Select random winner
#     winner = random.choice(chat_users)
#     winner_id = winner["user_id"]

#     # Add prize to winner
#     update_coins(winner_id, winner["coins"] + stake)

#     # Notify winner privately
#     try:
#         await context.bot.send_message(winner_id, f"🎉 You won {stake} coins from the raffle!")
#     except:
#         pass  # user may have blocked bot or privacy settings

#     await update.message.reply_text(f"✅ Raffle ended! Winner selected.")


import asyncio
import random
from telegram import Update
from telegram.ext import ContextTypes
from db import get_all_users, update_coins
from config import ADMINS 

async def rando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Admin only
    if user_id not in ADMINS:
        await update.message.reply_text("❌ Only admins can start a raffle.")
        return

    # Parse amount
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /raffle <amount>")
        return

    await update.message.reply_text(
        f"🎟️ Raffle started!\n"
        f"🎁 Prize: {amount} coins\n"
        f"⏳ Selecting winner in 15 seconds..."
    )

    await asyncio.sleep(15)

    # Get all users EXCEPT admins
    users = [
        u for u in get_all_users()
        if u["user_id"] not in ADMINS
    ]

    if not users:
        await update.message.reply_text("❌ No eligible users in database.")
        return

    # Pick random winner
    winner = random.choice(users)
    winner_id = winner["user_id"]

    # Give prize
    update_coins(winner_id, winner["coins"] + amount)

    # Notify winner privately
    try:
        await context.bot.send_message(
            winner_id,
            f"🎉 Congratulations!\nYou won **{amount} coins** from the raffle!"
        )
    except:
        pass  # user blocked bot or never started it

    await update.message.reply_text("✅ Raffle finished! Winner has been notified privately.")
