import discord
import pytz

set_timezone = pytz.timezone('Asia/Karachi')

#Bot Icon
bot_avatar = "https://i.postimg.cc/Dz4d7y7J/avatar.jpg"

#Colors 
accent_color = discord.Color(0x1624)
confirmation_color = discord.Color.green()
error_color = discord.Color.red()

#Mappings
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