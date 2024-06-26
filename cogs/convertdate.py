import discord
import datetime

from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color
from utils.errors import error_handler
from hijridate import Hijri, Gregorian
from discord.ext import commands
from discord import app_commands

class ConvertDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_avatar = bot_avatar
        self.timezone = set_timezone
        self.accent_color = accent_color
        self.confirmation_color = confirmation_color
        self.error_color = error_color
        
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
        
            embed = discord.Embed(title="Date Conversion", color=self.accent_color, timestamp=current_time)
            embed.add_field(name="Gregorian Date", value=f"{date}", inline=True)
            embed.add_field(name="Hijri Date", value=f"{hijri_date_formatted}", inline=True)
            embed.set_thumbnail(url="https://icons.iconarchive.com/icons/microsoft/fluentui-emoji-3d/256/Spiral-Calendar-3d-icon.png")
            embed.set_footer(text="TafseerBot", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=embed)
        except ValueError:
            error = discord.Embed(title="Error", description="Please provide the date in the format 'YYYY-MM-DD'", color=self.error_color, timestamp=current_time)
            error.set_footer(text="TafseerBot", icon_url=self.bot_avatar)
            await interaction.response.send_message(embed=error)

    @convertdate.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await error_handler(interaction, error)

async def setup(bot):
    await bot.add_cog(ConvertDate(bot))
