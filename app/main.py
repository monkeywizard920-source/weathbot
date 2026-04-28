import asyncio
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.discord_client import DiscordBot
from services.telegram_service import TelegramService
from core.logger import logger


async def main():
    discord_bot = DiscordBot()
    telegram_service = TelegramService(discord_bot)
    discord_bot.telegram_service = telegram_service

    try:
        # Запуск Telegram-сервиса
        try:
            await telegram_service.start()
        except Exception as te:
            logger.error(f"Telegram service failed to start: {te}")
            logger.warning("Discord bot will run without Telegram integration.")

        # Запуск Discord-бота (используем async контекстный менеджер для корректного закрытия)
        async with discord_bot:
            await discord_bot.start()
    except Exception as e:
        logger.error(f"Critical error during startup: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")
