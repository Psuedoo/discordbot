import os
import discord
import asyncio
from tinydb import TinyDB, Query 
from config import Config
from cogs.utils import checks
from discord.ext import commands
from discord.abc import Messageable
from discord.utils import get


def instantiate_configs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return Config(guild)

    else:
        return [Config(guild) for guild in guilds]

class Streamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
   
    @commands.Cog.listener()
    async def streamer_goes_live(self):
        pass

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="addstreamer")
    async def add_streamer(self, ctx, streamer_url):
        config = Config(ctx.guild)
        # https://www.twitch.tv/psuedoo
        streamer_name = streamer_url[streamer_url.rfind("/") + 1:] 

        config.streamers[streamer_name.strip()] = {'url': streamer_url}
        config.update_config()

        await ctx.send(f"{streamer_name} has been added!")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="removestreamer")
    async def remove_streamer(self, ctx, streamer_name):
        pass

    @commands.command(name="viewstreamers")
    async def view_streamers(self, ctx):
        config = Config(ctx.guild)
        await ctx.send([streamer for streamer in config.streamers.keys()])

def setup(bot):
    bot.add_cog(Streamer(bot))
