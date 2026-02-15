from telegram import Update
from telegram.ext import ContextTypes
from db import get_all_users

TOP_LIMIT = 10  # show top 10 users

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_users = get_all_users()
    if not all_users:
        await update.message.reply_text("No users found in the database yet.")
        return

    # Sort users by coins descending
    sorted_users = sorted(all_users, key=lambda x: x["coins"], reverse=True)

    top_users = sorted_users[:TOP_LIMIT]

    leaderboard = "🏆 Top Users:\n"
    medals = ["🥇", "🥈", "🥉"]  # first 3 special
    for i, user in enumerate(top_users):
        rank_emoji = medals[i] if i < 3 else f"{i+1}️⃣"
        name = user["username"] if user["username"] else str(user["user_id"])
        leaderboard += f"{rank_emoji} {name} — {user['coins']} coins\n"

    await update.message.reply_text(leaderboard)
