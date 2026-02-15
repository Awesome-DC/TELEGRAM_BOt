# import asyncio
# import random
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
# from db import get_user, update_coins

# # Active imposter games per chat
# active_imposter_games = {}  # chat_id: {stake, participants, imposter, guesses, timeout_task}

# MIN_PLAYERS = 3
# JOIN_TIMEOUT = 15  # seconds

# # -----------------------------
# # /imposter command
# # -----------------------------
# async def imposter(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.effective_chat.id
#     user_id = update.effective_user.id
#     user = get_user(user_id)

#     if not user:
#         await update.message.reply_text("❌ You need to /start first!")
#         return

#     # Parse stake
#     try:
#         stake = int(context.args[0])
#         if stake <= 0:
#             raise ValueError
#     except (IndexError, ValueError):
#         await update.message.reply_text("Usage: /imposter <stake>")
#         return

#     if user["coins"] < stake:
#         await update.message.reply_text(f"❌ You only have {user['coins']} coins.")
#         return

#     if chat_id in active_imposter_games:
#         await update.message.reply_text("❌ A game is already active in this chat.")
#         return

#     # Deduct stake from creator temporarily (will be refunded if game fails)
#     update_coins(user_id, user["coins"] - stake)

#     # Initialize game state
#     active_imposter_games[chat_id] = {
#         "stake": stake,
#         "participants": [user_id],
#         "imposter": None,
#         "guesses": {}
#     }

#     await update.message.reply_text(
#         f"🎮 Imposter game started by {update.effective_user.full_name}!\n"
#         f"Stake: {stake} coins\n"
#         f"Others have {JOIN_TIMEOUT} seconds to join using /ijoin"
#     )

#     # Start join timeout
#     async def resolve_game():
#         await asyncio.sleep(JOIN_TIMEOUT)
#         game = active_imposter_games.get(chat_id)
#         if not game:
#             return

#         participants = game["participants"]

#         # Check minimum players
#         if len(participants) < MIN_PLAYERS:
#             # Refund stakes
#             for pid in participants:
#                 player = get_user(pid)
#                 update_coins(pid, player["coins"] + stake)
#             await context.bot.send_message(chat_id, "❌ Not enough players joined. Stakes refunded.")
#             del active_imposter_games[chat_id]
#             return

#         # Pick random imposter
#         imposter_id = random.choice(participants)
#         game["imposter"] = imposter_id

#         # Send role DMs
#         for pid in participants:
#             try:
#                 if pid == imposter_id:
#                     await context.bot.send_message(pid, "💀 You are the imposter!")
#                 else:
#                     await context.bot.send_message(pid, "✅ You are not the imposter!")
#             except:
#                 pass  # user may have blocked bot or privacy settings

#         # Send group message to start guessing
#         buttons = [
#             [InlineKeyboardButton(get_user(pid)["username"] or str(pid), callback_data=f"guess_{pid}")]
#             for pid in participants
#         ]
#         keyboard = InlineKeyboardMarkup([buttons])

#         await context.bot.send_message(
#             chat_id,
#             "🕵️ Guess who the imposter is by clicking the button below:",
#             reply_markup=keyboard
#         )

#     # Schedule resolve after join timeout
#     asyncio.create_task(resolve_game())


# # -----------------------------
# # /ijoin command
# # -----------------------------
# async def ijoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.effective_chat.id
#     user_id = update.effective_user.id
#     user = get_user(user_id)

#     if not user:
#         await update.message.reply_text("❌ You need to /start first!")
#         return

#     if chat_id not in active_imposter_games:
#         await update.message.reply_text("❌ No active imposter game to join.")
#         return

#     game = active_imposter_games[chat_id]

#     if user_id in game["participants"]:
#         await update.message.reply_text("❌ You already joined the game.")
#         return

#     if user["coins"] < game["stake"]:
#         await update.message.reply_text(f"❌ You only have {user['coins']} coins.")
#         return

#     # Deduct stake from joiner
#     update_coins(user_id, user["coins"] - game["stake"])
#     game["participants"].append(user_id)

#     await update.message.reply_text(f"✅ {update.effective_user.full_name} joined the imposter game!")


# # -----------------------------
# # Callback handler for guessing
# # -----------------------------
# async def imposter_guess_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     user_id = query.from_user.id
#     chat_id = query.message.chat.id
#     data = query.data

#     if chat_id not in active_imposter_games:
#         await query.answer("❌ No active game in this chat.")
#         return

#     game = active_imposter_games[chat_id]

#     if user_id not in game["participants"]:
#         await query.answer("❌ You are not part of this game.")
#         return

#     if data.startswith("guess_"):
#         guessed_id = int(data.split("_")[1])

#         if user_id in game["guesses"]:
#             await query.answer("❌ You already guessed!")
#             return

#         game["guesses"][user_id] = guessed_id
#         await query.answer("✅ Guess registered!")

#         # Check if all participants (except imposter) have guessed
#         if len(game["guesses"]) >= len(game["participants"]) - 1:
#             # Resolve game
#             imposter_id = game["imposter"]
#             stake = game["stake"]
#             participants = game["participants"]
#             total_pot = stake * len(participants)

#             # Find correct guessers
#             correct_guessers = [
#                 pid for pid, guess in game["guesses"].items() if guess == imposter_id
#             ]

#             # Compute payouts
#             if len(correct_guessers) == 0:
#                 # Nobody guessed → imposter wins full pot
#                 winner_id = imposter_id
#                 new_balance = get_user(winner_id)["coins"] + total_pot
#                 update_coins(winner_id, new_balance)
#                 result_msg = f"💀 Nobody guessed the imposter. Imposter {get_user(imposter_id)['username'] or imposter_id} wins {total_pot} coins!"
#             else:
#                 # Correct guessers split pot
#                 split_amount = total_pot // len(correct_guessers)
#                 for pid in correct_guessers:
#                     user = get_user(pid)
#                     update_coins(pid, user["coins"] + split_amount)
#                 winners = ", ".join([get_user(pid)["username"] or str(pid) for pid in correct_guessers])
#                 result_msg = f"✅ Correct guessers: {winners} split {total_pot} coins! Each gets {split_amount} coins."

#             await query.message.reply_text(result_msg)
#             del active_imposter_games[chat_id]


import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from db import get_user, update_coins

# Active imposter games per chat
active_imposter_games = {}  # chat_id: {stake, participants, imposter, guesses, timeout_task}

MIN_PLAYERS = 3
JOIN_TIMEOUT = 15  # seconds

# -----------------------------
# Helper to create guess keyboard (2–3 buttons per row)
# -----------------------------
def make_guess_keyboard(participants):
    buttons = []
    row = []
    for i, pid in enumerate(participants, 1):
        row.append(InlineKeyboardButton(get_user(pid)["username"] or str(pid), callback_data=f"guess_{pid}"))
        if i % 3 == 0:  # 3 buttons per row
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

# -----------------------------
# /imposter command
# -----------------------------
async def imposter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("❌ You need to /start first!")
        return

    # Parse stake
    try:
        stake = int(context.args[0])
        if stake <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /imposter <stake>")
        return

    if user["coins"] < stake:
        await update.message.reply_text(f"❌ You only have {user['coins']} coins.")
        return

    if chat_id in active_imposter_games:
        await update.message.reply_text("❌ A game is already active in this chat.")
        return

    # Deduct stake from creator temporarily
    update_coins(user_id, user["coins"] - stake)

    # Initialize game state
    active_imposter_games[chat_id] = {
        "stake": stake,
        "participants": [user_id],
        "imposter": None,
        "guesses": {}
    }

    await update.message.reply_text(
        f"🎮 Imposter game started by {update.effective_user.full_name}!\n"
        f"Stake: {stake} coins\n"
        f"Others have {JOIN_TIMEOUT} seconds to join using /ijoin"
    )

    # Start join timeout
    async def resolve_game():
        await asyncio.sleep(JOIN_TIMEOUT)
        game = active_imposter_games.get(chat_id)
        if not game:
            return

        participants = game["participants"]

        # Check minimum players
        if len(participants) < MIN_PLAYERS:
            # Refund stakes
            for pid in participants:
                player = get_user(pid)
                update_coins(pid, player["coins"] + stake)
            await context.bot.send_message(chat_id, "❌ Not enough players joined. Stakes refunded.")
            del active_imposter_games[chat_id]
            return

        # Pick random imposter
        imposter_id = random.choice(participants)
        game["imposter"] = imposter_id

        # Send role DMs
        for pid in participants:
            try:
                if pid == imposter_id:
                    await context.bot.send_message(pid, "💀 You are the imposter!")
                else:
                    await context.bot.send_message(pid, "✅ You are not the imposter!")
            except:
                pass  # user may have blocked bot or privacy settings

        # Send group message to start guessing
        keyboard = make_guess_keyboard(participants)

        await context.bot.send_message(
            chat_id,
            "🕵️ Guess who the imposter is by clicking the button below:",
            reply_markup=keyboard
        )

    # Schedule resolve after join timeout
    asyncio.create_task(resolve_game())


# -----------------------------
# /ijoin command
# -----------------------------
async def ijoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("❌ You need to /start first!")
        return

    if chat_id not in active_imposter_games:
        await update.message.reply_text("❌ No active imposter game to join.")
        return

    game = active_imposter_games[chat_id]

    if user_id in game["participants"]:
        await update.message.reply_text("❌ You already joined the game.")
        return

    if user["coins"] < game["stake"]:
        await update.message.reply_text(f"❌ You only have {user['coins']} coins.")
        return

    # Deduct stake from joiner
    update_coins(user_id, user["coins"] - game["stake"])
    game["participants"].append(user_id)

    await update.message.reply_text(f"✅ {update.effective_user.full_name} joined the imposter game!")


# -----------------------------
# Callback handler for guessing
# -----------------------------
async def imposter_guess_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data

    if chat_id not in active_imposter_games:
        await query.answer("❌ No active game in this chat.")
        return

    game = active_imposter_games[chat_id]

    if user_id not in game["participants"]:
        await query.answer("❌ You are not part of this game.")
        return

    if data.startswith("guess_"):
        guessed_id = int(data.split("_")[1])

        if user_id in game["guesses"]:
            await query.answer("❌ You already guessed!")
            return

        game["guesses"][user_id] = guessed_id
        await query.answer("✅ Guess registered!")

        # Check if all participants (except imposter) have guessed
        if len(game["guesses"]) >= len(game["participants"]) - 1:
            # Resolve game
            imposter_id = game["imposter"]
            stake = game["stake"]
            participants = game["participants"]
            total_pot = stake * len(participants)

            # Find correct guessers
            correct_guessers = [
                pid for pid, guess in game["guesses"].items() if guess == imposter_id
            ]

            # Compute payouts
            if len(correct_guessers) == 0:
                # Nobody guessed → imposter wins full pot
                winner_id = imposter_id
                new_balance = get_user(winner_id)["coins"] + total_pot
                update_coins(winner_id, new_balance)
                result_msg = f"💀 Nobody guessed the imposter. Imposter {get_user(imposter_id)['username'] or imposter_id} wins {total_pot} coins!"
            else:
                # Correct guessers split pot
                split_amount = total_pot // len(correct_guessers)
                for pid in correct_guessers:
                    user = get_user(pid)
                    update_coins(pid, user["coins"] + split_amount)
                winners = ", ".join([get_user(pid)["username"] or str(pid) for pid in correct_guessers])
                result_msg = f"✅ Correct guessers: {winners} split {total_pot} coins! Each gets {split_amount} coins."

            await query.message.reply_text(result_msg)
            del active_imposter_games[chat_id]
