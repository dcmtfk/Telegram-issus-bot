import os
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

openai.api_key = os.getenv("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")
TELEGRAM_BOT_TOKEN = os.getenv("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g")

# Глобальный флаг: отвечать всем в группе или только при упоминании
REPLY_TO_ALL = False


# Ответы от Джарвиса
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    user_message = update.message.text
    chat_type = update.effective_chat.type
    bot_username = (await context.bot.get_me()).username

    # Поведение в группе
    if chat_type in ['group', 'supergroup']:
        if not REPLY_TO_ALL and f"@{bot_username}" not in user_message:
            return  # Игнорировать, если не упомянут и режим только-упоминания
        user_message = user_message.replace(f"@{bot_username}", "").strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — Джарвис, виртуальный помощник Близнецов. "
                        "Ты интеллигентный, точный и говоришь вежливо, с лёгким британским акцентом. "
                        "Твоя речь формальна, но допускает немного иронии. "
                        "Ты всегда обращаешься к своим хозяевам как 'Близнецы'. "
                        "Начинай ответы с фраз вроде: 'Как пожелаете, Близнецы' или 'Разумеется, Близнецы'. "
                        "Говори кратко и по делу, но не теряй индивидуальность."
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


# Команда /menu — отображает панель управления
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("✅ Отвечать всем", callback_data="reply_all"),
            InlineKeyboardButton("🔕 Только при упоминании", callback_data="mention_only"),
        ],
        [
            InlineKeyboardButton("ℹ️ Проверить режим", callback_data="status")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Управление ботом:", reply_markup=reply_markup)


# Обработка нажатий на кнопки
async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global REPLY_TO_ALL
    query = update.callback_query
    await query.answer()

    if query.data == "reply_all":
        REPLY_TO_ALL = True
        await query.edit_message_text("Теперь бот отвечает всем в группе.")
    elif query.data == "mention_only":
        REPLY_TO_ALL = False
        await query.edit_message_text("Теперь бот отвечает только при упоминании.")
    elif query.data == "status":
        status = "отвечает всем" if REPLY_TO_ALL else "отвечает только при упоминании"
        await query.edit_message_text(f"Сейчас бот {status} в группе.")


# Запуск приложения
if __name__ == '__main__':
    app = ApplicationBuilder().token("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g").build()

    # Обработчики
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(CallbackQueryHandler(handle_menu_callback))

    print("🤖 Бот Джарвис запущен...")
    app.run_polling()
