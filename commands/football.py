import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db import get_user, update_coins
from game_state import  ACTIVE_MATCHES
JOIN_TIMEOUT = 10

CLUBS = [
    "Real Madrid",
    "Manchester City",
    "Bayern Munich",
    "Barcelona",
    "Arsenal",
    "Liverpool"
]


# ==============================
# START MATCH
# ==============================
async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in ACTIVE_MATCHES:
        await update.message.reply_text("⚠️ A match is already running.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /match <amount>")
        return

    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Amount must be positive.")
        return

    team1, team2 = random.sample(CLUBS, 2)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(team1, callback_data=f"match_{team1}")],
        [InlineKeyboardButton(team2, callback_data=f"match_{team2}")]
    ])

    msg = await update.message.reply_text(
        f"⚽ {team1} vs {team2}\n"
        f"💰 Bet: {amount} coins\n"
        f"⏳ {JOIN_TIMEOUT}s to join!",
        reply_markup=keyboard
    )

    ACTIVE_MATCHES[chat_id] = {
        "teams": (team1, team2),
        "bet": amount,
        "players": {},
        "message_id": msg.message_id
    }

    asyncio.create_task(join_timeout(context, chat_id))


# ==============================
# JOIN MATCH
# ==============================
async def join_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name

    if chat_id not in ACTIVE_MATCHES:
        return

    match = ACTIVE_MATCHES[chat_id]
    team = query.data.replace("match_", "")

    if user_id in match["players"]:
        await query.answer("You already joined.")
        return

    user = get_user(user_id)

    if not user:
        await query.answer("You need to /start first.")
        return

    if user["coins"] < match["bet"]:
        await query.answer("Not enough coins.")
        return

    match["players"][user_id] = {
        "name": username,
        "team": team
    }

    await query.message.reply_text(
        f"✅ @{username} picked {team}"
    )


# ==============================
# JOIN TIMEOUT
# ==============================
async def join_timeout(context, chat_id):
    await asyncio.sleep(JOIN_TIMEOUT)

    if chat_id not in ACTIVE_MATCHES:
        return

    match = ACTIVE_MATCHES[chat_id]

    if not match["players"]:
        await context.bot.send_message(chat_id, "❌ No players joined.")
        del ACTIVE_MATCHES[chat_id]
        return

    await simulate_match(context, chat_id)


# ==============================
# SIMULATE MATCH
# ==============================
async def simulate_match(context, chat_id):
    match = ACTIVE_MATCHES[chat_id]

    team1, team2 = match["teams"]
    bet = match["bet"]
    msg_id = match["message_id"]

    winner = random.choice([team1, team2])
    loser = team2 if winner == team1 else team1

    win_goals = random.randint(1, 3)
    lose_goals = random.randint(0, win_goals - 1)

    score = {team1: 0, team2: 0}
    final_score = {winner: win_goals, loser: lose_goals}

    # Deduct coins from players
    for user_id in match["players"]:
        user = get_user(user_id)
        update_coins(user_id, user["coins"] - bet)

    # Live score animation
    while score != final_score:
        await asyncio.sleep(2)

        for team in score:
            if score[team] < final_score[team]:
                score[team] += 1

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=f"⚽ {team1} {score[team1]} - {score[team2]} {team2}"
        )

    # Final message
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=f"🏁 FULL TIME\n⚽ {team1} {score[team1]} - {score[team2]} {team2}"
    )

    # Payout winners
    for user_id, player in match["players"].items():
        user = get_user(user_id)

        if player["team"] == winner:
            winnings = bet * 2
            new_balance = user["coins"] + winnings
            update_coins(user_id, new_balance)

            await context.bot.send_message(
                chat_id,
                f"🏆 @{player['name']} won {winnings} coins!\n"
                f"💰 New balance: {new_balance}"
            )
        else:
            new_balance = user["coins"]
            await context.bot.send_message(
                chat_id,
                f"❌ @{player['name']} lost {bet} coins.\n"
                f"💰 New balance: {new_balance}"
            )

    del ACTIVE_MATCHES[chat_id]
