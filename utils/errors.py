import discord
import datetime
import mysql.connector
from mysql.connector import Error
import traceback

from enum import Enum
from discord.ext import commands
from discord.app_commands import MissingPermissions

class ErrorMessage(Enum):
    DATABASE_UNREACHABLE = "Unable to reach database. Please report to Administrator!"
    ADMINISTRATOR_REQUIRED = "You need the **Administrator** permission to use this command."
    OTHER_ERROR = "**An error occurred!** Please report to the Administrator!"

async def error_handler(interaction: discord.Interaction, error: Exception):
    try:
        if isinstance(error, mysql.connector.Error):
            await reply_to_interaction(interaction, ErrorMessage.DATABASE_UNREACHABLE.value)

        elif isinstance(error, MissingPermissions):
            await reply_to_interaction(interaction, ErrorMessage.ADMINISTRATOR_REQUIRED.value)

        else:
            raise error
    except:
        print("An undefined exception occurred:", repr(error))
        traceback.print_exc()
        await reply_to_interaction(interaction, ErrorMessage.OTHER_ERROR.value)

async def reply_to_interaction(interaction: discord.Interaction, message: str):
    if interaction.response.is_done():
        await interaction.followup.send(content=message)
    else:
        await interaction.response.send_message(content=message)
