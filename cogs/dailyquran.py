import discord
import requests
import asyncio
import random
import datetime

from utils.db import DB
from utils.errors import error_handler
from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color, translation_mapping
from discord import app_commands
from discord.ext import commands
from cogs.quran import Quran


class DailyQuran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = DB()
        self.bot_avatar = bot_avatar
        self.timezone = set_timezone
        self.accent_color = accent_color
        self.confirmation_color = confirmation_color
        self.error_color = error_color
        self.quran_instance = Quran(bot)
        self.translation_mapping = translation_mapping

    @discord.app_commands.command(name="setdailyqurantime", description="Set Time for Daily Quran Verse")
    @discord.app_commands.describe(hour="Hour in 24hr Format", minute="Minute")
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def set_dailyquran_time(self, interaction: discord.Interaction, hour: int, minute: int):

        server_id = interaction.guild_id
        current_time = datetime.datetime.now(self.timezone)

        try:
                set_time = datetime.time(hour, minute)
                time = set_time.strftime('%H:%M:00')

                self.db.save_time_to_db(server_id, time)
                embed = discord.Embed(title="Confirmation", description=f"The Daily Quran Verse time has been set to: {set_time.strftime('%I:%M %p')}", color=self.confirmation_color, timestamp=current_time)
                embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
                await interaction.response.send_message(embed=embed)
        except ValueError:
                embed = discord.Embed(title="Confirmation", description="Invalid time format. Please provide valid hour and minute values in 24hr format", color=self.error_color, timestamp=current_time)
                embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
                await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="setdailyquranchannel", description="Set Current Channel for Receiving Daily Quran Verse")
    @discord.app_commands.describe()
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def set_dailyquran_channel(self, interaction: discord.Interaction):

        server_id = interaction.guild_id
        channel_id = interaction.channel_id
        current_time = datetime.datetime.now(self.timezone)
        
        quran_channel = self.db.load_quran_channel_from_db(server_id)

        channel = self.bot.get_channel(channel_id) 
        channel_name = channel.name

        if quran_channel is None:
            self.db.save_quran_channel_to_db(server_id, channel_id)
            embed = discord.Embed(title="Confirmation", description=f"`{channel_name}` has been added to receive Daily Quran Verse", color=self.confirmation_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Error", description=f"`{channel_name}` is already set to receive Daily Quran Verse", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="rmdailyquranchannel", description=" Removes Current Channel from receiving Daily Quran Verse")
    @discord.app_commands.describe()
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def rm_dailyquran_channel(self, interaction: discord.Interaction):

        server_id = interaction.guild_id
        channel_id = interaction.channel_id
        current_time = datetime.datetime.now(self.timezone)

        quran_channel = self.db.load_quran_channel_from_db(server_id)
        channel = self.bot.get_channel(channel_id)

        if quran_channel is not None and quran_channel == channel_id:
            self.db.drop_quran_channel_from_db(server_id)
            embed = discord.Embed(title="Confirmation", description=f"`{channel.name}` has been removed from receive Daily Quran Verse", color=self.confirmation_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Error", description=f"`{channel.name}` is already not set for receiving Daily Quran Verse", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
            
    @discord.app_commands.command(name="dailyquransettings", description="Shows Current settings for Daily Quran Verse")
    @discord.app_commands.describe()
    async def settings(self, interaction: discord.Interaction):
        server_id = interaction.guild_id
        server_set_channel = self.db.load_quran_channel_from_db(server_id)
        server_set_times = self.db.load_time_from_db(server_id)
        server_set_translation = self.db.load_translation_from_db(server_id)

        current_time = datetime.datetime.now(self.timezone)
        
        if server_set_times is not None:
            set_time = server_set_times
        else:
            set_time = "No time set"
            
        if server_set_channel is None:
            channels_text = "No channel set"
        else: 
            channel_name = self.bot.get_channel(server_set_channel).name
            channels_text = f"`#{channel_name}`"
        
        if server_set_translation is None:
            translation_language = "No Translation Set"
        else:
            translation_language = server_set_translation
        
        embed = discord.Embed(title="Daily Quran Verse Setting", colour=self.accent_color, timestamp=current_time)
        embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        embed.add_field(name="Current Set Translation:", value=f"{translation_language}", inline=False)
        embed.add_field(name="Current Set Channel:", value=f"{channels_text}", inline=False)
        embed.add_field(name="Current Set Time:", value=f"{set_time}", inline=False)
        
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
            quran_channels = self.db.load_quran_channel_from_db(server_id)
            server_set_times = self.db.load_time_to_db(server_id)
            last_sent_date = self.db.load_last_sent_time_from_db(server_id)

            for server_id, set_time in server_set_times.items():
                if now.hour == set_time.hour and now.minute == set_time.minute:
                    if server_id in quran_channels:
                        last_sent_date_server = last_sent_date.get(server_id)
                        if last_sent_date_server is None or last_sent_date_server.date() != now.date() or (last_sent_date_server.hour, last_sent_date_server.minute) != (set_time.hour, set_time.minute):
                            for channel_id in quran_channels:
                                channel = self.bot.get_channel(channel_id)
                                await self.send_random_quran(channel, server_id)
                            
                            last_sent_date = now
                            self.db.save_last_sent_time_to_db(server_id, last_sent_date)
            
            await asyncio.sleep(60)

    @set_dailyquran_channel.error
    @set_dailyquran_time.error
    @rm_dailyquran_channel.error
    @settings.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await error_handler(interaction, error)

async def setup(bot):
    await bot.add_cog(DailyQuran(bot))