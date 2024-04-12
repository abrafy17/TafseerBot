import discord
import requests
import pytz
import asyncio
import random
import datetime

from datetime import timedelta
from discord import app_commands
from discord.ext import commands
from config.config import get_mysql_connection
from cogs.quran import Quran


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
        self.quran_instance = Quran(bot)
        self.translation_mapping = {
            'bengali' : 'bn.bengali',
            'english' : 'en.sahih',
            'farsi' : 'fa.ghomshei',
            'hindi' : 'hi.farooq',
            'italian' : 'it.piccardo',
            'japanese' : 'ja.japanese',
            'malaysian' : 'my.ghazi',
            'russian' : 'ru.kuliev-alsaadi',
            'spanish' : 'es.garcia',
            'urdu': 'ur.jalandhry',
        }

    @discord.app_commands.command(name="dailyqurantime", description="Set Time for Daily Quran Verse")
    @discord.app_commands.describe(hour="Hour in 24hr Format", minute="Minute")
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def set_rq_time(self, interaction: discord.Interaction, hour: int, minute: int):

        server_id = interaction.guild_id
        current_time = datetime.datetime.now(self.timezone)


        try:
            set_time = datetime.time(hour, minute)
            time = set_time.strftime('%H:%M:00')

            self.save_time_to_db(server_id, time)
            embed = discord.Embed(title="Confirmation", description=f"The Daily Quran message time has been set to: {set_time.strftime('%I:%M %p')} ({self.timezone.zone})", color=self.confirmation_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        except ValueError:
            embed = discord.Embed(title="Confirmation", description="Invalid time format. Please provide valid hour and minute values in 24hr format", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="dailyquranchannel", description="Set current channel to receive daily  verse")
    @discord.app_commands.describe()
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def add_dailyquran_channel(self, interaction: discord.Interaction):

        server_id = interaction.guild_id
        channel_id = interaction.channel_id
        current_time = datetime.datetime.now(self.timezone)
        
        quran_channel = self.load_quran_channel_from_db(server_id)

        channel = self.bot.get_channel(channel_id) 
        channel_name = channel.name

        if quran_channel is None:
            self.save_quran_channel_to_db(server_id, channel_id)
            embed = discord.Embed(title="Confirmation", description=f"`{channel_name}` has been added to receive Daily Quran messages", color=self.confirmation_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Error", description=f"`{channel_name}` is already set to receive Daily Quran messages", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="rmdailyquranchannel", description=" Removes current channel from receiving daily verse")
    @discord.app_commands.describe()
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def rm_dailyquran_channel(self, interaction: discord.Interaction):

        server_id = interaction.guild_id
        channel_id = interaction.channel_id
        current_time = datetime.datetime.now(self.timezone)

        quran_channel = self.load_quran_channel_from_db(server_id)
        channel = self.bot.get_channel(channel_id)

        if quran_channel is not None and quran_channel == channel_id:
            self.drop_quran_channel_from_db(server_id)
            embed = discord.Embed(title="Confirmation", description=f"`{channel.name}` is removed from receive daily verse", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Error", description=f"`{channel.name}` is not set for not receiving daily verse", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
            
    @discord.app_commands.command(name="dailyquransettings", description="Shows the current setting for daily verse")
    @discord.app_commands.describe()
    async def settings(self, interaction: discord.Interaction):
        server_id = interaction.guild_id
        server_set_channel = self.load_quran_channel_from_db(server_id)
        server_set_times = self.load_time_from_db(server_id)
        server_set_translation = self.load_translation_from_db(server_id)

        current_time = datetime.datetime.now(self.timezone)
        
        if server_set_times is not None:
            set_time_formatted = server_set_times
        else:
            set_time_formatted = "No time set"
            
        if server_set_channel is None:
            channels_text = "No channel set"
        else: 
            channel_name = self.bot.get_channel(server_set_channel).name
            channels_text = f"`#{channel_name}`"
        
        if server_set_translation is None:
            translation_language = "No Translation Set"
        else:
            translation_language = server_set_translation
        
        embed = discord.Embed(title="Daily Quran Setting", colour=self.accent_color, timestamp=current_time)
        embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        embed.add_field(name="Translation:", value=f"{translation_language}", inline=False)
        embed.add_field(name="Channel:", value=f"{channels_text}", inline=False)
        embed.add_field(name="Time:", value=f"{set_time_formatted}", inline=False)
        
        await interaction.response.send_message(embed=embed)

    async def send_random_quran(self, interaction: discord.Interaction, channel, server_id):
        aya = random.randint(1, 6237)
        server_id = interaction.guild_id
        verse_info = self.quran_instance.bring_verse(aya, server_id)
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

    async def dailyquran(self, interaction: discord.Interaction):
        while True:
            now = datetime.datetime.now(self.timezone)
            
            server_id = interaction.guild_id
            quran_channels = self.load_quran_channel_from_db(server_id)
            server_set_times = self.load_time_to_db(server_id)
            last_sent_date = self.load_last_sent_time_from_db(server_id)

            for server_id, set_time in server_set_times.items():
                if now.hour == set_time.hour and now.minute == set_time.minute:
                    if server_id in quran_channels:
                        last_sent_date_server = last_sent_date.get(server_id)
                        if last_sent_date_server is None or last_sent_date_server.date() != now.date() or (last_sent_date_server.hour, last_sent_date_server.minute) != (set_time.hour, set_time.minute):
                            for channel_id in quran_channels:
                                channel = self.bot.get_channel(channel_id)
                                await self.send_random_quran(channel, server_id)
                            
                            last_sent_date = now
                            self.save_last_sent_time_to_db(server_id, last_sent_date)
            
            await asyncio.sleep(60)

    def save_translation_to_db(self, server_id: int, translation_key: str):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO translations (server_id, translation_key) VALUES (%s, %s)"
        val = (server_id, translation_key)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

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
        
    def save_time_to_db(self, server_id: int, set_time: datetime.time):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO time (server_id, set_time) VALUES (%s, %s)"
        val = (server_id, set_time)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

    def load_time_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT set_time FROM time WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None
        
    def save_quran_channel_to_db(self, server_id: int, quran_channel: int):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO channel (server_id, quran_channel) VALUES (%s, %s)"
        val = (server_id, quran_channel)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

    def drop_quran_channel_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "UPDATE channel SET quran_channel = NULL WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()


    def load_quran_channel_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT quran_channel FROM channel WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None
        
    def save_last_sent_time_to_db(self, server_id: int, last_sent_date: datetime.datetime):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO lastsent(server_id, last_sent_date) VALUES (%s, %s)"
        val = (server_id, last_sent_date)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

    def load_last_sent_time_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT last_sent_date FROM lastsent WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None

async def setup(bot):
    await bot.add_cog(DailyQuran(bot))