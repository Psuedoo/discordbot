import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

# Use for local building with .env file rather than Docker env vars
if os.path.exists("./.env"):
    load_dotenv()


token = os.getenv("TOKEN", None)
prefix = os.getenv("PREFIX", "?")

intents = discord.Intents.default()
intents.members = True

initial_extensions = [
    "cogs.basic"
]

global bot
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.owner_id = os.getenv("OWNER_ID", None)


@bot.event
async def on_ready():
    print("Logged in")

    # TODO : Once converted bot into class, make presence setting command
    game = discord.Game("operating on myself")
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command(name="test", hidden=True)
async def test(ctx):
    await ctx.send(f"The test has passed!")

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
