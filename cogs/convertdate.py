# convertdate.py
import discord
import datetime
import pytz

from hijridate import Hijri, Gregorian
from discord.ext import commands
from discord import app_commands

class ConvertDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_avatar = "https://i.postimg.cc/Dz4d7y7J/avatar.jpg"
        self.timezone = pytz.timezone('Asia/Karachi')
        self.accent_color = discord.Color(0x1624)
        self.confirmation_color = discord.Color.green()
        self.error_color = discord.Color.red()

    @discord.app_commands.command(name="convertdate", description="Convert date to Hijri")
    @discord.app_commands.describe(date="Enter the date you want to convert to Hijri (e.g. DD-MM-YYYY)")
    async def convertdate(self, interaction: discord.Interaction, *, date: str):
        current_time = datetime.datetime.now(self.timezone)
        try:
            day, month, year = map(int, date.split('-'))
        
            hijri_date = Gregorian(year, month, day).to_hijri()
            hijri_month_name = hijri_date.month_name()
            hijri_notation = hijri_date.notation()
            hijri_date_formatted = f"{hijri_date.dmyformat('-')}{hijri_notation} \n ({hijri_month_name})"
        
            embed = discord.Embed(title="Assalam O Alaikum", color=self.accent_color, timestamp=current_time)
            embed.add_field(name="Entered date", value=f"{date}", inline=True)
            embed.add_field(name="Hijri date", value=f"{hijri_date_formatted}", inline=True)
            embed.set_thumbnail(url="https://icons.iconarchive.com/icons/paomedia/small-n-flat/512/calendar-icon.png")
            embed.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        except ValueError:
            error = discord.Embed(title="Error", description="Please provide the date in the format 'YYYY-MM-DD'", color=self.error_color, timestamp=current_time)
            error.set_footer(text="Jazak Allah", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=error)

async def setup(bot):
    await bot.add_cog(ConvertDate(bot))
