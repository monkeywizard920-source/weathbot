import discord
from discord.ext import commands
from core.config import config
from core.logger import logger


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        self.telegram_service = None

    async def setup_hook(self):
        logger.info("Setting up Discord bot...")
        await self.load_extension("bot.commands")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def start(self):
        await super().start(config.DISCORD_TOKEN)

    async def close(self):
        if self.telegram_service:
            await self.telegram_service.stop()
        await super().close()
