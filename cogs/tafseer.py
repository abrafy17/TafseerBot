# tafseer.py
import discord
import datetime
import requests
import html2text
import pytz

from discord.ext import commands
from discord import app_commands

class Tafseer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_avatar = "https://i.postimg.cc/Dz4d7y7J/avatar.jpg"
        self.timezone = pytz.timezone('Asia/Karachi')
        self.accent_color = discord.Color(0x1624)
        self.confirmation_color = discord.Color.green()
        self.error_color = discord.Color.red()

    @discord.app_commands.command(name="tafseer", description="Get Tafseer of Ayah")
    @discord.app_commands.describe(verse="Enter Chapter:Verse to get Tafseer of Verse (e.g. 1:1)")
    async def tafseer(self, interaction: discord.Interaction, verse: str):
        chapter, verse_number = verse.split(":")
        current_time = datetime.datetime.now(self.timezone)
        url = f"https://api.quran.com/api/v4/tafsirs/169/by_ayah/{chapter}:{verse_number}"
        print(f"At {current_time}, Invoked Random Quran Verse API URL: {url}")  # for debugging
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

async def setup(bot):
    await bot.add_cog(Tafseer(bot))