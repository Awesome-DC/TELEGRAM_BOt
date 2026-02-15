# from telegram import Update
# from telegram.ext import ContextTypes
# from config import ADMINS
# from db import get_user, update_coins, get_redeem_code, mark_code_used, generate_code, add_redeem_code

# async def fd(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     if user_id not in ADMINS:
#         await update.message.reply_text("❌ Admin only command.")
#         return

#     if len(context.args) < 2:
#         await update.message.reply_text("Usage: /create <coin_amount> <number_of_codes>")
#         return

#     coins = int(context.args[0])
#     count = int(context.args[1])

#     codes = []
#     for _ in range(count):
#         code = generate_code()
#         add_redeem_code(code, coins)
#         codes.append(code)

#     # Send codes privately
#     await update.message.reply_text(f"✅ Generated {count} code(s) worth {coins} coins each:\n" + "\n".join(codes))

# async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     user = get_user(user_id)
#     if not user:
#         await update.message.reply_text("❌ You are not registered yet.")
#         return

#     if len(context.args) == 0:
#         await update.message.reply_text("❌ Usage: /code <redeem_code>")
#         return

#     redeem_code = context.args[0].upper()
#     db_code = get_redeem_code(redeem_code)

#     if not db_code:
#         await update.message.reply_text("❌ Invalid code!")
#         return

#     if db_code["used_by"]:
#         await update.message.reply_text("⚠️ This code has already been used.")
#         return

#     # Redeem coins
#     new_coins = user["coins"] + db_code["coins"]
#     update_coins(user_id, new_coins)
#     mark_code_used(redeem_code, user_id)

#     await update.message.reply_text(f"✅ Success! You received {db_code['coins']} coins.\nYour new balance: {new_coins}")

from telegram import Update
from telegram.ext import ContextTypes
from config import ADMINS
from db import get_user, update_coins, get_redeem_code, mark_code_used, generate_code, add_redeem_code

async def fd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command to generate redeem codes.
    Usage: /fd <coins> <number_of_codes>
    """
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ Admin only command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /fd <coin_amount> <number_of_codes>")
        return

    try:
        coins = int(context.args[0])
        count = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Both coin amount and number of codes must be numbers.")
        return

    codes = []
    for _ in range(count):
        code = generate_code().upper()  # ensure uppercase for consistency
        add_redeem_code(code, coins)
        codes.append(code)

    # Send each code privately in HTML code block for easy tap-to-copy
    for idx, code in enumerate(codes, start=1):
        await update.message.reply_text(
            f"🎁 Redeem Code {idx} (worth {coins} coins):\n\n<code>{code}</code>\n",
            parse_mode="HTML"
        )

    # Summary message
    await update.message.reply_text(
        f"✅ Generated {count} code(s) worth {coins} coins each. Check your messages above!"
    )


async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command for users to redeem a code.
    Usage: /code <redeem_code>
    """
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("❌ You are not registered yet.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /code <redeem_code>")
        return

    redeem_code = context.args[0].upper()
    db_code = get_redeem_code(redeem_code)

    if not db_code:
        await update.message.reply_text("❌ Invalid code!")
        return

    if db_code["used_by"]:
        await update.message.reply_text("⚠️ This code has already been used.")
        return

    # Redeem coins
    new_coins = user["coins"] + db_code["coins"]
    update_coins(user_id, new_coins)
    mark_code_used(redeem_code, user_id)

    await update.message.reply_text(
        f"✅ Success! You received {db_code['coins']} coins.\n"
        f"💰 Your new balance: {new_coins}"
    )
