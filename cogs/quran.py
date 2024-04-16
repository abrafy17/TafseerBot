import discord
import datetime
import requests

from utils.errors import error_handler
from utils.fetchquran import FetchQuran
from utils.database import ServerSetTransaltion
from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color, translation_mapping
from discord import app_commands
from discord.ext import commands

class Quran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_avatar = bot_avatar
        self.timezone = set_timezone
        self.accent_color = accent_color
        self.confirmation_color = confirmation_color
        self.error_color = error_color
        self.translation_mapping = translation_mapping
        self.fetchquran = FetchQuran()

    @discord.app_commands.command(name="quran", description="Sends Verse from the Quran.")
    @discord.app_commands.describe(chapter= "Chapter Number (1-114)", verse="Verse Number from Entered Chapter")
    async def quran(self, interaction: discord.Interaction, chapter: str, verse: str):
        await interaction.response.defer(thinking=True)

        server_id = interaction.guild_id
        current_time = datetime.datetime.now()

        verse_info = await self.fetchquran.fetch_quran(server_id=server_id, chapter=chapter, verse=verse)
        
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
        
    @discord.app_commands.command(name = "settranslation", description = "Set Translation for Quranic Verse")
    @discord.app_commands.describe(title = "Enter the name of translation bengali, farsi, hindi, italian, japanese, malaysian, russian, spanish, urdu")
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def settranslation(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer(thinking=True)
        current_time = datetime.datetime.now(self.timezone)

        server_id = interaction.guild_id
        server_name = interaction.guild.name
        servertranslation = ServerSetTransaltion(server_id)

        if title.lower() not in self.translation_mapping:
            set_translation_error_embed = discord.Embed(title="Error", description=f"**Invalid translation!** Please choose from Bengali, English, Farsi, Hindi, Italian, Japanese, Malaysian, Russian, Spanish and Urdu", color=self.error_color, timestamp=current_time)
            set_translation_error_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.followup.send(embed=set_translation_error_embed)
            return
        
        else:

            translation = self.translation_mapping[title.lower()]
            await servertranslation.save(translation)

            translation_language = title.capitalize()
        
            set_translation_confirmation_embed = discord.Embed(title="Confirmation", description=f"The current translation for `{server_name}` has been set to {translation_language}", color=self.confirmation_color, timestamp=current_time)
            set_translation_confirmation_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.followup.send(embed=set_translation_confirmation_embed)

    @discord.app_commands.command(name="translation", description="Current Translation for Quranic Verse")
    @discord.app_commands.describe()
    async def translation(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        current_time = datetime.datetime.now(self.timezone)
        
        server_id = interaction.guild_id
        server_name = interaction.guild.name
        servertranslation = ServerSetTransaltion(server_id)
        
        server_set_translation = await servertranslation.load()

        reverse_translation_mapping = {v: k for k, v in self.translation_mapping.items()}

        translation_language = server_set_translation
        translation_name = reverse_translation_mapping.get(translation_language, "English").capitalize()

        translation_embed = discord.Embed(title="Current Translation", description=f"The current translation for `{server_name}` is set to {translation_name}", color=self.accent_color, timestamp=current_time)
        translation_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        await interaction.followup.send(embed=translation_embed)

    @quran.error
    @settranslation.error
    @translation.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await error_handler(interaction, error)

async def setup(bot):
    await bot.add_cog(Quran(bot))
