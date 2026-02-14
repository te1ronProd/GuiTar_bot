print("ФАЙЛ ЗАГРУЗИЛСЯ")
import json
from datetime import date
ADMIN_CHAT_ID = 1117990260
VIDEO_FILE_ID = "BAACAgIAAxkBAAMbaY300iGEexN9ogABj8VhGAKaZv5uAAJFqgACCkcYSAVCFXG23vC2OgQ"
PHOTO_FILE_ID = "AgACAgIAAxkBAAMnaY33kr8_oZ-aAvuUtepiv9WC7dsAAhwSaxuQ53BIr8TP8sZZrGUBAAMCAAN5AAM6BA"

# <<< ДОБАВЛЕНО >>>
from flask import Flask
import threading
# <<< ДОБАВЛЕНО >>>

from telegram.constants import ParseMode
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
    "<blockquote>• Чему хочешь научиться (Фингерстайл/Аккорды/Что-то конкретное)\n"
    "• Оцени свой текущий уровень (1-10)\n"
    "• Цель</blockquote>\n\n"
    "Я прочитаю и отвечу лично 🤙"
)

LESSON_TEXT = (
    "Всё, что тебя ждёт на первом уроке:\n\n"
    "<blockquote>• Оплата <b>ПО ОЩУЩЕНИЯМ</b> (от 0 до 700₽)\n"
    "• Знакомство со мной\n"
    "• Обсуждение целей и формата обучения\n"
    "• Постановка техники (если требуется)\n"
    "• Первая уверенность в руках\n"
    "• Понимание, как мы будем двигаться дальше</blockquote>"
)

ABOUT_TEXT = (
    "<b>Я Артём.</b>\n"
    "Обо мне:\n\n"
    "<blockquote>✈️ Студент МАИ, факультет программная инженерия\n" 
    "🎸 Фингерстайл гитарист\n" 
    "🏆 Чемпион России и х3 КМС по волейболу\n\n"
    "Развиваюсь в программировании, игре на гитаре и онлайн бизнесе 🚀</blockquote>"
)

PATH_TEXT = (
    "Мой путь:\n"
    "Волейбол (11 лет) → Фингерстайл (2 года) → Программная инженерия → Программирование → Онлайн-бизнес"
)

SKILLS_TEXT = (
    "Почему тебе стоит учиться у меня:\n\n"
    "<blockquote>• <b>Высокий уровень\n"
    "• Станем братками с первой встречи\n"
    "• Обучаю на популярных произведениях\n"
    "• Быстрый результат\n"
    "• Правильная техника\n"
    "• Минимум теории, максимум практики\n"
    "• Первое произведение всего за 2-3 урока!</b></blockquote>\n\n"
    "Записывайся 🙃"
)

CONTACT_TEXT = (
    "<i>Связаться со мной:</i>\n"
    "@te1ron"
)
PRICE_TEXT = (
    "<b>Цены:</b>\n\n"
    "<blockquote>1 урок = <b>700₽</b>\n"
    "Пакеты:\n1) 3 урока = <b>1900₽</b>\n2) 5 уроков = <b>3200₽</b>\n3) 10 уроков = <b>6200₽</b>\n"
    "Оплата <b>ПОСЛЕ</b> урока переводом</blockquote>\n\n"
    "Если есть вопросы, пиши в личку 👇"
)


MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🧠 Обо мне", "🤔 Почему я?"],
        ["☝️ Первый урок", "💸 Цены"],
        ["📩 Связаться", "📝 Записаться"],
        ["🎥 ВИДЕО МОЕЙ ИГРЫ 🔥"]
    ],
    resize_keyboard=True
)

REQUEST_KEYBOARD = ReplyKeyboardMarkup(
    [["❌ Отменить запись"]],
    resize_keyboard=True
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

    await update.message.reply_text(
        f"Привет, {user_name}! 👋\n\n"
        "Я бот Артема. Выбери, что тебе интересно:",
        reply_markup=MAIN_KEYBOARD
    )


    
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id

    await update.message.reply_text(
        f"Вот твой PHOTO_FILE_ID 👇\n\n{file_id}"
    )

#Работа с видео
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    print(update.message.video.file_id)
    print("VIDEO FILE ID:", video.file_id)

    await update.message.reply_text(
        "Видео получено ✅\nID выведен в консоль"
    )

# --- ОБРАБОТКА КНОПОК ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = users.get(user_id, "друг")
    text = update.message.text

    if text == "🧠 Обо мне":
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=PHOTO_FILE_ID,
            caption=ABOUT_TEXT,
            reply_markup=MAIN_KEYBOARD,
            parse_mode=ParseMode.HTML
        )

    elif text == "🤔 Почему я?":
        await update.message.reply_text(SKILLS_TEXT, reply_markup=MAIN_KEYBOARD)

    elif text == "💸 Цены":
        await update.message.reply_text(PRICE_TEXT, reply_markup=MAIN_KEYBOARD)

    elif text == "☝️ Первый урок":
        await update.message.reply_text(LESSON_TEXT, reply_markup=MAIN_KEYBOARD)

    elif text == "📩 Связаться":
        await update.message.reply_text(CONTACT_TEXT, reply_markup=MAIN_KEYBOARD)

    elif text == "📝 Записаться":
        waiting_for_request.add(user_id)
        await update.message.reply_text(
            REQUEST_TEXT + "\n\n❗ Напиши сообщение текстом 👇",
            reply_markup=REQUEST_KEYBOARD
        )

    elif text == "❌ Отменить запись":
        waiting_for_request.discard(user_id)
        await update.message.reply_text(
            "Запись отменена 👌",
            reply_markup=MAIN_KEYBOARD
        )

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
            "Спасибо! Я получил сообщение и скоро отвечу 👍",
            reply_markup=MAIN_KEYBOARD
        )

    elif text == "🎥 ВИДЕО МОЕЙ ИГРЫ 🔥":
        await context.bot.send_video(
            chat_id=update.message.chat_id,
            video=VIDEO_FILE_ID,
            caption="🎸 Перемен в моем исполнении\n\nЕсли хочешь так же — пиши, построим твой путь 🤙"
        )

    else:
        await update.message.reply_text(
            "Выбери пункт из меню 👇",
            reply_markup=MAIN_KEYBOARD
        )

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
    print("MAIN STARTED")
    import os

    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).parse_mode("HTML").build()


    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("stats_today", stats_today))
    app.add_handler(CommandHandler("start", start))

    # <<< ДОБАВЛЕНО: ловим видео и печатаем file_id >>>
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    # <<< ТЕКСТ ОБРАБАТЫВАЕТСЯ ПОСЛЕ >>>
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("БОТ 100% ЗАПУЩЕН И ЭТО НОВАЯ ВЕРСИЯ")
    app.run_polling()
    


if __name__ == "__main__":
    keep_alive()   # <<< ДОБАВЛЕНО
    main()
    