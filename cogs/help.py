import discord

from discord import SelectOption
from discord.ext import commands
from utils.gui import set_timezone, bot_avatar, accent_color, confirmation_color, error_color

SELECT_OPTIONS = [
    SelectOption(label="Quran", value="quran", description="View help for Quran commands"),
    SelectOption(label="Tafseer", value="tafseer", description="View help for Tafseer commands"),
    SelectOption(label="Convert Date", value="convertdate", description="View help for Convert Date commands"),
    SelectOption(label="Daily Quran", value="dailyquran", description="View help for Daily Quran commands")
]

class HelpMenu(discord.ui.View):
    def __init__(self, *args, interaction: discord.Interaction, **kwargs):
        super().__init__(timeout=600)
        self.latest_interaction = interaction

    async def interaction_check(self, interaction: discord.Interaction):
        result = await super().interaction_check(interaction)
        self.latest_interaction = interaction
        if not result:
            await interaction.response.defer()
        return result

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.latest_interaction.edit_original_response(view=self, content=":warning: This message has timed out.")


    @discord.ui.select(custom_id="tafseerbot:help", placeholder="Select a help topic", options=SELECT_OPTIONS)
    async def select_callback(self, interaction: discord.Integration, menu: discord.ui.Select):
        option = menu.values[0]

        if option == "quran":
            embed = discord.Embed(title="Quran", color=accent_color, description="Quran")
            embed.add_field(name="/quran", inline=True, value="Get Quranic verses"
                            "\n\n`/quran <surah> <verse>`"
                            "\n\nExample: `/quran 32 7`")
            
            embed.add_field(name="/rquran", inline=True, value="Get a Random Quranic Verse"
                            "\n\n`/rquran`")
            
            embed.add_field(name="/settranslation", inline=True, value="Change the Quran translation for server"
                            "\n\n`/settransaltion <translation>`"
                            "\n\nExample `/settranslation Urdu`")
            
            embed.add_field(name="/translation", inline=True, value="Shows the Current Set Translation for Server"
                            "\n\n`/translation`")
            
            await interaction.response.edit_message(embed=embed)

        elif option == "tafseer":
            embed = discord.Embed(title="Tafseer", color=accent_color, description="Tafseer")
            embed.add_field(name="/tafseer", inline=True, value="Get Tafseer of Quranic verses"
                            "\n\n`/tafseer <surah> <verse>`"
                            "\n\nExample: `/tafseer 2 17`")
            
            await interaction.response.edit_message(embed=embed)
            
        elif option == "convertdate":
            embed = discord.Embed(title="Convert Date", color=accent_color, description="Convert Date")
            embed.add_field(name="/convertdate", inline=True, value="Get Hijri Date"
                            "\n\n`/convertdate <date>`"
                            "\n\nExample: `/convertdate 29-8-2024`")
            
        elif option == "dailyquran":
            embed = discord.Embed(title="Daily Quran", color=accent_color, description="Daily Quran")
            embed.add_field(name="/dailyquransettings", inline=True, value="Get Current Set Setting of Daily Quran"
                            "\n\n`/dailyquransettings`")
            
            embed.add_field(name="/setdailyquranchannel", inline=True, value="Set Current Channel to Receive Daily Quran Verse"
                            "\n\n`/setdailyquranchannel`")
            
            embed.add_field(name="/rmdailyquranchannel", inline=True, value="Removes Current Channel from Receiving Daily Quran Verse"
                            "\n\n`/rmdailyquranchannel`"
                            "\n\nExample `/settranslation Urdu`")
            
            embed.add_field(name="/setdailyqurantime", inline=True, value="Sets Time at which Channel will Receive Daily Quran Verse, Use's 24Hr Format"
                            "\n\n`/setdailyqurantime <hour> <minute>`"
                            "\n\nExample: `/setdailyqurantime 14 30`")
            
            await interaction.response.edit_message(embed=embed)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="help", description="Get the list of commands for TafseerBot")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="TafseerBot Help", color=accent_color)
        embed.description = "**TafseerBot** is a Discord bot built with Discord.py that provides Quranic Verse, Translations of Verse, Random Quranic Verse, Tafseer, and the ability to change the Gregorian date to Hijri all using slash commands."
        embed.set_thumbnail(url=bot_avatar)

        await interaction.response.send_message(embed=embed, view=HelpMenu(interaction=interaction), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))

    
