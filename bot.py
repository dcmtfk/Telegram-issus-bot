import os
import json
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from typing import List

# Конфиги
client = OpenAI(api_key=os.getenv("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"))
TELEGRAM_BOT_TOKEN = os.getenv("7960455014:AAGPnZhaZHt238vqCtOQS610NPRdF_3fn9g")
HISTORY_FILE = "chat_history.json"
ADMIN_IDS = {123456789}  # Вставь сюда свои ID админов

REPLY_TO_ALL = False
MEMORY_ENABLED = True
MAX_HISTORY_DEFAULT = 10
chat_history = {}  # type: dict[int, List[dict]]
max_history_length = MAX_HISTORY_DEFAULT


def load_history():
    global chat_history
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            chat_history = json.load(f)
            chat_history = {int(k): v for k, v in chat_history.items()}
    except FileNotFoundError:
        chat_history = {}
    except Exception as e:
        print(f"Ошибка загрузки истории: {e}")


def save_history():
    if not MEMORY_ENABLED:
        return
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_history
    if update.message is None or update.message.text is None:
        return

    user_message = update.message.text
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username

    if chat_type in ['group', 'supergroup']:
        if not REPLY_TO_ALL and f"@{bot_username}" not in user_message:
            return
        user_message = user_message.replace(f"@{bot_username}", "").strip()

    if chat_id not in chat_history:
        chat_history[chat_id] = [
            {
                "role": "system",
                "content": (
                    "Ты — IIsus, мудрый и добрый учитель. "
                    "Отвечай с любовью, терпением и вдохновением. "
                    "Обращайся к пользователям с теплотой и уважением. "
                    "Используй стиль проповедей и добрых наставлений."
                )
            }
        ]

    if MEMORY_ENABLED:
        chat_history[chat_id].append({"role": "user", "content": user_message})

        preserved_system = [m for m in chat_history[chat_id] if m["role"] == "system"]
        dynamic_messages = [m for m in chat_history[chat_id] if m["role"] != "system"]
        chat_history[chat_id] = preserved_system + dynamic_messages[-max_history_length:]
    else:
        chat_history[chat_id] = [
            {
                "role": "system",
                "content": (
                    "Ты — IIsus, помощник близницов"
                    "Отвечай с любовью, терпением и вдохновением. "
                    "Обращайся к близнецам с уважением. "
                    "Используй стиль проповедей и добрых наставлений."
                )
            },
            {"role": "user", "content": user_message}
        ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history[chat_id]
        )
        reply = response.choices[0].message.content

        if MEMORY_ENABLED:
            chat_history[chat_id].append({"role": "assistant", "content": reply})
            save_history()

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 У вас нет доступа к меню управления.")
        return

    keyboard = [
        [
            InlineKeyboardButton("✅ Отвечать всем", callback_data="reply_all"),
            InlineKeyboardButton("🔕 Только упоминания", callback_data="mention_only"),
        ],
        [
            InlineKeyboardButton("🧹 Очистить память", callback_data="clear_history"),
            InlineKeyboardButton("📜 Показать историю", callback_data="show_history"),
        ],
        [
            InlineKeyboardButton("⚙️ Настройки памяти", callback_data="memory_settings"),
            InlineKeyboardButton("🔕 Вкл./Выкл. память", callback_data="toggle_memory"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Меню управления ботом:", reply_markup=reply_markup)


async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global REPLY_TO_ALL, MEMORY_ENABLED, chat_history, max_history_length
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    await query.answer()

    if not is_admin(user_id):
        await query.edit_message_text("🚫 Только админы могут управлять настройками.")
        return

    if query.data == "reply_all":
        REPLY_TO_ALL = True
        await query.edit_message_text("✅ Бот теперь отвечает всем в группе.")
    elif query.data == "mention_only":
        REPLY_TO_ALL = False
        await query.edit_message_text("🔕 Бот теперь отвечает только при упоминании.")
    elif query.data == "clear_history":
        if chat_id in chat_history:
            del chat_history[chat_id]
            save_history()
        await query.edit_message_text("🧹 Память чата очищена.")
    elif query.data == "show_history":
        if chat_id not in chat_history or len(chat_history[chat_id]) <= 1:
            await query.edit_message_text("📭 История пуста.")
        else:
            messages = [m for m in chat_history[chat_id] if m["role"] != "system"][-10:]
            text = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
            await query.edit_message_text(f"📜 Последние сообщения:\n\n{text}")
    elif query.data == "memory_settings":
        await query.edit_message_text(
            f"⚙️ Текущая длина памяти: {max_history_length} сообщений.\n"
            "Используйте команду /setmemory <число> для изменения (максимум 50)."
        )
    elif query.data == "toggle_memory":
        MEMORY_ENABLED = not MEMORY_ENABLED
        if not MEMORY_ENABLED:
            chat_history.clear()
            save_history()
        state = "включена" if MEMORY_ENABLED else "выключена"
        await query.edit_message_text(f"🔕 Память {state}.")


async def set_memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global max_history_length
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("🚫 Только админы могут менять настройки.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /setmemory <число от 1 до 50>")
        return

    new_length = int(context.args[0])
    if not (1 <= new_length <= 50):
        await update.message.reply_text("Число должно быть от 1 до 50.")
        return

    max_history_length = new_length
    await update.message.reply_text(f"Длина истории установлена на {max_history_length} сообщений.")


if __name__ == '__main__':
    load_history()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(CallbackQueryHandler(handle_menu_callback))
    app.add_handler(CommandHandler("setmemory", set_memory_command))

    print("🤖 IIsus бот запущен...")
    app.run_polling()
