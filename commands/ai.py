from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from openai import OpenAI
import os
from config import GROQ
# Initialize Groq client
client = OpenAI(
    api_key=GROQ,
    base_url="https://api.groq.com/openai/v1"
)

# /ai command handler
async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check if the user provided a prompt
    if not context.args:
        await update.message.reply_text("❌ Please provide a prompt. Usage: /ai <your question>")
        return

    prompt = " ".join(context.args)

    try:
        # Call Groq API
        response = client.responses.create(
            model="openai/gpt-oss-20b",
            input=prompt
        )

        # Get output text
        output_text = getattr(response, "output_text", None)
        if not output_text:
            # fallback in case output_text is not set
            output_text = response.output[0].content[0].text

        # Edit the previous message with AI response
        await update.message.reply_text(f"================\n💡 ASTRA AI 💡\n================\n\n{output_text}\n================")

    except Exception as e:
        await update.message.reply_text(f"❌ Something went wrong:\n{e}")
