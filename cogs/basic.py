import random
import discord
from discord.ext import commands

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="randomnumber", aliases=["randnum",])
    async def randomnumber(self, ctx, max_number=1000):
        await ctx.send(random.randint(1, max_number))

def setup(bot):
    bot.add_cog(Basic(bot))
