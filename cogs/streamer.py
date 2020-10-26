import os
import discord
import asyncio
import requests
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
        self.TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]

    # TODO: Add live notifications for streamers in config
    @commands.command(name="whoslive", description="Shows what streamers are currently live from the streamer library")
    async def whos_live(self, ctx, streamer):
        # reponse = requests.get()
        pass

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="addstreamer", description="Adds a streamer to the streamer library")
    async def add_streamer(self, ctx, streamer_url):
        config = Config(ctx.guild)
        # https://www.twitch.tv/psuedoo
        streamer_name = streamer_url[streamer_url.rfind("/") + 1:]

        config.streamers[streamer_name.strip()] = {'url': streamer_url, 'live': False}
        config.update_config()

        await ctx.send(f"{streamer_name} has been added!")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="removestreamer", description="Removes a streamer from the streamer library")
    async def remove_streamer(self, ctx, streamer_name):
        config = Config(ctx.guild)
        if config.streamers[streamer_name.lower()]:
            config.streamers.pop(streamer_name.lower())
            config.update_config()
            await ctx.send(f"{streamer_name.lower()} has been removed!")
        else:
            await ctx.send(f"No streamer with username {streamer_name} found.")

    @commands.command(name="viewstreamers", description="Displays the streamers in the streamer library")
    async def view_streamers(self, ctx):
        config = Config(ctx.guild)
        await ctx.send([streamer for streamer in config.streamers.keys()])

    @commands.command(name="viewstreamer", description="Displays a certain streamer from the streamer library")
    async def view_streamer(self, ctx, streamer_name):
        config = Config(ctx.guild)

        streamers = {"name": {"url"}, "name2": {"url"}, }
        if config.streamers[streamer_name.lower()]:
            streamer_url = config.streamers[streamer_name.lower()].get('url')

            await ctx.send(f"{streamer_name}: <{streamer_url}>")
        else:
            await ctx.send("Streamer doesn't exist.")


def setup(bot):
    bot.add_cog(Streamer(bot))
