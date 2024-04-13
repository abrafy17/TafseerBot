import discord
import datetime
import requests

from utils.errors import error_handler
from utils.db import DB
from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color, translation_mapping
from discord import app_commands
from discord.ext import commands

class Quran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = DB()
        self.bot_avatar = bot_avatar
        self.timezone = set_timezone
        self.accent_color = accent_color
        self.confirmation_color = confirmation_color
        self.error_color = error_color
        self.translation_mapping = translation_mapping

    @discord.app_commands.command(name="quran", description="Sends Verse from the Quran.")
    @discord.app_commands.describe(verse="Enter the chapter and verse number (e.g. 1:1)")
    async def quran(self, interaction: discord.Interaction, *, verse: str):
        #await interaction.response.defer(thinking=True)

        server_id = interaction.guild_id
        translation_key = self.db.load_translation_from_db(server_id)
    
        current_time = datetime.datetime.now()
        
        if ":" not in verse:
            invalid_embed = discord.Embed(title = "Error!",description = "Please add ':' between Chapter and Verse, (e.g. 1:1)", color=self.error_color)
            await interaction.response.send_message(embed=invalid_embed)
            return

        try:
            chapter, verse = verse.split(':')
        except ValueError:
            error = discord.Embed(title = "Error!",description = "Failed to fetch data from the API. Please try again later", color=self.error_color)
            await interaction.response.send_message(embed=error)
            return

        verse_info = self.bring_verse(verse, interaction.guild_id)
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
        
    @discord.app_commands.command(name = "settranslation", description = "Set Translation for Quran Verse")
    @discord.app_commands.describe(title = "Enter the name of translation bengali, farsi, hindi, italian, japanese, malaysian, russian, spanish, urdu")
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.guild_only()
    async def settranslation(self, interaction: discord.Interaction, title: str):
        current_time = datetime.datetime.now(self.timezone)

        server_id = interaction.guild_id
        server_name = interaction.guild.name
        
        if title.lower() not in self.translation_mapping:
            set_translation_error_embed = discord.Embed(title="Error", description=f"**Invalid translation!** Please choose from Bengali, English, Farsi, Hindi, Italian, Japanese, Malaysian, Russian, Spanish and Urdu", color=self.error_color, timestamp=current_time)
            set_translation_error_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=set_translation_error_embed)
            return

        translation_key = self.translation_mapping[title.lower()]
        self.db.save_translation_to_db(server_id, translation_key)

        translation_language = title.capitalize()
    
        set_translation_confirmation_embed = discord.Embed(title="Confirmation", description=f"The current translation for `{server_name}` has been set to {translation_language}", color=self.confirmation_color, timestamp=current_time)
        set_translation_confirmation_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        await interaction.response.send_message(embed=set_translation_confirmation_embed)

    @discord.app_commands.command(name="translation", description="Current Translation for Quran Verse")
    @discord.app_commands.describe()
    async def translation(self, interaction: discord.Interaction):
        current_time = datetime.datetime.now(self.timezone)
        
        server_id = interaction.guild_id
        server_name = interaction.guild.name
        
        server_set_translation = self.db.load_translation_from_db(server_id)

        if server_set_translation:
            translation_language = server_set_translation
            translation_embed = discord.Embed(title="Current Translation", description=f"The current translation for `{server_name}` is set to {translation_language}", color=self.accent_color, timestamp=current_time)
        else:
            translation_embed = discord.Embed(title="Current Translation", description=f"No translation is set for `{server_name}`", color=self.error_color, timestamp=current_time)
            
        translation_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        await interaction.response.send_message(embed=translation_embed)

    def bring_verse(self, verse: int, server_id: int):

        server_set_translation = self.db.load_translation_from_db(server_id)
        current_time = datetime.datetime.now(self.timezone)

        url = f'http://api.alquran.cloud/ayah/{verse}/editions/quran-uthmani,{server_set_translation}'
        print(f"At {current_time}, Invoked Random Quran Verse API URL: {url}") #for debugging
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch verse data: {response.status_code}")
            return None 
        
        json_data = requests.get(url).json()

        verse_arabic = json_data['data'][0]['text']
        verse_translation = json_data['data'][1]['text']
        surah_name = json_data['data'][0]['surah']['englishName']
        surah_name_english = json_data['data'][0]['surah']['englishNameTranslation']
        translation_name_english = json_data['data'][1]['edition']['englishName']
        number_in_surah = json_data['data'][0]['numberInSurah']
        chapter_number = json_data['data'][0]['surah']['number']
        sajda = json_data['data'][0]['sajda']

        sajda_info = "Sajda is Wajib" if sajda else ""

        return {
            'verse_arabic': verse_arabic,
            'verse_translation': verse_translation,
            'surah_name': surah_name,
            'number_in_surah': number_in_surah,
            'surah_name_english': surah_name_english,
            'translation_name_english': translation_name_english,
            'chapter_number': chapter_number,
            'sajda_info': sajda_info
            }
    
    @quran.error
    @settranslation.error
    @translation.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await error_handler(interaction, error)

async def setup(bot):
    await bot.add_cog(Quran(bot))
