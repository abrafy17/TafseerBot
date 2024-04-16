import discord
import configparser

from discord.ext import commands
from cogs.dailyquran import DailyQuran

config = configparser.ConfigParser()
config.read('config.ini')

token = config['TafseerBot']['token']

description = "TafseerBot"

intents = discord.Intents.all()

class TafseerBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix='^', description=description, case_insensitive=True, intents=intents, activity = discord.Activity(type=discord.ActivityType.watching, name="/help"))
        self.dailyquran_cog = DailyQuran(self)
        self.initial_extensions = [
            "cogs.quran",
            "cogs.randomquran",
            "cogs.tafseer",
            "cogs.convertdate",
            "cogs.dailyquran",
            "cogs.help"
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
