import os
import discord
from discord.ext import commands


TOKEN = os.environ['TOKEN']
GUILD = os.environ['DISCORD_GUILD']

token=os.environ["TOKEN"]
guild=os.environ["DISCORD_GUILD"] 

client = discord.Client()

def get_prefix(bot, message):
    prefixes = ['?']

    if not message.guild:
        return '?'

    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = ["cogs.basic","cogs.admin"]

bot = commands.Bot(command_prefix=get_prefix)




@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")

    game = discord.Game("Coding Myself", type=1, url="https://twitch.tv/psuedoo")
    await bot.change_presence(activity=game)
    



if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


bot.run(token)
