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


def setup(bot):
    bot.add_cog(Poll(bot))
