import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from db import get_user, update_coins

# Active mine games per chat
active_mine_games = {}  # game_id: {group_chat_id, stake, grid, opened, user_id, temp_coins}

GRID_SIZE = 5  # 5x5
BOMB = "💣"
SAFE = "🟩"

# -----------------------------
# Helper: generate mine grid
# -----------------------------
def generate_grid(bomb_count):
    grid = [[SAFE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    bombs_placed = 0
    while bombs_placed < bomb_count:
        r = random.randint(0, GRID_SIZE - 1)
        c = random.randint(0, GRID_SIZE - 1)
        if grid[r][c] != BOMB:
            grid[r][c] = BOMB
            bombs_placed += 1
    return grid

# -----------------------------
# Helper: create inline buttons
# -----------------------------
def make_grid_keyboard(game):
    buttons = []
    for r in range(GRID_SIZE):
        row = []
        for c in range(GRID_SIZE):
            if (r, c) in game["opened"]:
                # Show opened cell
                row.append(InlineKeyboardButton(game["grid"][r][c], callback_data="none"))
            else:
                row.append(InlineKeyboardButton("⬜", callback_data=f"mine_{r}_{c}"))
        buttons.append(row)
    # Add cashout button at bottom
    buttons.append([InlineKeyboardButton("💰 Cashout", callback_data="mine_cashout")])
    return InlineKeyboardMarkup(buttons)

# -----------------------------
# /mine command
# -----------------------------
async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("❌ You need to /start first!")
        return

    try:
        stake = int(context.args[0])
        bomb_count = int(context.args[1])
        if stake <= 0 or bomb_count < 1 or bomb_count > GRID_SIZE * GRID_SIZE - 1:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /mine <stake> <bombs> (bombs 1–24)")
        return

    if user["coins"] < stake:
        await update.message.reply_text(f"❌ You only have {user['coins']} coins.")
        return

    # Deduct stake
    update_coins(user_id, user["coins"] - stake)

    # Generate grid
    grid = generate_grid(bomb_count)

    # Save game
    active_mine_games[user_id] = {
        "group_chat_id": chat_id,
        "stake": stake,
        "grid": grid,
        "opened": {},
        "user_id": user_id,
        "temp_coins": stake
    }

    # Send initial grid
    await update.message.reply_text(
        f"🎮 {update.effective_user.full_name} started a Mine game!\n"
        f"Stake: {stake} coins | Bombs: {bomb_count}\n"
        "Click a cell to open it or cash out at any time.",
        reply_markup=make_grid_keyboard(active_mine_games[user_id])
    )

# -----------------------------
# Callback for mine button clicks
# -----------------------------
async def mine_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if user_id not in active_mine_games:
        await query.answer("❌ No active /mine game found.")
        return

    game = active_mine_games[user_id]

    # Cashout
    if data == "mine_cashout":
        coins = game["temp_coins"]
        update_coins(user_id, get_user(user_id)["coins"] + coins)
        await query.message.edit_text(f"💰 You cashed out {coins} coins!")
        del active_mine_games[user_id]
        return

    # Parse row/col
    try:
        _, r, c = data.split("_")
        r, c = int(r), int(c)
    except:
        await query.answer("❌ Invalid button.")
        return

    if (r, c) in game["opened"]:
        await query.answer("❌ Already opened!")
        return

    game["opened"][(r, c)] = True

    # Check bomb
    if game["grid"][r][c] == BOMB:
        await query.message.edit_text(
            f"💥 Boom! You hit a bomb at ({r+1},{c+1}). You lost your stake."
        )
        del active_mine_games[user_id]
        return
    else:
        # Increase temp coins slightly for each safe cell (example multiplier)
        game["temp_coins"] = int(game["temp_coins"] * 1.2)
        await query.answer("✅ Safe! Continue or cash out.")
        # Update grid display
        await query.message.edit_text(
            f"🎮 Your Mine game (Stake: {game['stake']} coins)\n"
            f"Temp coins: {game['temp_coins']}\n"
            "Click a cell to open it or cash out.",
            reply_markup=make_grid_keyboard(game)
        )
