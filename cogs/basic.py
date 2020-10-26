import random
import discord
import requests
import json
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
        configs = []
        for guild in guilds:
            configs.append(Config(guild))
        return configs


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.command(name="randomnumber", aliases=["randnum", ])
    async def randomnumber(self, ctx, max_number=1000):
        await ctx.send(random.randint(1, max_number))

    @commands.command(name="randomchoice", aliases=["rc", ])
    async def randomchoice(self, ctx, *choices):
        await ctx.send(f"I have chosen {random.choice(choices)}.")

    @commands.command(name="joke")
    async def joke(self, ctx):
        url = "https://icanhazdadjoke.com/"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        await ctx.send(response.json()['joke'])



def setup(bot):
    bot.add_cog(Basic(bot))
