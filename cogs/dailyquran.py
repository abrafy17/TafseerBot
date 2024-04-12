import discord
import datetime
import requests
import pytz
import asyncio
import random

from discord import app_commands
from discord.ext import commands
from config.config import get_mysql_connection
from cogs.randomquran import bring_verse


class DailyQuran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_connection = get_mysql_connection()
        self.cursor = self.db_connection.cursor()
        self.bot_avatar = "https://i.postimg.cc/Dz4d7y7J/avatar.jpg"
        self.timezone = pytz.timezone('Asia/Karachi')
        self.accent_color = discord.Color(0x1624)
        self.confirmation_color = discord.Color.green()
        self.error_color = discord.Color.red()
        self.bring_verse = bring_verse()

    @discord.app_commands.command(name="setrqtranslation", description="Sets Translation for Random Quran")
    @discord.app_commands.describe(translation_name="Name of the Translation")
    async def set_rq_translation(self, interaction: discord.Interaction, translation_name: str):
        # Your setrqtranslation command logic here

    @discord.app_commands.command(name="setrqtime", description="Sets Time for Daily Quran Verse")
    @discord.app_commands.describe(hour="Hour in 24hr Format", minute="Minute")
    async def set_rq_time(self, interaction: discord.Interaction, hour: int, minute: int):
        # Your setrqtime command logic here

    @discord.app_commands.command(name="setrqchannel", description="Sets This Channel to Receive Daily Quran verse")
    async def set_rq_channel(self, interaction: discord.Interaction):
        # Your setrqchannel command logic here

    @discord.app_commands.command(name="settings", description="Shows the current setting for Daily Quran")
    async def settings(self, interaction: discord.Interaction):
        # Your settings command logic here

    async def dailyquran(self):
        while True:
            now = datetime.datetime.now(self.timezone)
            
            for server_id, set_time in server_set_times.items():
                if now.hour == set_time.hour and now.minute == set_time.minute:
                    if server_id in quran_channels:
                        last_sent_date_server = last_sent_date.get(server_id)
                        if last_sent_date_server is None or last_sent_date_server.date() != now.date() or (last_sent_date_server.hour, last_sent_date_server.minute) != (set_time.hour, set_time.minute):
                            for channel_id in quran_channels[server_id]:
                                channel = bot.get_channel(channel_id)
                                await self.send_random_quran(channel, server_id)
                            
                            last_sent_date[server_id] = now
            
            await asyncio.sleep(60)

    async def send_random_quran(self, channel, server_id):
        aya = random.randint(1, 6237)
        verse_info = self.bring_verse(aya, server_id)
        if verse_info:
            current_time = datetime.datetime.now(self.timezone)
            translation_name_english = verse_info['translation_name_english']
            embed = discord.Embed(
                title=f"Surah {verse_info['surah_name']} - {verse_info['surah_name_english']}",
                description=f"({verse_info['chapter_number']}:{verse_info['number_in_surah']}) \n\n{verse_info['verse_arabic']}\n\n**Translation:**\n{verse_info['verse_translation']}\n\n{verse_info['sajda_info']}",
                color=self.accent_color, timestamp=current_time)
            
            embed.set_footer(text=f"Translation by: {translation_name_english}", icon_url=self.bot_avatar)
            
            await channel.send(embed=embed)
        else:
            error_embed = discord.Embed(title="Error!", description="Failed to fetch verse information.", color=self.error_color)
            await channel.send(embed = error_embed)

async def setup(bot):
    await bot.add_cog(DailyQuran(bot))