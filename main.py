import os
import openai
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# Получаем токены
TELEGRAM_BOT_TOKEN = os.getenv("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g")
OPENAI_API_KEY = os.getenv("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")
PORT = int(os.environ.get("PORT", 8080))

openai.api_key = OPENAI_API_KEY

# Telegram обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ИИ-командир подключён. Вызови меня словом 'ИИ'.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_message = update.message.text.strip()

    if "ии" not in user_message.lower():
        return

    await update.message.reply_text("📡 Приём. Обрабатываю...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — ИИ-командир в военном стиле. Отвечай строго, по-русски, кратко."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("⚠️ Ошибка. Проверь токен OpenAI.")
        print("Ошибка:", e)

# Запускаем Telegram polling в потоке
def run_telegram_bot():
    app = ApplicationBuilder().token("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🪖 Telegram бот активен.")
    app.run_polling()

# Flask-сервер для Render
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Бот работает (ИИ онлайн 🪖)"

if __name__ == '__main__':
    telegram_thread = threading.Thread(target=run_telegram_bot)
    telegram_thread.start()
    web_app.run(host="0.0.0.0", port=PORT)
