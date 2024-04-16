import discord
import datetime
import requests
import html2text

from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color
from utils.errors import error_handler
from discord.ext import commands
from discord import app_commands

class Tafseer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_avatar = bot_avatar
        self.timezone = set_timezone
        self.accent_color = accent_color
        self.confirmation_color = confirmation_color
        self.error_color = error_color

    @discord.app_commands.command(name="tafseer", description="Get Tafseer of Ayah")
    @discord.app_commands.describe(chapter = "Chapter Number (1-114)", verse="Verse Number of Entered Chapter")
    async def tafseer(self, interaction: discord.Interaction, chapter:str, verse: str):
        chapter_number = chapter
        verse_number = verse
        current_time = datetime.datetime.now(self.timezone)
        url = f"https://api.quran.com/api/v4/tafsirs/169/by_ayah/{chapter_number}:{verse_number}"
        print(f"At {current_time.strftime('%H:%M %p on %d-%m-%Y')}, Invoked Random Quran Verse API URL: {url}")  # for debugging
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            tafseer_text = data['tafsir']['text']
            tafseer_name = data['tafsir']['resource_name']

            markdown_text = html2text.html2text(tafseer_text)

            chunks = [markdown_text[i:i + 1024] for i in range(0, len(markdown_text), 1024)]

            embeds = []
            remaining_text = ""

            for chunk in chunks:
                if len(remaining_text) + len(chunk) <= 1024:
                    remaining_text += chunk
                else:
                    embed = discord.Embed(title=f"Tafseer for Verse {verse}", color=self.accent_color, timestamp=current_time)
                    embed.add_field(name=f"", value=remaining_text, inline=False)
                    embed.set_footer(text=f"Tafseer by: {tafseer_name}", icon_url=self.bot_avatar)
                    embeds.append(embed)
                    remaining_text = chunk

            if remaining_text:
                final_embed = discord.Embed(title=f"Tafseer for verse {verse}", color=self.accent_color, timestamp=current_time)
                final_embed.add_field(name=f"", value=remaining_text, inline=False)
                final_embed.set_footer(text=f"Tafseer by: {tafseer_name}", icon_url=self.bot_avatar)
                embeds.append(final_embed)

            await interaction.response.send_message(embed=embeds[0])

            if len(embeds) > 1:
                for embed in embeds[1:]:
                    await interaction.followup.send(embed=embed)

        else:
            error_embed = discord.Embed(title="Error", description="Failed to fetch tafseer data.", color=self.error_color)
            await interaction.response.send_message(embed=error_embed)
            
    @tafseer.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await error_handler(interaction, error)

async def setup(bot):
    await bot.add_cog(Tafseer(bot))