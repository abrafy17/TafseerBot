import discord
import datetime
import requests
import random
import pytz

from discord import app_commands
from discord.ext import commands
from config.config import get_mysql_connection
from cogs.quran import Quran


class RandomQuran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_connection = get_mysql_connection()
        self.cursor = self.db_connection.cursor()
        self.bot_avatar = "https://i.postimg.cc/Dz4d7y7J/avatar.jpg"
        self.timezone = pytz.timezone('Asia/Karachi')
        self.accent_color = discord.Color(0x1624)
        self.confirmation_color = discord.Color.green()
        self.error_color = discord.Color.red()
        self.quran_instance = Quran(bot)

    @discord.app_commands.command(name="rquran", description="Sends Random Verse from the Quran")
    @discord.app_commands.describe()
    async def rquran(self, interaction: discord.Interaction):
        current_time = datetime.datetime.now(self.timezone)
        aya = random.randint(1, 6237)
        guild_id = interaction.guild_id
        verse_info = self.quran_instance.bring_verse(aya, guild_id)
        if verse_info:
            translation_name_english = verse_info['translation_name_english']
            embed = discord.Embed(
                title=f"Surah {verse_info['surah_name']} - {verse_info['surah_name_english']}",
                description=f"Al Quran {verse_info['chapter_number']}:{verse_info['number_in_surah']} \n\n{verse_info['verse_arabic']}\n\n**Translation:**\n{verse_info['verse_translation']}\n\n{verse_info['sajda_info']}",
                color=self.accent_color, timestamp=current_time)
            
            embed.set_footer(text=f"Translation by: {translation_name_english}", icon_url=self.bot_avatar)
            
            await interaction.response.send_message(embed=embed)
        else:
            error_embed = discord.Embed(title="Error!", description="Failed to fetch verse information.",color=self.error_color)
            await interaction.response.send_message(embed = error_embed)

    def load_translation_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT translation_key FROM translations WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None
        
async def setup(bot):
    await bot.add_cog(RandomQuran(bot))