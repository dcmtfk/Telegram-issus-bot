import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

openai.api_key = os.getenv("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")
TELEGRAM_BOT_TOKEN = os.getenv("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if context.bot.username in user_message:
        user_message = user_message.replace(f"@{context.bot.username}", "").strip()
    else:
        return

    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )

    await update.message.reply_text(chat_response["choices"][0]["message"]["content"])

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started.")
    app.run_polling()
