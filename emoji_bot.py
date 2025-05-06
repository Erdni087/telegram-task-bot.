import logging
import nest_asyncio
import asyncio
import requests
import random
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # Планировщик задач

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Токены
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

# Хранилище ID пользователей
user_ids = set()

# Получение заданий с TaskRabbit
def get_taskrabbit_jobs(city_slug="new-york-city"):
    url = f"https://www.taskrabbit.com/locations/{city_slug}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for job in soup.select("a.styles__CategoryLinkWrapper-sc-1ni9u3v-2"):
        title = job.text.strip()
        link = job["href"]
        full_link = f"https://www.taskrabbit.com{link}"
        jobs.append((title, full_link))

    return jobs[:5]

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_ids.add(update.effective_chat.id)
    await update.message.reply_text("Привет! Я многофункциональный бот 😊 Введи /help чтобы увидеть команды.")

async def emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟✨🚀")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = "New York"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    try:
        response = requests.get(url).json()
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        await update.message.reply_text(f"🌡 Температура в {city}: {temp}°C\n☁️ Погода: {desc}")
    except Exception as e:
        await update.message.reply_text("Ошибка при получении погоды.")
        print("Ошибка:", e)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])[:3]
        if not articles:
            await update.message.reply_text("Нет новостей.")
            return
        msg = "📰 Топ новости:\n"
        for art in articles:
            msg += f"\n- {art['title']}\n{art['url']}\n"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("Ошибка при получении новостей.")
        print("Ошибка:", e)

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "💬 «Будь собой — остальные роли уже заняты.»",
        "💬 «Успех — это движение от неудачи к неудаче без потери энтузиазма.»",
        "💬 «Не жди. Время никогда не будет подходящим.»"
    ]
    await update.message.reply_text(random.choice(quotes))

async def birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎂 Поздравляем с Днём Рождения! (функция будет расширяться)")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Доброе утро! Ваша подборка дня:\n/weather\n/quote\n/news")

async def taskrabbit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Ищу новые задания с TaskRabbit...")
    try:
        jobs = get_taskrabbit_jobs()
        if jobs:
            text = "🛠 Найдены задания TaskRabbit:\n\n"
            for title, link in jobs:
                text += f"🔹 {title}\n{link}\n\n"
        else:
            text = "😕 Нет доступных заданий."
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка TaskRabbit: {e}")
        print("Ошибка TaskRabbit:", e)

async def linkedin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💼 LinkedIn: поиск вакансий в разработке.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
Список доступных команд:
/start – Приветствие
/emoji – Эмодзи
/weather – Показать погоду
/news – Новости
/quote – Цитата дня
/birthday – Поздравление с ДР
/daily – Ежедневная подборка
/taskrabbit – Новые задания TaskRabbit
/linkedin – Новые вакансии LinkedIn
/help – Помощь
"""
    await update.message.reply_text(text)

# Основной запуск
async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрация команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("emoji", emoji))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("birthday", birthday))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("taskrabbit", taskrabbit))
    app.add_handler(CommandHandler("linkedin", linkedin))
    app.add_handler(CommandHandler("help", help_command))

    # Планировщик
    scheduler = AsyncIOScheduler()

    async def daily_message():
        for user_id in user_ids:
            try:
                # Погода
                city = "New York"
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
                response = requests.get(url).json()
                temp = response["main"]["temp"]
                desc = response["weather"][0]["description"]
                weather_text = f"🌡 Погода в {city}: {temp}°C\n☁️ {desc}"

                # Цитата
                quotes = [
                    "💬 «Будь собой — остальные роли уже заняты.»",
                    "💬 «Успех — это движение от неудачи к неудаче без потери энтузиазма.»",
                    "💬 «Не жди. Время никогда не будет подходящим.»"
                ]
                quote_text = random.choice(quotes)

                # Новости
                news_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
                news_response = requests.get(news_url).json()
                articles = news_response.get("articles", [])[:3]
                news_text = "📰 Новости:\n" + "\n".join(
                    f"🔹 {art['title']}\n{art['url']}" for art in articles
                ) if articles else "Нет свежих новостей."

                # TaskRabbit
                jobs = get_taskrabbit_jobs()
                taskrabbit_text = "🛠 Задания:\n" + "\n".join(
                    f"{title}\n{link}" for title, link in jobs
                ) if jobs else "Нет заданий TaskRabbit."

                # Отправка
                await app.bot.send_message(chat_id=user_id, text="📅 Ежедневная подборка:\n\n" +
                                           weather_text + "\n\n" +
                                           quote_text + "\n\n" +
                                           news_text + "\n\n" +
                                           taskrabbit_text)
            except Exception as e:
                print("Ошибка при отправке ежедневной рассылки:", e)

    # Запланировать на 8:00 утра UTC
       # Планировщик: запуск каждый час
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_message, "interval", hours=1)
    scheduler.start()


  

    print("Бот работает...")
    await app.run_polling()

# Запуск
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(run_bot())
