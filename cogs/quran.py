import discord
import datetime
import requests
import pytz

from discord import app_commands
from discord.ext import commands
from config.config import get_mysql_connection

class Quran(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_connection = get_mysql_connection()
        self.cursor = self.db_connection.cursor()
        self.bot_avatar = "https://i.postimg.cc/Dz4d7y7J/avatar.jpg"
        self.timezone = pytz.timezone('Asia/Karachi')
        self.accent_color = discord.Color(0x1624)
        self.confirmation_color = discord.Color.green()
        self.error_color = discord.Color.red()

    @discord.app_commands.command(name="quran", description="Sends Verse from the Quran.")
    @discord.app_commands.describe(verse="Enter the chapter and verse number (e.g. 1:1)")
    async def quran(self, interaction: discord.Interaction, *, verse: str):
        #await interaction.response.defer(thinking=True)

        server_id = interaction.guild_id
        translation_key = self.load_translation_from_db(server_id)
    
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
    @discord.app_commands.describe(title = "Enter the name of translation (e.g. urdu, english, filipino)")
    async def settranslation(self, interaction: discord.Interaction, title: str):
        server_id = interaction.guild_id
        current_time = datetime.datetime.now(self.timezone)
        
        translation_mapping = {
            'bengali' : 'bn.bengali',
            'english': 'en.sahih',
            'farsi' : 'fa.ghomshei',
            'hindi' : 'hi.farooq',
            'italian' : 'it.piccardo',
            'japanese' : 'ja.japanese',
            'malaysian' : 'my.ghazi',
            'russian' : 'ru.kuliev-alsaadi',
            'spanish' : 'es.garcia',
            'urdu': 'ur.jalandhry',
        }

        if title.lower() not in translation_mapping:
            set_translation_error_embed = discord.Embed(title="Error", description=f"Invalid translation. Please choose 'english', 'urdu', or 'filipino'", color=self.error_color, timestamp=current_time)
            set_translation_error_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=set_translation_error_embed)
            return

        translation_key = translation_mapping[title.lower()]
        self.save_translation_to_db(server_id, translation_key)

        translation_language = title.capitalize()
    
        set_translation_confirmation_embed = discord.Embed(title="Confirmation", description=f"Quran Translation set to {translation_language}", color=self.confirmation_color, timestamp=current_time)
        set_translation_confirmation_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        await interaction.response.send_message(embed=set_translation_confirmation_embed)

    @discord.app_commands.command(name="translation", description="Current Translation for Quran Verse")
    @discord.app_commands.describe()
    async def translation(self, interaction: discord.Interaction):
        current_time = datetime.datetime.now(self.timezone)
        
        server_id = interaction.guild_id if interaction.guild else None
        server_name = interaction.guild.name if interaction.guild else "this server"
        
        translation_key = self.load_translation_from_db(server_id)

        if translation_key:
            translation_language = translation_key.split("_")[0].capitalize()
            translation_embed = discord.Embed(title="Current Translation", description=f"The current translation for `{server_name}` is set to {translation_language}", color=self.accent_color, timestamp=current_time)
        else:
            translation_embed = discord.Embed(title="Current Translation", description=f"No translation is set for `{server_name}`", color=self.error_color, timestamp=current_time)
            
        translation_embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
        await interaction.response.send_message(embed=translation_embed)

    def bring_verse(self, verse: int, server_id: int):

        translation_key = self.load_translation_from_db(server_id)
        current_time = datetime.datetime.now(self.timezone)

        url = f'http://api.alquran.cloud/ayah/{verse}/editions/quran-uthmani,{translation_key}'
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
    
async def setup(bot):
    await bot.add_cog(Quran(bot))