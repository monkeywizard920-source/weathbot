import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_CHANNEL_1 = int(os.getenv("DISCORD_CHANNEL_1", 1498441099629297664))  # Канал для оригинальных сообщений из Telegram
    DISCORD_CHANNEL_2 = int(os.getenv("DISCORD_CHANNEL_2", 1498441237538017391))  # Канал для перевода
    DISCORD_WEATHER_CHANNEL = int(os.getenv("DISCORD_WEATHER_CHANNEL", 1498442070765863114))  # Канал для погоды

    # Telegram
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_CHANNEL = int(os.getenv("TELEGRAM_CHANNEL", -1001237513492))  # Канал Topor

    # OpenWeather API
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

    # DeepL API
    TRANSLATE_API_KEY = os.getenv("TRANSLATE_API_KEY", "")

    # Запрещённые слова для замены
    FORBIDDEN_WORDS = {
        "bad_word_1": "good_word_1",
        "bad_word_2": "good_word_2",
    }

config = Config()