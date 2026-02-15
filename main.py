from commands.beg import beg
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, filters, ContextTypes, CallbackQueryHandler, MessageHandler
from db import create_tables, add_user, get_user, create_redeem_table
from commands.stake import stake
from commands.football import match, join_match
from commands.math import maths,maths_answer,math_join_callback
from commands.broad import broadcast
from commands.balance import balance
from game_state import ACTIVE_MATCHES
from commands.add import add, addall 
from config import TOKEN, ADMINS, GROUP_CHAT_ID
from commands.ur import ur, urall, resetall
from backup import backup_db
from commands.top import top
from commands.ttt import ttt, ttt_join_callback,ttt_move_callback
from commands.ai import ai_command
from commands.evenodd import evenodd
from commands.give import give
from commands.design import design_screen, clear_console
from commands.mine import mine, mine_callback
from commands.bet import bet, join
from commands.profile import profile
from commands.random import rando
from commands.redeem import redeem, redeem_callback
from commands.raffle import giveaway, rjoin
from commands.imposter import imposter, ijoin, imposter_guess_callback
from commands.code import fd, code
import sys
import asyncio
# 1️⃣ Create tables at startup
create_tables()
create_redeem_table()


# Fix Windows Python 3.12 event loop issues
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# 2️⃣ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

# Check if user is already a member of the group
    try:
        member = await context.bot.get_chat_member(GROUP_CHAT_ID, user_id)
        if member.status in ["left", "kicked"]:
            # Not joined
            await update.message.reply_text(
                f"❌ You must join our group first before using the bot.\n"
                f"Join here: https://t.me/+VBIKY4Y9bAQyZDU0"
            )
            return
    except:
        # User not found in group
        await update.message.reply_text(
            f"❌ You must join our group first before using the bot.\n"
            f"Join here: https://t.me/+VBIKY4Y9bAQyZDU0"
        )
        return
    # Add user if not exists, start with 0 coins
    add_user(user_id, username, starter_coins=0)

    user = get_user(user_id)
    coins = user["coins"]
    text = ""
    
    if user_id in ADMINS:
        text += (
               f"👋 Hello {update.effective_user.first_name}, welcome Back\n\n"
                "COMMANDS:\n"
                "/balance - Check your credits\n"
                "/give <user_id> <amount> - Give credits to someone\n"
                "/top - leaderboard\n"
                "/profile - check profile\n"
                "/AI - get ai response\n"
        "\n"
                "GAMES\n"
                "/maths <amount> - play maths game\n"
                "/evenodd <amount> <even/odd> - Play Even or Odd game\n"
                "/mine <amount> - Mine game\n"
                "/ttt <amount> - play tik tak toe\n"
                "/beg - Beg for random credits\n"
                "/stake <amount>/all - play casino game\n"
                "/bet <amount> - bet\n"
            
                "/match <amount> - play match bet\n"
                "/join - join any opened game\n"
                "/imposter <amount> - imposter game\n"
                "/ijoin - join the current imposter game\n"
        "\n"
                "ADMINS OMLY\n"
                "/create <amount> <number> - code\n"
                "/raffle <amount> - raffle draw\n"
                "/random <amount> - give coin randomly\n"
                "/add <amount> -  Add credits\n"
                "/addall <amount> -  Add credits to all\n"
                "/broadcast <text> - send message to all user"
                "/ur - remove credits\n"
                "/urall <amount> -  remove credits from all\n"
                "/reset - reset credits\n"
                )
    # Base menu for normal users
    else:
        text = (
        f"👋 Hello {update.effective_user.first_name}, welcome to normans game bot!\n\n"
        "COMMANDS:\n"
        "/balance - Check your credits\n"
        "/give <user_id> <amount> - Give credits to someone\n"
        "/top - leaderboard\n"
        "/profile - check profile\n"
        "/code <code> - redeem code\n"
        "/AI - get ai response\n"
"\n"
        "GAMES\n"
        "/maths <amount> - play maths game\n"
        "/ttt <amount> - play tik tak toe\n"
        "/evenodd <amount> <even/odd> - Play Even or Odd game\n"
        "/mine <amount> - Mine game\n"
        "/match <amount> - play match bet\n"
        "/beg - Beg for random credits\n"
        "/stake <amount>/all - play casino game\n"
        "/crash <amount> - play aviator(in construction)\n"
        "/bet <amount> - bet with friends\n"
        "/join - join any opened game\n"
        "/imposter <amount> - imposter game\n"
        "/ijoin - join the current imposter game\n"
        "/rjoin - Join active giveaway\n"
        "\n"
        "REDEEM\n"
        "/redeem\n\n"
        "made by @BEC_KY2\n"
    )

    await update.message.reply_text(text)

async def send_startup_message(app):
    try:
        await app.bot.send_message(
            chat_id=ADMINS[0],
            text="🤖 Bot is now running!"
        )
        # Set dynamic status under bot name
        await app.bot.set_my_short_description(
            short_description="🎮 Normans Game Bot - Ready to play!"
        )
    except Exception as e:
        print("Startup message failed:", e)

# 4️⃣ Bot setup
# def main():
#     app = ApplicationBuilder().token(TOKEN).build()
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CommandHandler("stake", stake))
#     app.add_handler(CommandHandler("beg", beg))
#     app.add_handler(CommandHandler("broadcast", broadcast))
#     app.add_handler(CommandHandler("backup", backup_db))
#     app.add_handler(CommandHandler("mine", mine))
#     app.add_handler(CallbackQueryHandler(mine_callback, pattern=r'^mine_'))
#     app.add_handler(CommandHandler("give", give))
#     app.add_handler(CommandHandler("profile", profile))
#     app.add_handler(CommandHandler("balance", balance))
#     app.add_handler(CommandHandler("add", add))
#     app.add_handler(CommandHandler("evenodd", evenodd))
#     app.add_handler(CommandHandler("top", top))
#     app.add_handler(CommandHandler("addall", addall))
#     app.add_handler(CommandHandler("random", rando))
#     app.add_handler(CommandHandler("bet", bet))
#     app.add_handler(CommandHandler("redeem", redeem))
#     app.add_handler(CommandHandler("reset", resetall))
#     app.add_handler(CommandHandler("join", join))
#     app.add_handler(CommandHandler("maths", maths))
#     app.add_handler(CallbackQueryHandler(math_join_callback, pattern=r"^mathjoin_"))
#     app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), maths_answer))
#     app.add_handler(CommandHandler("create", fd))
#     app.add_handler(CommandHandler("code", code))
#     app.add_handler(CommandHandler("ai", ai_command))
#     app.add_handler(CommandHandler("imposter", imposter))
#     app.add_handler(CommandHandler("ttt", ttt))
#     app.add_handler(CallbackQueryHandler(ttt_join_callback, pattern=r"^tjoin_"))
#     app.add_handler(CallbackQueryHandler(ttt_move_callback, pattern=r"^tttmove_"))
#     app.add_handler(CommandHandler("ijoin", ijoin))
#     app.add_handler(CallbackQueryHandler(imposter_guess_callback))
#     app.add_handler(CommandHandler("raffle", giveaway))
#     app.add_handler(CommandHandler("rjoin", rjoin))
#     app.add_handler(CommandHandler("ur", ur))
#     app.add_handler(CallbackQueryHandler(redeem_callback))
#     app.add_handler(CommandHandler("urall", urall))
#     app.add_handler(CommandHandler("match", match))
#     app.add_handler(CallbackQueryHandler(join_match, pattern="^match_"))
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # =========================
    # COMMAND HANDLERS
    # =========================
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stake", stake))
    app.add_handler(CommandHandler("beg", beg))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("backup", backup_db))
    app.add_handler(CommandHandler("mine", mine))
    app.add_handler(CommandHandler("give", give))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("evenodd", evenodd))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("addall", addall))
    app.add_handler(CommandHandler("random", rando))
    app.add_handler(CommandHandler("bet", bet))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("reset", resetall))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("maths", maths))
    app.add_handler(CommandHandler("create", fd))
    app.add_handler(CommandHandler("code", code))
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("imposter", imposter))
    app.add_handler(CommandHandler("ttt", ttt))
    app.add_handler(CommandHandler("ijoin", ijoin))
    app.add_handler(CommandHandler("raffle", giveaway))
    app.add_handler(CommandHandler("rjoin", rjoin))
    app.add_handler(CommandHandler("ur", ur))
    app.add_handler(CommandHandler("urall", urall))
    app.add_handler(CommandHandler("match", match))

    # =========================
    # CALLBACK HANDLERS (ORDER MATTERS)
    # =========================

    # Specific pattern callbacks FIRST
    app.add_handler(CallbackQueryHandler(mine_callback, pattern=r'^mine_'))
    app.add_handler(CallbackQueryHandler(math_join_callback, pattern=r'^mathjoin_'))
    app.add_handler(CallbackQueryHandler(ttt_join_callback, pattern=r'^tjoin_'))
    app.add_handler(CallbackQueryHandler(ttt_move_callback, pattern=r'^tttmove_'))
    app.add_handler(CallbackQueryHandler(join_match, pattern=r'^match_'))
    app.add_handler(CallbackQueryHandler(redeem_callback, pattern=r'^redeem_'))

    # Imposter (if it has pattern, add it above instead)
    app.add_handler(CallbackQueryHandler(imposter_guess_callback))

    # =========================
    # MESSAGE HANDLERS
    # =========================
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), maths_answer))

    clear_console()
    design_screen()

    # ✅ Startup message using post_init (cleanest way)
    async def post_init(app):
        await app.bot.send_message(
            chat_id=ADMINS[0],
            text="🤖 Bot is now running!"
        )

    app.post_init = post_init

    app.run_polling()


if __name__ == "__main__":
    main()
