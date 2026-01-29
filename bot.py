import json
from datetime import date
ADMIN_CHAT_ID = 1117990260

# <<< ДОБАВЛЕНО >>>
from flask import Flask
import threading
# <<< ДОБАВЛЕНО >>>

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# <<< ДОБАВЛЕНО >>>
# --- KEEP ALIVE ДЛЯ RENDER ---
keep_alive_app = Flask("keep_alive")

@keep_alive_app.route("/")
def home():
    return "Bot is alive"

def run():
    keep_alive_app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
# <<< ДОБАВЛЕНО >>>

# --- СЛОВАРЬ ДЛЯ ХРАНЕНИЯ ДАННЫХ В ПАМЯТИ ---
users = {}

STATS_FILE = "stats.json"


def load_stats():
    with open(STATS_FILE, "r") as f:
        return json.load(f)


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


waiting_for_request = set()

# --- ТЕКСТЫ БОТА ---
REQUEST_TEXT = (
    "📝 Напиши, пожалуйста:\n\n"
    "• Чему хочешь научиться (Фингерстайл/Аккорды/Что-то конкретное)\n"
    "• Оцени свой текущий уровень (1-10)\n"
    "• Цель\n\n"
    "Я прочитаю и отвечу лично 🤙"
)

ABOUT_TEXT = (
    "Я Артём.\n"
    "Студент МАИ, фингерстайл гитарист, чемпион России и х3 КМС по волейболу.\n"
    "Развиваюсь в программировании, игре на гитаре и онлайн-деньгах 🚀"
)

PATH_TEXT = (
    "Мой путь:\n"
    "Волейбол (11 лет) → Фингерстайл (2 года) → Программная инженерия → Программирование → Онлайн-бизнес"
)

SKILLS_TEXT = (
    "Чем могу быть полезен:\n"
    "• Обучение игре на гитаре\n"
    "• Telegram-боты\n"
    "• Автоматизация\n"
    "• Обучение Python (ОГЭ/ЕГЭ)\n"
    "• Помощь с проектами"
)

CONTACT_TEXT = (
    "Связаться со мной:\n"
    "@te1ron"
)

EDU_TEXT = (
    "📚 Обучение и репетиторство:\n"
    "• Гитара с нуля\n"
    "• Python с нуля\n"
    "• Подготовка к ОГЭ / ЕГЭ (информатика/математика)\n"
    "• Объясняю просто и по делу, сразу показывая результат\n"
    "Напиши, если интересно 👇"
)

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    users[user_id] = user_name

    stats = load_stats()
    today = str(date.today())

    if stats["last_date"] != today:
        stats["today_users"] = 0
        stats["last_date"] = today

    if user_id not in stats["user_ids"]:
        stats["user_ids"].append(user_id)
        stats["total_users"] += 1
        stats["today_users"] += 1

    save_stats(stats)

    keyboard = [
        ["🧠 Обо мне", "🏆 Мой путь"],
        ["💻 Чем полезен", "📚 Обучаю"],
        ["📝 Записаться"],
        ["📩 Связаться"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Привет, {user_name}! 👋\n\n"
        "Я бот Артема. Выбери, что тебе интересно:",
        reply_markup=reply_markup
    )

# --- ОБРАБОТКА КНОПОК ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = users.get(user_id, "друг")
    text = update.message.text

    if text == "🧠 Обо мне":
        await update.message.reply_text(ABOUT_TEXT)

    elif text == "🏆 Мой путь":
        await update.message.reply_text(PATH_TEXT)

    elif text == "💻 Чем полезен":
        await update.message.reply_text(SKILLS_TEXT)

    elif text == "📚 Обучаю":
        await update.message.reply_text(EDU_TEXT)

    elif text == "📩 Связаться":
        await update.message.reply_text(CONTACT_TEXT)

    elif text == "📝 Записаться":
        waiting_for_request.add(user_id)
        await update.message.reply_text(REQUEST_TEXT)

    elif user_id in waiting_for_request:
        waiting_for_request.remove(user_id)

        username = update.message.from_user.username
        user_link = f"https://t.me/{username}" if username else "юзернейм не указан"

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "🔥 НОВАЯ ЗАЯВКА\n\n"
                f"Имя: {user_name}\n"
                f"Юзернейм: {user_link}\n"
                f"Сообщение:\n{text}"
            )
        )

        await update.message.reply_text(
            "Спасибо! Я получил сообщение и скоро отвечу 👍"
        )

    else:
        await update.message.reply_text("Выбери пункт из меню 👇")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_CHAT_ID:
        return

    stats = load_stats()

    await update.message.reply_text(
        "📊 Статистика бота:\n"
        f"Всего пользователей: {stats['total_users']}"
    )


async def stats_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_CHAT_ID:
        return

    stats = load_stats()

    await update.message.reply_text(
        "📈 Статистика за сегодня:\n"
        f"Новых пользователей: {stats['today_users']}"
    )

# --- ЗАПУСК ---
def main():
    import os

    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("stats_today", stats_today))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    keep_alive()   # <<< ДОБАВЛЕНО
    main()