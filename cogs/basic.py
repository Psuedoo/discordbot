import random
import discord
import requests
import json
from config import Config
from cogs.utils import checks
from discord.ext import commands


class Basic(commands.Cog):
    """*Basic commands for random things*"""
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

    @commands.command(name="randomnumber", aliases=["randnum", ], description="Generates a random number")
    async def randomnumber(self, ctx, max_number=1000):
        await ctx.send(random.randint(1, max_number))

    @commands.command(name="randomchoice", aliases=["rc", ], description="Picks from given choices, randomly")
    async def randomchoice(self, ctx, *choices):
        await ctx.send(f"I have chosen {random.choice(choices)}.")

    @commands.command(name="joke", description="Tells a joke")
    async def joke(self, ctx):
        url = "https://icanhazdadjoke.com/"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        await ctx.send(response.json()['joke'])


def setup(bot):
    bot.add_cog(Basic(bot))
