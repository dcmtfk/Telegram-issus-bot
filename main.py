import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

TELEGRAM_BOT_TOKEN = os.getenv("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g")
HF_TOKEN = os.getenv("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")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Отправка запроса к Hugging Face
def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()

# Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Солдат, ИИ на связи. Вызови меня словом 'ИИ' и доложи задачу.")

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    if "ии" not in user_message.lower():
        return  # Игнорируем всё, кроме сообщений с "ии"

    await update.message.reply_text("📡 Принял вызов. Обрабатываю...")

    prompt = (
        f"ИИ-командир"
        f"... "
        f"Сообщение: {user_message}"
    )

    response = query({
        "inputs": prompt,
        "parameters": {"max_new_tokens": 100}
    })

    try:
        full_text = response[0]["generated_text"]
        reply = full_text.split(user_message, 1)[-1].strip()
    except:
        reply = "Ошибка обработки. Повтори вызов, солдат."

    await update.message.reply_text(reply)

# Запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🪖 ИИ-боец на связи.")
    app.run_polling()
