# TafseerBot

TafseerBot is a Discord bot built with Discord.py that provides Quranic ayahs, translations, random ayahs, tafseer, and the ability to change the Gregorian date to Hijri using slash commands. It also sends a daily verse to set channels on a server.

## Features

- **/quran**: Get specific Quranic verse and translation.
- **/rquran**: Get a random Quranic verse and its translation.
- **/tafseer**: Get detailed tafseer for specific verse.
- **/convertdate**: Change Gregorian date to Hijri.
- **/setdailyquranchannel**: Set channels to receive daily Quranic verse.
- **/setdailyqurantime**: Set time at which to receive daily Quranic verse.
- **/help**: Use help to see all the commands and their usage.

## Invite to Your Server
If you just want to Invite already setup Bot to your server.

Use this link: [INVITE](https://discord.com/oauth2/authorize?client_id=1201036808855752754&permissions=274881202176&scope=bot+applications.commands).

## Discord

Join Discord: https://discord.gg/tQaHnpnwXy
## Setup

Clone the repository:
```
git clone https://github.com/yourusername/TafseerBot.git
```
Install dependencies:
```
pip install -r requirements.txt
```
Set up a Discord bot and obtain the token.
Create a config.ini file in the root directory and add your bot token and database credentials:
```
Run the bot:
```
python main.py
```
Usage

Invite the bot to your Discord server.
Use slash commands (/quran, /rquran, /tafseer, /convertdate) to interact with the bot.
Set channel using the /setdailyquranchannel command to receive daily quranic verse.
and
Set time using the /setdailyqurantime command to set time at which set channel will receive quranic verse.

you can use /rmdailyquranchannel command to stop channel from receiving daily quranic verse.

Contributing

Contributions are welcome! If you have suggestions or want to contribute to the project, follow these steps:

Fork the repository.

Create a new branch (git checkout -b feature/yourfeature).

Make your changes.

Commit your changes (git commit -am 'Add new feature').

Push to the branch (git push origin feature/yourfeature).

Create a new Pull Request.

License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details.
