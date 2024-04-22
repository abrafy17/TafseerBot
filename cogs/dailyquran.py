import discord
import requests
import asyncio
import random
import datetime

from utils.fetchquran import FetchQuran
from utils.database import DailyQuranTime, DailyQuranChannel, ServerSetTranslation
from utils.errors import error_handler
from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color, translation_mapping
from discord import app_commands
from discord.ext import commands, tasks


class DailyQuran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_avatar = bot_avatar
        self.timezone = set_timezone
        self.accent_color = accent_color
        self.confirmation_color = confirmation_color
        self.error_color = error_color
        self.translation_mapping = translation_mapping
        self.fetchquran = FetchQuran()
        #self.dailyquran.start()

    @discord.app_commands.command(name="setdailyqurantime", description="Set Time for Daily Quran")
    @discord.app_commands.describe(hour="Hour in 24hr Format", minute="Minute")
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def set_dailyquran_time(self, interaction: discord.Interaction, hour: int, minute: int):

        server_id = interaction.guild_id
        current_time = datetime.datetime.now(self.timezone)
        servertime = DailyQuranTime(server_id)

        try:
                set_time = datetime.time(hour, minute)
                time = set_time.strftime('%H:%M')

                await servertime.save(time)
                embed = discord.Embed(title="Confirmation", description=f"The Daily Quran time has been set to: {set_time.strftime('%I:%M %p')}", color=self.confirmation_color, timestamp=current_time)
                embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
                await interaction.response.send_message(embed=embed)
        except ValueError:
                embed = discord.Embed(title="Confirmation", description="Invalid time format. Please provide valid hour and minute values in 24hr format", color=self.error_color, timestamp=current_time)
                embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
                await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="setdailyquranchannel", description="Set Current Channel for Receiving Daily Quran")
    @discord.app_commands.describe()
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def set_dailyquran_channel(self, interaction: discord.Interaction):

        server_id = interaction.guild_id
        channel_id = interaction.channel_id
        current_time = datetime.datetime.now(self.timezone)
        serverchannel = DailyQuranChannel(server_id)
        
        quran_channel = await serverchannel.load()
    
        if quran_channel is None or quran_channel != channel_id: 
            await serverchannel.save(channel_id)
            channel_name = self.bot.get_channel(channel_id).name
            embed = discord.Embed(title="Confirmation", description=f"`{channel_name}` has been added to receive Daily Quran Verse", color=self.confirmation_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        else:
            channel_name = self.bot.get_channel(quran_channel).name 
            embed = discord.Embed(title="Error", description=f"`{channel_name}` is already set to receive Daily Quran Verse", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="rmdailyquranchannel", description=" Removes Current Channel from receiving Daily Quran")
    @discord.app_commands.describe()
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def rm_dailyquran_channel(self, interaction: discord.Interaction):

        server_id = interaction.guild_id
        channel_id = interaction.channel_id
        current_time = datetime.datetime.now(self.timezone)
        serverchannel = DailyQuranChannel(server_id)

        quran_channel = await serverchannel.load()
        channel = self.bot.get_channel(channel_id)

        if quran_channel is not None and quran_channel == channel_id:
            await serverchannel.delete()
            embed = discord.Embed(title="Confirmation", description=f"`{channel.name}` has been removed from receiving Daily Quran Verse", color=self.confirmation_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Error", description=f"`{channel.name}` is not set for receiving Daily Quran Verse", color=self.error_color, timestamp=current_time)
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
            
    @discord.app_commands.command(name="dailyquransettings", description="Shows Current settings for Daily Quran")
    @discord.app_commands.describe()
    async def settings(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        server_id = interaction.guild_id

        server_translation = ServerSetTranslation(server_id)
        server_time = DailyQuranTime(server_id)
        server_channel = DailyQuranChannel(server_id)

        server_set_translation = await server_translation.load()
        server_set_time = await server_time.load()
        server_set_channel = await server_channel.load()

        current_time = datetime.datetime.now(self.timezone)

        if not server_set_time:
            time = "No time set"
        else:
            set_time = server_set_time
            datetime_time = datetime.datetime.strptime(set_time, "%H:%M")
            time = datetime_time.strftime('%I:%M %p')

        if server_set_channel is None:
            channels_text = "No channel set"
        else:
            channels_text = self.bot.get_channel(server_set_channel)

        if not server_set_translation:
            translation_language = "Default: English"
        else:
            reverse_translation_mapping = {v: k for k, v in self.translation_mapping.items()}
            translation_language = server_set_translation
            translation_name = reverse_translation_mapping.get(translation_language, "English").capitalize()

        embed = discord.Embed(title="Daily Quran Settings", colour=self.accent_color, timestamp=current_time)
        embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        embed.add_field(name="Current Set Translation:", value=f"{translation_name}", inline=False)
        embed.add_field(name="Current Set Channel:", value=f"`{channels_text}`", inline=False)
        embed.add_field(name="Current Set Time:", value=f"{time}", inline=False)

        await interaction.followup.send(embed=embed)

    async def send_random_quran(self, interaction: discord.Interaction, channel, server_id):
        random_verse = random.randint(1, 6237)
        verse_info = await self.fetchquran.fetch_quran(server_id=server_id, chapter=None, verse=random_verse)
        
        if verse_info:
            current_time = datetime.datetime.now(self.timezone)
            translation_name_english = verse_info['translation_name_english']
            embed = discord.Embed(
                title=f"Surah {verse_info['surah_name']} - {verse_info['surah_name_english']}",
                description=f"Al Quran {verse_info['chapter_number']}:{verse_info['number_in_surah']} \n\n{verse_info['verse_arabic']}\n\n**Translation:**\n{verse_info['verse_translation']}\n\n{verse_info['sajda_info']}",
                color=self.accent_color, timestamp=current_time)

            embed.set_footer(text=f"Translation by: {translation_name_english}", icon_url=self.bot_avatar)

            await channel.send(embed=embed)
        else:
            error_embed = discord.Embed(title="Error!", description="Failed to fetch verse information.", color=self.error_color)
            await channel.send(embed = error_embed)

    async def dailyquran(self):
        while True:
            now = datetime.datetime.now(self.timezone)

            interactions = []
            async for guild in self.bot.fetch_guilds(limit=None):
                interactions.append(guild)

            for interaction in interactions:
                server_id = interaction.id 
        
                server_time = DailyQuranTime(server_id)
                server_channel = DailyQuranChannel(server_id)

                channel_id = await server_channel.load()
                channel = self.bot.get_channel(channel_id)
                set_time_str = await server_time.load()

                if channel is not None and set_time_str and set_time_str.strip():
                    hours, minutes = map(int, set_time_str.split(':'))
                    set_time_datetime = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)

                    current_time_formatted = now.strftime("%H:%M")
                    set_time_formatted = set_time_datetime.strftime("%H:%M")

                    if current_time_formatted == set_time_formatted:
                        await self.send_random_quran(interaction= discord.Interaction, channel= channel, server_id= server_id)
                else:
                    print(f"Time is: {now.strftime('%I:%M %p, %d-%m-%Y')}")

            await asyncio.sleep(60 - now.second)


    @set_dailyquran_channel.error
    @set_dailyquran_time.error
    @rm_dailyquran_channel.error
    @settings.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await error_handler(interaction, error)

async def setup(bot):
    await bot.add_cog(DailyQuran(bot))