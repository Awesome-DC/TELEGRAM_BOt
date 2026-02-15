# import random
# from telegram import Update
# from telegram.ext import ContextTypes
# from db import get_user, update_coins

# FRUITS = ["🍎", "🍌", "🍒", "🍇"]
# MULTIPLIER = 2  # 3 matching fruits doubles the stake

# async def stake(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     user = get_user(user_id)

#     if not user:
#         await update.message.reply_text("❌ You need to /start first!")
#         return

#     # Parse stake amount
#     try:
#         amount = int(context.args[0])
#         if amount <= 0:
#             raise ValueError
#     except (IndexError, ValueError):
#         await update.message.reply_text("Usage: /stake <amount> (must be a positive number)")
#         return

#     # Check if user has enough coins
#     if user["coins"] < amount:
#         await update.message.reply_text(f"❌ insufficient balance")
#         return

#     # Deduct stake
#     new_balance = user["coins"] - amount
#     update_coins(user_id, new_balance)

#     # Spin 3 fruits
#     spin_result = [random.choice(FRUITS) for _ in range(3)]

#     # Check if all 3 match
#     if spin_result[0] == spin_result[1] == spin_result[2]:
#         winnings = amount * MULTIPLIER
#         new_balance += winnings
#         update_coins(user_id, new_balance)
#         reply = (
#             f"🎰 You staked {amount} coins!\n"
#             f"Spin Result:\n{' | '.join(spin_result)}\n"
#             f"🎉 JACKPOT! You win {winnings} coins!\n"
#             f"💰 Your new balance: {new_balance} coins"
#         )
#     else:
#         reply = (
#             f"🎰 You staked {amount} coins!\n"
#             f"Spin Result:\n{' | '.join(spin_result)}\n"
#             f"❌ No match, you lost {amount} coins.\n"
#             f"💰 Your new balance: {new_balance} coins"
#         )

#     await update.message.reply_text(reply)


import random
from collections import Counter
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, update_coins

FRUITS = ["🍎", "🍌", "🍒", "🍇"]

async def stake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("❌ You need to /start first!")
        return

    # Parse stake amount
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /stake <amount> (must be a positive number)")
        return

    # Check if user has enough coins
    if user["coins"] < amount:
        await update.message.reply_text(f"❌ You only have {user['coins']} coins. Cannot stake {amount}.")
        return

    # Deduct stake first
    new_balance = user["coins"] - amount
    update_coins(user_id, new_balance)

    # Spin 3 fruits
    spin_result = [random.choice(FRUITS) for _ in range(3)]
    counts = Counter(spin_result)

    multiplier = 0
    for fruit, count in counts.items():
        if count == 3:
            multiplier = 3
            break
        elif count == 2:
            multiplier = 2

    # Calculate winnings
    if multiplier > 0:
        winnings = amount * multiplier
        new_balance += winnings
        update_coins(user_id, new_balance)
        reply = (
            f"🎰 You staked {amount} coins!\n"
            f"Spin Result:\n{' | '.join(spin_result)}\n"
            f"🎉 You win x{multiplier}! You earned {winnings} coins!\n"
            f"💰 New balance: {new_balance} coins"
        )
    else:
        reply = (
            f"🎰 You staked {amount} coins!\n"
            f"Spin Result:\n{' | '.join(spin_result)}\n"
            f"❌ No match, you lost {amount} coins.\n"
            f"💰 New balance: {new_balance} coins"
        )

    await update.message.reply_text(reply)
