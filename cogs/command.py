import os
import discord
import asyncio
from tinydb import TinyDB, Query 
from config import Config
from command_class import CustomCommand
from cogs.utils import checks
from discord.ext import commands


def instantiate_configs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return Config(guild)

    else:
        return [Config(guild) for guild in guilds]

def instantiate_dbs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return TinyDB(Config(guild).sounds)

    else:
        return [TinyDB(Config(guild).sounds) for guild in guilds]

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds

    @commands.command(name="addcommand")
    @commands.check(checks.is_bot_enabled)
    async def add_custom_command(self, ctx, command_name, command_response):
        cc = CustomCommand(ctx.guild)
        cc.add_custom_command(command_name, command_response)
        await ctx.send(f"Successfully added {command_name}!")

    @commands.command(name="deletecommand")
    @commands.check(checks.is_bot_enabled)
    async def delete_custom_command(self, ctx, command_name):
        cc = CustomCommand(ctx.guild)
        cc.delete_custom_command(command_name)
        await ctx.send(f"Successfully deleted {command_name}!")

    @commands.command(name="viewcommands")
    async def view_custom_commands(self, ctx):
        cc = CustomCommand(ctx.guild)
        await ctx.send(cc.view_custom_commands())
        

def setup(bot):
    bot.add_cog(CommandCog(bot))
