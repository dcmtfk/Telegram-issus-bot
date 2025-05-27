import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Настройка ключей
openai_client = OpenAI(api_key=os.getenv("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"))
TELEGRAM_BOT_TOKEN = os.getenv("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g")

# Кнопки меню
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("📜 Помощь", callback_data="help")],
        [InlineKeyboardButton("🛑 Выключить", callback_data="shutdown")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🪖 Солдат ИИ на связи. Ожидаю приказов.",
        reply_markup=get_main_menu()
    )

# Ответ на нажатия в меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "settings":
        await query.edit_message_text("🔧 Настройки пока не реализованы.")
    elif query.data == "help":
        await query.edit_message_text("ℹ️ Просто упомяни 'ИИ' в сообщении, и я отвечу.")
    elif query.data == "shutdown":
        await query.edit_message_text("💤 Бот завершает службу.")
        await context.application.stop()

# Ответ на команды
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if "ии" in user_message.lower():
        await update.message.chat.send_action(action="typing")
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — ИИ в стиле военного помощника, говоришь строго, коротко и по делу."},
                {"role": "user", "content": user_message}
            ]
        )
        response_text = completion.choices[0].message.content
        await update.message.reply_text(f"🪖 ИИ докладывает:\n{response_text}")

# Запуск
def main():
    app = ApplicationBuilder().token("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
