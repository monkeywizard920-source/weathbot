import discord
from discord.ext import commands
from services.weather_service import get_weather
from services.translate_service import translate_text
from core.config import config
from core.logger import logger


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='weather')
    async def weather_command(self, ctx, *, city: str):
        if ctx.channel.id != config.DISCORD_WEATHER_CHANNEL:
            await ctx.send("This command can only be used in the weather channel.")
            return

        try:
            weather_data = await get_weather(city, self.bot.http_session)
            await ctx.send(f"Weather in {city}: {weather_data['temp']}°C, {weather_data['description']}")
        except Exception as e:
            logger.error(f"Error in weather command: {e}")
            await ctx.send("Failed to fetch weather data.")

    @commands.command(name='translate')
    async def translate_command(self, ctx, target_lang: str, *, text: str):
        if ctx.channel.id != config.DISCORD_CHANNEL_2:
            await ctx.send("This command can only be used in the translation channel.")
            return

        try:
            translated_text = await translate_text(text, target_lang, self.bot.http_session)
            await ctx.send(f"Translated to {target_lang}: {translated_text}")
        except Exception as e:
            logger.error(f"Error in translate command: {e}")
            await ctx.send("Failed to translate text.")


async def setup(bot):
    await bot.add_cog(BotCommands(bot))