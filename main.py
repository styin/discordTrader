import os
import requests

from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

# Cog Extensions
extensions = [
    'cogs.master_cog',
    'cogs.tk_cog',
    'cogs.trade_cog',
    'cogs.member_cog'
]

# API requests rate limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"[WARNING] Rate limit: {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("[LOG] No rate limit")

# Bot Client Object
class botClient:
    # Bot Constructor
    def __init__(self, token=None):
        self.token = token or os.getenv('botSecret')
        self.bot = commands.Bot(command_prefix=os.getenv('PREFIX'), case_insensitive=True)
        # self.author_id = int(os.getenv('styID'))
        self.on_ready = self.bot.event(self.on_ready)
        for extension in extensions:
            self.bot.load_extension(extension)  # Loads every extension.
  
    # Bot Boot Up
    def run(self):
        self.bot.run(self.token)

    # Event: On Ready
    async def on_ready(self):  # When the bot is ready
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Success! Logged in as [{0}]".format(self.bot.user))
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("")
        print("██████╗  ██████╗      ████████╗")
        print("██╔══██╗██╔════╝      ╚══██╔══╝")
        print("██║  ██║██║     █████╗   ██║   ")
        print("██║  ██║██║     ╚════╝   ██║   ")
        print("██████╔╝╚██████╗         ██║   ")
        print("╚═════╝  ╚═════╝         ╚═╝   ")
        print("")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Current Build: {0}".format(os.getenv('VERSION')))
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Booting
def main():
    bot = botClient()
    bot.run()

# Ensures this is the file being ran
if __name__ == '__main__':  
    main()
