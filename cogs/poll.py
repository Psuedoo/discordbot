import random
import requests
from discord.ext import commands


class Poll(commands.Cog):
    """*Commands for working the polls*"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pollcreate")
    async def poll_create(self, ctx):
        pass

    @commands.command(name="pollend")
    async def poll_end(self, ctx):
        pass

    @commands.command(name="addchoice")
    async def poll_add_choice(self, ctx):
        pass

    @commands.command(name="removechoice")
    async def poll_remove_choice(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Poll(bot))
