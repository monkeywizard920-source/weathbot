import discord
import aiohttp
from discord.ext import commands
from core.config import config
from core.logger import logger


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        self.telegram_service = None
        self.http_session = None

    async def setup_hook(self):
        logger.info("Setting up Discord bot...")
        self.http_session = aiohttp.ClientSession()
        await self.load_extension("bot.commands")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def start(self):
        await super().start(config.DISCORD_TOKEN)

    async def close(self):
        if self.telegram_service:
            await self.telegram_service.stop()
        if self.http_session:
            await self.http_session.close()
        await super().close()
