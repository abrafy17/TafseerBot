```yaml
embed:
  title: TafseerBot
  description: "TafseerBot is a Discord bot built with Discord.py that provides Quranic ayahs, translations, random ayahs, tafseer, and the ability to change the Gregorian date to Hijri using slash commands. It also sends a daily verse to set channels on a server."
  fields:
    - name: Features
      value: |
        - **/quran**: Get a specific Quranic verse and translation.
        - **/rquran**: Get a random Quranic verse and its translation.
        - **/tafseer**: Get detailed tafseer for a specific verse.
        - **/convertdate**: Change Gregorian date to Hijri.
        - **/setdailyquranchannel**: Set channels to receive the daily Quranic verse.
        - **/setdailyqurantime**: Set the time at which to receive the daily Quranic verse.
        - **/help**: Use help to see all the commands and their usage.
    - name: Invite to Your Server
      value: "If you want to invite the already setup Bot to your server, use this link: [INVITE](https://discord.com/oauth2/authorize?client_id=1201036808855752754&permissions=274881202176&scope=bot+applications.commands)."
    - name: Discord
      value: "Join our Discord community: [Discord Invite Link](https://discord.gg/tQaHnpnwXy)"
    - name: Setup
      value: |
        1. Clone the repository:
           ```
           git clone https://github.com/yourusername/TafseerBot.git
           ```
        2. Install dependencies:
           ```
           pip install -r requirements.txt
           ```
        3. Set up a Discord bot and obtain the token.
        4. Create a `config.ini` file in the root directory and add your bot token and database credentials:
           ```ini
           [Discord]
           bot_token = your_bot_token_here

           [MySQL]
           host = your_host
           user = your_user
           password = your_password
           database = your_database
           ```
        5. Run the bot:
           ```
           python main.py
           ```
    - name: Usage
      value: |
        1. Invite the bot to your Discord server.
        2. Use slash commands (/quran, /rquran, /tafseer, /convertdate) to interact with the bot.
        3. Set a channel using the `/setdailyquranchannel` command to receive the daily Quranic verse.
        4. Set a time using the `/setdailyqurantime` command to receive the Quranic verse at a specific time.
        5. Use the `/rmdailyquranchannel` command to stop a channel from receiving the daily Quranic verse.
    - name: Contributing
      value: |
        Contributions are welcome! If you have suggestions or want to contribute to the project, follow these steps:
        1. Fork the repository.
        2. Create a new branch (`git checkout -b feature/yourfeature`).
        3. Make your changes.
        4. Commit your changes (`git commit -am 'Add new feature'`).
        5. Push to the branch (`git push origin feature/yourfeature`).
        6. Create a new Pull Request.
    - name: License
      value: "This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details."
  color: 0x42f5a8
