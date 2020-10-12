import os
import discord
from config import Config
from cogs.utils import checks
from pathlib import Path
from discord.ext import commands


token = os.environ["TOKEN"]
# guild=os.environ["DISCORD_GUILD"] 

intents = discord.Intents.default()
intents.members = True

initial_extensions = ["cogs.basic", "cogs.admin", "cogs.sound"]

def instantiate_configs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return Config(guild)

    else:
        configs = []
        for guild in guilds:
            configs.append(Config(guild))
        return configs


def prefix(bot, message):
    id = message.channel.guild.id
    configs = instantiate_configs(bot.guilds)

    for config in configs:
        if config.guild_id == id:
            return config.prefix


bot = commands.Bot(command_prefix=prefix, intents=intents)

# ISSUE : Roles created after config are not updated
# FIX   : Maybe a role creation event listener to update the config with the new role
@bot.event
async def on_ready():
    print(f"Logged in")

    configs = instantiate_configs(bot.guilds)

    for config in configs:
        print(config.guild_id)

@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f"Welcome {member.mention} to {guild.name}!"
        await guild.system_channel.send(to_send)

@bot.command(name="test")
async def test(ctx):
    await ctx.send("The test has passed!")

@commands.check(checks.is_bot_enabled)
@bot.command(name="setprefix")
async def set_prefix(ctx, prefix):
    guild_id = ctx.message.channel.guild.id
    current_config = instantiate_configs(ctx.bot.guilds, guild_id)
    current_config.prefix = str(prefix)
    current_config.update_config()
    await ctx.send(f"Prefix has been updated to {prefix}")


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
