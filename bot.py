import os
import discord
from discord.ext import commands


TOKEN = os.environ['TOKEN']
GUILD = os.environ['DISCORD_GUILD']

token=os.environ["TOKEN"]
guild=os.environ["DISCORD_GUILD"] 

# client = discord.Client()


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

initial_extensions = ["cogs.basic","cogs.admin"]

@bot.event
async def on_ready():
    print(f"Logged in")
#    game = discord.Game("Coding Myself", type=1, url="https://twitch.tv/psuedoo")
#    await bot.change_presence(activity=game)

@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f"Welcome {member.mention} to {guild.name}!"
        await guild.system_channel.send(to_send)

@bot.command(name="test")
async def test(ctx):
    await ctx.send("The test has passed!")


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
