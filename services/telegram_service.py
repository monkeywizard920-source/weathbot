from telethon import TelegramClient, events
from core.config import config
from core.logger import logger
from services.transform_service import transform_text


class TelegramService:
    def __init__(self, discord_bot):
        self.discord_bot = discord_bot
        self.client = TelegramClient(
            'telegram_session',
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH
        )

    async def start(self):
        if config.TELEGRAM_BOT_TOKEN:
            # Если есть токен — заходим как бот (без input)
            await self.client.start(bot_token=config.TELEGRAM_BOT_TOKEN)
            logger.info("Telegram client started as Bot")
        else:
            # Если токена нет — пробуем зайти как пользователь
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.error("Telegram session not authorized!")
                logger.error("Please run the bot LOCALLY first to create 'telegram_session.session'")
                raise RuntimeError("Session not found. Login required.")
            
            logger.info("Telegram client started as User")

        self.client.add_event_handler(self.handle_new_message, events.NewMessage(chats=config.TELEGRAM_CHANNEL))

    async def handle_new_message(self, event):
        original_message = event.message.text
        if not original_message:
            return

        transformed_message = await transform_text(original_message)

        # Отправка оригинального сообщения в DISCORD_CHANNEL_1
        channel_1 = self.discord_bot.get_channel(config.DISCORD_CHANNEL_1)
        if channel_1:
            await channel_1.send(f"Original message from Telegram: {original_message}")
        else:
            logger.warning(f"Discord channel {config.DISCORD_CHANNEL_1} not found in cache.")

        # Отправка изменённого сообщения в DISCORD_CHANNEL_2
        channel_2 = self.discord_bot.get_channel(config.DISCORD_CHANNEL_2)
        if channel_2:
            await channel_2.send(f"Transformed message: {transformed_message}")
        else:
            logger.warning(f"Discord channel {config.DISCORD_CHANNEL_2} not found in cache.")

    async def stop(self):
        await self.client.disconnect()
        logger.info("Telegram client stopped")