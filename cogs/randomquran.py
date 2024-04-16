import discord
import datetime
import random

from utils.errors import error_handler
from utils.fetchquran import FetchQuran
from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color
from discord import app_commands
from discord.ext import commands

class RandomQuran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_avatar = bot_avatar
        self.timezone = set_timezone
        self.accent_color = accent_color
        self.confirmation_color = confirmation_color
        self.error_color = error_color
        self.fetch_quran = FetchQuran()

    @discord.app_commands.command(name="rquran", description="Sends Random Verse from the Quran")
    @discord.app_commands.describe()
    async def rquran(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        current_time = datetime.datetime.now(self.timezone)
        random_verse = random.randint(1, 6237)

        server_id = interaction.guild_id
        verse_info = await self.fetch_quran.fetch_quran(server_id=server_id, chapter=None, verse=random_verse)

        if verse_info:
            translation_name_english = verse_info['translation_name_english']
            embed = discord.Embed(
                title=f"Surah {verse_info['surah_name']} - {verse_info['surah_name_english']}",
                description=f"Al Quran {verse_info['chapter_number']}:{verse_info['number_in_surah']} \n\n{verse_info['verse_arabic']}\n\n**Translation:**\n{verse_info['verse_translation']}\n\n{verse_info['sajda_info']}",
                color=self.accent_color, timestamp=current_time)
            
            embed.set_footer(text=f"Translation by: {translation_name_english}", icon_url=self.bot_avatar)
            
            await interaction.followup.send(embed=embed)
        else:
            error_embed = discord.Embed(title="Error!", description="Failed to fetch verse information.",color=self.error_color)
            await interaction.followup.send(embed = error_embed)
    
    @rquran.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await error_handler(interaction, error)
       
async def setup(bot):
    await bot.add_cog(RandomQuran(bot))