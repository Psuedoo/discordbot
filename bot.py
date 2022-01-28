import os
import discord
import asyncio
from db.db_handler import DatabaseHandler
from dotenv import load_dotenv
from discord.ext import commands

# Use for local building with .env file rather than Docker env vars
if os.path.exists("./.env"):
    load_dotenv()


token = os.getenv("TOKEN", None)
# prefix = os.getenv("PREFIX", "?")

intents = discord.Intents.default()
intents.members = True

initial_extensions = [
    "cogs.basic",
    "cogs.mod"
]

db_handler = DatabaseHandler()

global bot
bot = commands.Bot(command_prefix="?", intents=intents)
bot.owner_id = os.getenv("OWNER_ID", None)



@bot.event
async def on_ready():
    print("Logged in")

    await db_handler.initialize_guilds(bot.guilds)

    # TODO: When adding role through guild gui, add role to db

    # for guild in bot.guilds:

    # TODO: Change prefix based on Guild Config from db
        # prefix = await db_handler.get_prefix(guild)
        # bot.command_prefix = prefix
    # TODO : Once converted bot into class, make presence setting command
    game = discord.Game("operating on myself")
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.event
async def on_message(message):
    print(message.content)
    # Check if message starts with guild's prefix
    if message.content.startswith('?'):
        command = message.content[1:].split()
        try:
            response = await db_handler.get_command(message.guild, command[0])
            await message.channel.send(response)
        except AttributeError as error:
            await bot.process_commands(message)

        # if response:
        # else:
        # response = await db_handler.get_command(message.guild, )


# @bot.event
# async def on_message():

@bot.command(name="test", hidden=True)
async def test(ctx):
    await ctx.send(f"The test has passed!")

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
