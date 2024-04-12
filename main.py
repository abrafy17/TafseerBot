import discord

from discord.ext import commands
from config.config import TOKEN

token = TOKEN
description = "TafseerBot"

intents = discord.Intents.all()

class TafseerBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix='^', description=description, case_insensitive=True, intents=intents)
        self.initial_extensions = [
            "cogs.quran",
            "cogs.randomquran",
            "cogs.tafseer",
            "cogs.convertdate"
        ]
    
    async def setup_hook(self):
        for ext in self.initial_extensions:
            if ext not in self.extensions:
                await self.load_extension(ext)
    
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id}) on {len(self.guilds)} servers')
        synced = await self.tree.sync()
        #await bot.tree.sync(guild=None)
        await self.setup_hook()
        print("Slash CMDs Synced " + str(len(synced)) + " commands")

bot = TafseerBot()
bot.run(token)
