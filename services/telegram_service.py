from telethon import TelegramClient, events, connection
from telethon.errors import FloodWaitError
from core.config import config
from core.logger import logger
from services.transform_service import transform_text


class TelegramService:
    def __init__(self, discord_bot):
        self.discord_bot = discord_bot

        proxy = None
        conn_type = None
        if config.USE_PROXY:
            proxy = (config.PROXY_SERVER, config.PROXY_PORT, config.PROXY_SECRET)
            conn_type = connection.ConnectionTcpMTProxyIntermediate

        self.client = TelegramClient(
            config.TELEGRAM_STRING_SESSION or 'telegram_session', # Используем stringsession или файловую
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH,
            proxy=proxy,
            connection=conn_type
        )

        # Collect all Telegram channels to listen to
        self.all_telegram_channels_to_listen = [config.TELEGRAM_CHANNEL]
        self.all_telegram_channels_to_listen.extend(config.TELEGRAM_NEWS_CHANNELS_MAPPING.keys())

    async def start(self):
        if config.TELEGRAM_BOT_TOKEN:
            # Если есть токен — заходим как бот (без input)
            await self.client.start(bot_token=config.TELEGRAM_BOT_TOKEN)
            logger.info("Telegram client started as Bot.")
        else:
            # Если токена нет — пробуем зайти как пользователь
            # Передаем только те параметры, которые реально заполнены в .env
            start_kwargs = {}
            if config.TELEGRAM_PHONE:
                start_kwargs['phone'] = config.TELEGRAM_PHONE
            if config.TELEGRAM_PASSWORD:
                start_kwargs['password'] = config.TELEGRAM_PASSWORD
            
            try:
                # Проверяем, авторизованы ли мы уже (есть ли валидная сессия)
                # Если используется stringsession, то connect() уже должен быть частью start()
                # Если используется файловая сессия, то connect() нужен для is_user_authorized()
                if not config.TELEGRAM_STRING_SESSION: # Если не используем stringsession, то пытаемся подключиться
                    await self.client.connect()

                if not await self.client.is_user_authorized(): # Проверяем, авторизован ли пользователь
                    if not config.TELEGRAM_PHONE:
                        raise RuntimeError("Session not found and TELEGRAM_PHONE is not set. Run locally first!")
                    
                    logger.info("Session not found. Attempting to login...")
                    # В контейнере это упадет с EOFError, если потребуется ввод кода
                    await self.client.start(**start_kwargs)
                    # После успешной авторизации, если это новая сессия, выводим stringsession
                    logger.info(f"New Telegram session created. Copy this string to TELEGRAM_STRING_SESSION in your .env: {self.client.session.save()}")
                else:
                    logger.info("Telegram session loaded from file.")

            except FloodWaitError as e:
                logger.error(f"Telegram rate limit hit! You must wait {e.seconds} seconds (~{e.seconds // 3600} hours) before trying again.")
                raise
            
            logger.info("Telegram client started as User (interactive login completed).")

        # Add event handler for all specified Telegram channels
        self.client.add_event_handler(self.handle_new_message, events.NewMessage(chats=self.all_telegram_channels_to_listen))

    async def handle_new_message(self, event):
        original_message = event.message.text
        if not original_message:
            return

        transformed_message = await transform_text(original_message)
        
        telegram_chat_id = event.chat_id

        # Handle the original forwarding logic (if the message is from the main TELEGRAM_CHANNEL)
        if telegram_chat_id == config.TELEGRAM_CHANNEL:
            # Отправка оригинального сообщения в DISCORD_CHANNEL_1
            channel_1 = await self._get_discord_channel(config.DISCORD_CHANNEL_1)
            if channel_1:
                await channel_1.send(f"Original message from Telegram: {original_message}")

            # Отправка изменённого сообщения в DISCORD_CHANNEL_2
            channel_2 = await self._get_discord_channel(config.DISCORD_CHANNEL_2)
            if channel_2:
                await channel_2.send(f"Transformed message: {transformed_message}")
            logger.info(f"Message from main Telegram channel {telegram_chat_id} forwarded to Discord channels {config.DISCORD_CHANNEL_1} and {config.DISCORD_CHANNEL_2}.")
        
        # Handle the new news forwarding logic
        elif telegram_chat_id in config.TELEGRAM_NEWS_CHANNELS_MAPPING:
            discord_target_channel_id = config.TELEGRAM_NEWS_CHANNELS_MAPPING[telegram_chat_id]
            discord_channel = await self._get_discord_channel(discord_target_channel_id)
            if discord_channel:
                await discord_channel.send(f"📰 {transformed_message}") # Adding a news emoji
            logger.info(f"Message from Telegram news channel {telegram_chat_id} forwarded to Discord channel {discord_target_channel_id}.")
        
        else:
            logger.warning(f"Message received from unmapped Telegram channel: {telegram_chat_id}. Message: {original_message[:50]}...")

    async def _get_discord_channel(self, channel_id):
        """Попытка получить канал из кэша, если нет — запрос по API"""
        channel = self.discord_bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.discord_bot.fetch_channel(channel_id)
            except Exception as e:
                logger.error(f"Failed to find Discord channel {channel_id}: {e}")
        return channel

    async def stop(self):
        await self.client.disconnect()
        logger.info("Telegram client stopped")