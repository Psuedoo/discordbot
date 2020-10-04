from cogs.utils import checks
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="load", hidden=True)
    @commands.check(checks.is_psuedo)
    async def c_load(self, ctx, *, cog: str):

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f"Loaded {cog}")


    @commands.command(name="unload", hidden=True)
    @commands.check(checks.is_psuedo)
    async def c_unload(self, ctx, *, cog: str):

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f"Unloaded {cog}")


    @commands.command(name="reload", hidden=True)
    @commands.check(checks.is_psuedo)
    async def c_reload(self, ctx, *, cog: str):

        try:
            self.bot.load_extension(cog)
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f"Reloaded {cog}")


def setup(bot):
    bot.add_cog(Admin(bot))
