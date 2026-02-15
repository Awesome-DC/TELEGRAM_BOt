import asyncio
import random
import uuid
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db import get_user, update_coins

# ==============================
# Game storage
# ==============================
MATHS_GAMES = {}
JOIN_TIMEOUT = 10  # seconds to wait for more players
MAX_PLAYERS = 10

# ==============================
# Helpers
# ==============================
def generate_question():
    a = random.randint(1, 50)
    b = random.randint(1, 50)
    op = random.choice(["+", "-", "*"])
    question = f"{a} {op} {b}"
    answer = eval(question)
    return question, answer

# ==============================
# Start maths game
# ==============================
async def maths(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /maths <bet_amount>")
        return

    bet = int(context.args[0])
    user = get_user(user_id)
    if not user or user["coins"] < bet:
        await update.message.reply_text("❌ You don't have enough coins.")
        return

    # Deduct bet immediately
    update_coins(user_id, user["coins"] - bet)

    game_id = str(uuid.uuid4())
    join_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Game", callback_data=f"mathjoin_{game_id}")]
    ])

    msg = await update.message.reply_text(
        f"🎲 @{username} started a Maths Game!\nBet: {bet} coins\nWaiting for more players... (up to {MAX_PLAYERS})",
        reply_markup=join_btn
    )

    # Initialize game
    MATHS_GAMES[game_id] = {
        "players": [username],
        "player_ids": [user_id],
        "scores": {username: 0},
        "bet": bet,
        "chat_id": update.effective_chat.id,
        "msg_id": msg.message_id,
        "joined": False,
        "questions": [],
        "current_q": 0
    }

    # Wait for players to join
    context.application.create_task(auto_start_math(game_id, context))

# ==============================
# Auto-start after join timeout
# ==============================
async def auto_start_math(game_id, context):
    await asyncio.sleep(JOIN_TIMEOUT)
    game = MATHS_GAMES.get(game_id)
    if not game:
        return

    if not game["joined"]:
        game["joined"] = True
        await ask_question(game_id, context)

# ==============================
# Join maths game
# ==============================
async def math_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    _, game_id = query.data.split("_")

    game = MATHS_GAMES.get(game_id)
    if not game:
        await query.answer("Game not found.", show_alert=True)
        return

    if game["joined"]:
        await query.answer("Game already started.", show_alert=True)
        return

    if username in game["players"]:
        await query.answer("You already joined!", show_alert=True)
        return

    if len(game["players"]) >= MAX_PLAYERS:
        await query.answer("Game is full!", show_alert=True)
        return

    user = get_user(user_id)
    if user["coins"] < game["bet"]:
        await query.answer("Not enough coins.", show_alert=True)
        return

    update_coins(user_id, user["coins"] - game["bet"])

    game["players"].append(username)
    game["player_ids"].append(user_id)
    game["scores"][username] = 0

    await context.bot.edit_message_text(
        chat_id=game["chat_id"],
        message_id=game["msg_id"],
        text=f"🎲 @{username} joined the game!\nCurrent players: {', '.join(game['players'])}\nWaiting for more or auto-start in {JOIN_TIMEOUT} seconds..."
    )

# ==============================
# Ask questions
# ==============================
async def ask_question(game_id, context):
    game = MATHS_GAMES.get(game_id)
    if not game:
        return

    num_questions = len(game["players"]) * 5
    game["questions"] = [generate_question() for _ in range(num_questions)]
    game["current_q"] = 0

    await send_next_question(game_id, context)

async def send_next_question(game_id, context):
    game = MATHS_GAMES.get(game_id)
    if not game:
        return

    if game["current_q"] >= len(game["questions"]):
        await end_math_game(game_id, context)
        return

    q_text, _ = game["questions"][game["current_q"]]
    game["current_q"] += 1

    player_list = ", ".join(game["players"])
    await context.bot.send_message(
        chat_id=game["chat_id"],
        text=f"📝 Question {game['current_q']}/{len(game['questions'])}\nPlayers: {player_list}\nSolve: {q_text}"
    )

# ==============================
# Answer handler
# ==============================
async def maths_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Find active game where user is a player
    game = None
    game_id = None
    for gid, g in MATHS_GAMES.items():
        if username in g["players"]:
            game = g
            game_id = gid
            break

    if not game:
        return  # Not in a game

    q_index = game["current_q"] - 1
    if q_index < 0:
        return

    correct_answer = game["questions"][q_index][1]
    try:
        if float(text) == correct_answer:
            game["scores"][username] += 1
            await update.message.reply_text(f"✅ Correct, @{username}!")
        else:
            await update.message.reply_text(f"❌ Wrong, @{username}. Correct was {correct_answer}")
    except ValueError:
        await update.message.reply_text(f"❌ Invalid answer, @{username}.")

    await send_next_question(game_id, context)

# ==============================
# End game
# ==============================
async def end_math_game(game_id, context):
    game = MATHS_GAMES.get(game_id)
    if not game:
        return

    text = "🏁 Game Over!\n\n"
    for username in game["players"]:
        score = game["scores"].get(username, 0)
        coins_won = score * game["bet"]
        index = game["players"].index(username)
        user_id = game["player_ids"][index]
        if user_id:
            user = get_user(user_id)
            update_coins(user_id, user["coins"] + coins_won)
        text += f"@{username}: {score} correct → {coins_won} coins\n"

    await context.bot.send_message(chat_id=game["chat_id"], text=text)

    del MATHS_GAMES[game_id]

# import asyncio
# import random
# import uuid
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import ContextTypes
# from db import get_user, update_coins

# MATHS_GAMES = {}
# JOIN_TIMEOUT = 15  # seconds to allow players to join

# # -----------------------------
# # Helpers
# # -----------------------------
# def generate_question():
#     a = random.randint(1, 20)
#     b = random.randint(1, 20)
#     op = random.choice(["+", "-", "*"])
#     question = f"{a} {op} {b}"
#     answer = eval(question)
#     return question, answer

# def generate_questions(num):
#     return [generate_question() for _ in range(num)]

# # -----------------------------
# # /maths command
# # -----------------------------
# async def maths(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user = get_user(update.effective_user.id)
#     if not user:
#         await update.message.reply_text("❌ You are not registered.")
#         return

#     if not context.args or not context.args[0].isdigit():
#         await update.message.reply_text("Usage: /maths <bet_amount>")
#         return

#     bet = int(context.args[0])
#     if user["coins"] < bet:
#         await update.message.reply_text(f"❌ Not enough coins. You have {user['coins']}")
#         return

#     update_coins(user["user_id"], user["coins"] - bet)

#     username = update.effective_user.username or update.effective_user.first_name
#     game_id = str(uuid.uuid4())

#     # Number of questions depends on max players
#     max_players = 10
#     num_questions = 5  # base number, can scale
#     questions = generate_questions(num_questions)

#     join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Join Game", callback_data=f"mathjoin_{game_id}")]])
#     msg = await update.message.reply_text(
#         f"🧮 @{username} started a Maths Game!\nBet: {bet} coins\nWaiting for players to join...\nMax: {max_players} players",
#         reply_markup=join_btn
#     )

#     MATHS_GAMES[game_id] = {
#         "players": [username],
#         "player_ids": [update.effective_user.id],
#         "answers": {username: 0},
#         "bet": bet,
#         "current_question": 0,
#         "questions": questions,
#         "max_players": max_players,
#         "joined": False,
#         "msg_id": msg.message_id,
#         "chat_id": msg.chat_id
#     }

#     # Wait for players to join
#     asyncio.create_task(wait_for_players(game_id, context))

# # -----------------------------
# # Wait for players
# # -----------------------------
# async def wait_for_players(game_id, context):
#     await asyncio.sleep(JOIN_TIMEOUT)
#     game = MATHS_GAMES.get(game_id)
#     if not game:
#         return

#     game["joined"] = True
#     await ask_question(game_id, context)

# # -----------------------------
# # Player Join Callback
# # -----------------------------
# async def maths_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     username = update.effective_user.username or update.effective_user.first_name
#     user_id = update.effective_user.id

#     _, game_id = query.data.split("_")
#     game = MATHS_GAMES.get(game_id)
#     if not game or game["joined"]:
#         await query.answer("Game already started!", show_alert=True)
#         return

#     if username in game["players"]:
#         await query.answer("❌ You already joined!", show_alert=True)
#         return

#     if len(game["players"]) >= game["max_players"]:
#         await query.answer("❌ Game is full!", show_alert=True)
#         return

#     user = get_user(user_id)
#     if user["coins"] < game["bet"]:
#         await query.answer("❌ Not enough coins!", show_alert=True)
#         return

#     update_coins(user_id, user["coins"] - game["bet"])

#     game["players"].append(username)
#     game["player_ids"].append(user_id)
#     game["answers"][username] = 0

#     await query.edit_message_text(
#         f"✅ @{username} joined the Maths Game!\nPlayers: {', '.join(game['players'])}"
#     )

# # -----------------------------
# # Ask Question
# # -----------------------------
# async def ask_question(game_id, context):
#     game = MATHS_GAMES[game_id]
#     if game["current_question"] >= len(game["questions"]):
#         # Game over
#         await end_game(game_id, context)
#         return

#     question, answer = game["questions"][game["current_question"]]
#     game["current_answer"] = answer
#     game["current_question"] += 1

#     players_text = ", ".join(game["players"])
#     msg_text = f"🧮 Question {game['current_question']} for players: {players_text}\n\n{question}"
#     await context.bot.send_message(chat_id=game["chat_id"], text=msg_text)

# # -----------------------------
# # Answer Handler
# # -----------------------------
# async def maths_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     username = update.effective_user.username or update.effective_user.first_name
#     text = update.message.text.strip()

#     # Find the game the player is in
#     game = None
#     for g in MATHS_GAMES.values():
#         if username in g["players"] and g["joined"]:
#             game = g
#             break
#     if not game:
#         return

#     try:
#         user_answer = int(text)
#     except:
#         await update.message.reply_text("❌ Answer must be a number!")
#         return

#     if user_answer == game["current_answer"]:
#         game["answers"][username] += 1
#         await update.message.reply_text(f"✅ @{username} answered correctly! Total correct: {game['answers'][username]}")
#     else:
#         await update.message.reply_text(f"❌ @{username} answered incorrectly.")

#     # Move to next question if all players answered
#     # Here we could wait for all players, for simplicity, we move on automatically
#     await ask_question(game_id=list(MATHS_GAMES.keys())[list(MATHS_GAMES.values()).index(game)], context=context)

# # -----------------------------
# # End Game
# # -----------------------------
# async def end_game(game_id, context):
#     game = MATHS_GAMES[game_id]

#     # Determine winner(s)
#     max_score = max(game["answers"].values())
#     winners = [u for u, score in game["answers"].items() if score == max_score]

#     # Pay coins
#     for u in winners:
#         idx = game["players"].index(u)
#         user_id = game["player_ids"][idx]
#         if user_id:
#             user = get_user(user_id)
#             update_coins(user_id, user["coins"] + game["bet"] * 2)  # double bet

#     winner_text = ", ".join([f"@{w}" for w in winners])
#     await context.bot.send_message(
#         chat_id=game["chat_id"],
#         text=f"🏆 Game over!\n\nWinner(s): {winner_text}\nScores: {game['answers']}"
#     )

#     del MATHS_GAMES[game_id]
