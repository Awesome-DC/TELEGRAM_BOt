import asyncio
import random
import uuid
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db import get_user, update_coins

TTT_GAMES = {}
JOIN_TIMEOUT = 10


# ==============================
# Helpers
# ==============================

def board_to_text(board):
    return "\n".join([" | ".join(row) for row in board])


def generate_board_buttons(game_id):
    game = TTT_GAMES[game_id]
    buttons = []

    for i in range(3):
        row = []
        for j in range(3):
            cell = game["board"][i][j]
            label = cell if cell != " " else " "
            row.append(
                InlineKeyboardButton(
                    label,
                    callback_data=f"tttmove_{game_id}_{i}_{j}"
                )
            )
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)


# ==============================
# Start Game
# ==============================
async def auto_bot_join(game_id, context):
    await asyncio.sleep(JOIN_TIMEOUT)

    game = TTT_GAMES.get(game_id)
    if not game:
        return

    if game["joined"] is False:
        game["players"].append("BOT")
        game["player_ids"].append(None)
        game["joined"] = True
        await edit_board(game_id, context)

async def ttt(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /ttt <amount>")
        return

    bet = int(context.args[0])
    user = get_user(user_id)

    if user["coins"] < bet:
        await update.message.reply_text("Not enough coins.")
        return

    update_coins(user_id, user["coins"] - bet)

    game_id = str(uuid.uuid4())

    join_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Game", callback_data=f"tjoin_{game_id}")]
    ])

    msg = await update.message.reply_text(
        f"🎮 @{username} started Tic-Tac-Toe\nBet: {bet}\nWaiting for player...",
        reply_markup=join_btn
    )

    TTT_GAMES[game_id] = {
        "players": [username],
        "player_ids": [user_id],
        "bet": bet,
        "board": [[" "] * 3 for _ in range(3)],
        "turn": 0,  # 0 = player1, 1 = player2
        "joined": False,
        "chat_id": msg.chat_id,
        "msg_id": msg.message_id
    }

    context.application.create_task(auto_bot_join(game_id, context))


# ==============================
# Join Game
# ==============================

async def ttt_join_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    _, game_id = query.data.split("_")
    game = TTT_GAMES.get(game_id)

    if not game or game["joined"]:
        await query.answer("Game already started.", show_alert=True)
        return

    user = get_user(user_id)
    if user["coins"] < game["bet"]:
        await query.answer("Not enough coins.", show_alert=True)
        return

    update_coins(user_id, user["coins"] - game["bet"])

    game["players"].append(username)
    game["player_ids"].append(user_id)
    game["joined"] = True

    await edit_board(game_id, context)


# ==============================
# Player Move
# ==============================

async def ttt_move_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    _, game_id, r, c = query.data.split("_")
    r, c = int(r), int(c)

    game = TTT_GAMES.get(game_id)
    if not game:
        return

    current_turn = game["turn"]

    # Only correct player can move
    if user_id != game["player_ids"][current_turn]:
        await query.answer("Not your turn!", show_alert=True)
        return

    if game["board"][r][c] != " ":
        await query.answer("Cell taken!", show_alert=True)
        return

    mark = "X" if current_turn == 0 else "O"
    game["board"][r][c] = mark

    await check_winner_or_continue(game_id, context)


# ==============================
# Bot Move
# ==============================

async def bot_move(game_id, context):
    game = TTT_GAMES[game_id]

    empty = [(i, j) for i in range(3)
             for j in range(3)
             if game["board"][i][j] == " "]

    if empty:
        r, c = random.choice(empty)
        game["board"][r][c] = "O"

    await check_winner_or_continue(game_id, context)


# ==============================
# Edit Board
# ==============================

async def edit_board(game_id, context, text=None):
    game = TTT_GAMES[game_id]

    display_text = text or (
        f"🎮 Tic-Tac-Toe\n"
        f"Turn: @{game['players'][game['turn']]}\n\n"
        f"{board_to_text(game['board'])}"
    )

    await context.bot.edit_message_text(
        chat_id=game["chat_id"],
        message_id=game["msg_id"],
        text=display_text,
        reply_markup=generate_board_buttons(game_id)
    )


# ==============================
# Check Winner
# ==============================

def check_winner(board):
    lines = board + list(zip(*board)) + [
        [board[i][i] for i in range(3)],
        [board[i][2 - i] for i in range(3)]
    ]

    for line in lines:
        if line[0] != " " and line.count(line[0]) == 3:
            return line[0]

    if all(cell != " " for row in board for cell in row):
        return "Draw"

    return None


# ==============================
# Winner / Continue
# ==============================

async def check_winner_or_continue(game_id, context):
    game = TTT_GAMES[game_id]
    winner = check_winner(game["board"])
    bet = game["bet"]

    if winner:
        if winner == "Draw":
            text = f"🤝 Draw!\n\n{board_to_text(game['board'])}"
        else:
            winner_index = 0 if winner == "X" else 1
            winner_id = game["player_ids"][winner_index]
            winner_name = game["players"][winner_index]

            if winner_id:
                user = get_user(winner_id)
                update_coins(winner_id, user["coins"] + bet * 2)

            text = (
                f"🏆 @{winner_name} wins!\n"
                f"💰 Coins won: {bet * 2}\n\n"
                f"{board_to_text(game['board'])}"
            )

        # REMOVE BUTTONS HERE
        await context.bot.edit_message_text(
            chat_id=game["chat_id"],
            message_id=game["msg_id"],
            text=text
        )

        del TTT_GAMES[game_id]
        return

    # Switch turn
    game["turn"] = 1 if game["turn"] == 0 else 0

    # If bot turn
    if game["players"][game["turn"]] == "BOT":
        await bot_move(game_id, context)
    else:
        await edit_board(game_id, context)
