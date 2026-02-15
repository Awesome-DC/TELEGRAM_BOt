from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
import sqlite3

# ================= CONFIG =================
BOT_TOKEN = "8369286252:AAGr9k1yoCoepKPwdw9OILwLhQ-dDyEoAJM"
PRODUCER_ID = 8038576832  # replace with producer Telegram ID
# =========================================

# --------- DATABASE SETUP ----------
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    ref_code TEXT PRIMARY KEY,
    user_id INTEGER,
    username TEXT,
    full_name TEXT
)
""")
conn.commit()
# ----------------------------------


def generate_ref(user_id: int) -> str:
    return f"C{user_id % 100000}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "how can i be off assistance to you"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # ================= CUSTOMER MESSAGE =================
    if user.id != PRODUCER_ID:
        ref = generate_ref(user.id)

        username = f"@{user.username}" if user.username else "No username"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

        cursor.execute(
            """
            INSERT OR IGNORE INTO conversations
            (ref_code, user_id, username, full_name)
            VALUES (?, ?, ?, ?)
            """,
            (ref, user.id, username, full_name)
        )
        conn.commit()

        await context.bot.send_message(
            chat_id=PRODUCER_ID,
                text=(
                    f"📩 New message from {ref}\n"
                    f"👤 Username: {username}\n"
                    f"📝 Name: {full_name}\n\n"
                    "==============\n"
                    f"{text}\n"
                    "=============="
                )
            )

        # await update.message.reply_text("✅ Message sent to producer.")

    # ================= PRODUCER REPLY =================
    else:
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "⚠️ Please reply to a customer message."
            )
            return

        replied_text = update.message.reply_to_message.text

        if not replied_text.startswith("📩 New message from"):
            await update.message.reply_text("⚠️ Invalid reply.")
            return

        lines = replied_text.splitlines()
        # First line should be "📩 New message from REF_CODE"
        if lines[0].startswith("📩 New message from"):
            ref = lines[0].replace("📩 New message from", "").strip()
        else:
            await update.message.reply_text("❌ Could not extract reference code.")
            return
        
        cursor.execute(
            "SELECT user_id FROM conversations WHERE ref_code = ?",
            (ref,)
        )
        result = cursor.fetchone()

        if not result:
            await update.message.reply_text("❌ User not found.")
            return

        customer_id = result[0]

        await context.bot.send_message(
            chat_id=customer_id,
            text=f"{text}"
        )

        # await update.message.reply_text("✅ Reply sent.")


# ================= MAIN =================
def man():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # print("🤖 Bot is running...")
    app.run_polling()
