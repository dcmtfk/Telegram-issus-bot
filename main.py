import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from openai import OpenAI

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BOT_NAME = "ИИ"
ADMIN_IDS = [123456789]  # Замените на ваш Telegram ID

# Хранение данных в памяти
bot_data = {
    "users": {},  # {user_id: {"requests": 0, "mode": "standard", "last_active": str}}
    "settings": {
        "active": True,
        "default_mode": "standard",
        "voice_enabled": False,
        "cache": {}  # {"вопрос": "ответ"}
    },
    "stats": {
        "total_requests": 0,
        "start_time": datetime.now().isoformat()
    }
}

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# 1. Добавляем команду /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Эта команда только для администраторов")
        return
    
    uptime = datetime.now() - datetime.fromisoformat(bot_data["stats"]["start_time"])
    await update.message.reply_text(
        f"📊 Статус бота {BOT_NAME}:\n"
        f"• Работает: {uptime}\n"
        f"• Всего запросов: {bot_data['stats']['total_requests']}\n"
        f"• Пользователей: {len(bot_data['users'])}\n"
        f"• Режим работы: {'ВКЛ' if bot_data['settings']['active'] else 'ВЫКЛ'}\n"
        f"• Голосовые: {'ВКЛ' if bot_data['settings']['voice_enabled'] else 'ВЫКЛ'}"
    )

# 2. Система администратора
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещен")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔌 Вкл/Выкл бота", callback_data="toggle_bot")],
        [InlineKeyboardButton("🎤 Вкл/Выкл голос", callback_data="toggle_voice")],
        [InlineKeyboardButton("🧹 Очистить кэш", callback_data="clear_cache")],
        [InlineKeyboardButton("📊 Статистика", callback_data="full_stats")]
    ]
    
    await update.message.reply_text(
        "👑 Админ-панель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 3. Обработка голосовых сообщений
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_data["settings"]["voice_enabled"]:
        await update.message.reply_text("ℹ️ Обработка голосовых сообщений отключена")
        return
    
    await update.message.reply_text("🔇 Голосовые сообщения пока не поддерживаются")
    # Здесь можно добавить реальную обработку через speech-to-text API

# 4. Кэширование частых вопросов
def get_cached_answer(question: str) -> str:
    question_lower = question.lower().strip()
    for cached_q, cached_a in bot_data["settings"]["cache"].items():
        if cached_q in question_lower or question_lower in cached_q:
            return cached_a
    return None

def add_to_cache(question: str, answer: str):
    if len(bot_data["settings"]["cache"]) > 50:  # Ограничиваем размер кэша
        bot_data["settings"]["cache"].pop(next(iter(bot_data["settings"]["cache"])))
    
    bot_data["settings"]["cache"][question.lower().strip()] = answer

# Обновленные обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = {
            "requests": 0,
            "mode": bot_data["settings"]["default_mode"],
            "last_active": datetime.now().isoformat()
        }
    
    await update.message.reply_text(
        f"👋 Привет! Я {BOT_NAME}, твой AI-помощник.\n"
        f"• Напиши мне сообщение с моим именем\n"
        f"• Используй /control для управления\n"
        f"• Статус: /status (для админов)"
    )

async def control_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = {
            "requests": 0,
            "mode": bot_data["settings"]["default_mode"],
            "last_active": datetime.now().isoformat()
        }
    
    keyboard = [
        [InlineKeyboardButton("🛠️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("📊 Статистика", callback_data="my_stats")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("👑 Админ", callback_data="admin")])
    
    await update.message.reply_text(
        "⚙️ Панель управления:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "toggle_bot" and user_id in ADMIN_IDS:
        bot_data["settings"]["active"] = not bot_data["settings"]["active"]
        status = "включен" if bot_data["settings"]["active"] else "выключен"
        await query.answer(f"Бот {status}")
        await admin_panel(update, context)
    
    elif query.data == "toggle_voice" and user_id in ADMIN_IDS:
        bot_data["settings"]["voice_enabled"] = not bot_data["settings"]["voice_enabled"]
        status = "включены" if bot_data["settings"]["voice_enabled"] else "выключены"
        await query.answer(f"Голосовые сообщения {status}")
        await admin_panel(update, context)
    
    elif query.data == "clear_cache" and user_id in ADMIN_IDS:
        bot_data["settings"]["cache"] = {}
        await query.answer("Кэш очищен")
        await admin_panel(update, context)
    
    elif query.data == "full_stats" and user_id in ADMIN_IDS:
        uptime = datetime.now() - datetime.fromisoformat(bot_data["stats"]["start_time"])
        await query.edit_message_text(
            f"📈 Полная статистика:\n"
            f"• Время работы: {uptime}\n"
            f"• Всего запросов: {bot_data['stats']['total_requests']}\n"
            f"• Уникальных пользователей: {len(bot_data['users'])}\n"
            f"• Размер кэша: {len(bot_data['settings']['cache'])}"
        )
    
    elif query.data == "admin" and user_id in ADMIN_IDS:
        await admin_panel(update, context)
    
    # ... (остальные обработчики кнопок из предыдущей версии)
    
    await query.answer()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_data["settings"]["active"]:
        await update.message.reply_text("⏸️ Бот временно отключен")
        return
    
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Инициализация пользователя
    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = {
            "requests": 0,
            "mode": bot_data["settings"]["default_mode"],
            "last_active": datetime.now().isoformat()
        }
    
    # Проверка обращения к боту
    if BOT_NAME.lower() not in user_message.lower() and not update.message.chat.is_private:
        return
    
    # Обновление статистики
    bot_data["users"][user_id]["requests"] += 1
    bot_data["users"][user_id]["last_active"] = datetime.now().isoformat()
    bot_data["stats"]["total_requests"] += 1
    
    # Проверка кэша
    cached_answer = get_cached_answer(user_message)
    if cached_answer:
        await update.message.reply_text(f"♻️ (из кэша)\n{cached_answer}")
        return
    
    try:
        # Генерация ответа
        mode = bot_data["users"][user_id]["mode"]
        system_msg = {
            "standard": "You are a helpful assistant.",
            "creative": "You are a creative assistant. Provide imaginative responses."
        }.get(mode, "You are a helpful assistant.")
        
        if client:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content
            add_to_cache(user_message, reply)  # Добавляем в кэш
        else:
            reply = "OpenAI не настроен. Используется заглушка."
        
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("control", control_panel))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("admin", admin_panel))
    
    # Обработчики сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Кнопки
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

if __name__ == '__main__':
    main()
