import discord
from discord.ext import commands
from services.weather_service import get_weather
from services.translate_service import translate_text
from core.config import config
from core.logger import logger


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _handle_weather(self, destination, city: str):
        """Вспомогательный метод для получения и отправки погоды"""
        try:
            weather_data = await get_weather(city, self.bot.http_session)
            await destination.send(f"🌤️ Погода в **{city}**: {weather_data['temp']}°C, {weather_data['description']}")
        except Exception as e:
            logger.error(f"Error in weather request: {e}")
            await destination.send(f"❌ Не удалось получить погоду для города '{city}'.")

    async def _handle_translate(self, destination, target_lang: str, text: str):
        """Вспомогательный метод для перевода и отправки текста"""
        try:
            translated_text = await translate_text(text, target_lang, self.bot.http_session)
            await destination.send(f"📖 **Перевод ({target_lang.upper()}):** {translated_text}")
        except Exception as e:
            logger.error(f"Error in translate request: {e}")
            await destination.send("❌ Произошла ошибка при переводе текста.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Слушатель для обработки обращений без префикса !"""
        if message.author.bot:
            return

        content = message.content.strip()
        low_content = content.lower()

        # Обработка "Погода [Город]"
        if low_content.startswith("погода "):
            city = content[7:].strip()
            if city:
                await self._handle_weather(message.channel, city)

        # Обработка "Переведи [Текст]"
        elif low_content.startswith("переведи "):
            remainder = content[9:].strip()
            if not remainder:
                return

            # Пробуем определить, указан ли язык (напр. "Переведи en Привет")
            parts = remainder.split(maxsplit=1)
            target_lang = "EN"  # Язык по умолчанию
            text_to_translate = remainder

            # Если первое слово похоже на код языка (2 символа)
            if len(parts[0]) == 2 and parts[0].isalpha():
                target_lang = parts[0]
                text_to_translate = parts[1] if len(parts) > 1 else ""
            
            if text_to_translate:
                await self._handle_translate(message.channel, target_lang, text_to_translate)

    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Простая проверка связи"""
        await ctx.send(f"🏓 Pong! Я вижу сообщения в этом канале. Его ID: `{ctx.channel.id}`")

    @commands.command(name='id')
    async def id_command(self, ctx):
        """Узнать ID текущего канала"""
        await ctx.send(f"🆔 ID этого канала: `{ctx.channel.id}`. Используйте его в .env, если нужно.")

    @commands.command(name='weather')
    async def weather_command(self, ctx, *, city: str):
        """Команда через префикс: !weather Москва"""
        await self._handle_weather(ctx, city)

    @commands.command(name='translate')
    async def translate_command(self, ctx, target_lang: str, *, text: str):
        """Команда через префикс: !translate en Привет"""
        await self._handle_translate(ctx, target_lang, text)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Обработка ошибок команд с префиксом !"""
        if isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.name == 'weather':
                await ctx.send("❓ Укажите город. Пример: `!weather Москва` или просто напишите `Погода Москва`.")
            elif ctx.command.name == 'translate':
                await ctx.send("❓ Укажите язык и текст. Пример: `!translate en Привет`.")
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            logger.error(f"Command error: {error}")


async def setup(bot):
    await bot.add_cog(BotCommands(bot))