from cogs.utils import checks
from discord.ext import commands
from config import Config


class Admin(commands.Cog):
    """*Admin commands for bot configuration*"""
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

    @commands.command(name="load", hidden=True, description="Loads a cog")
    @commands.check(checks.is_psuedo)
    async def c_load(self, ctx, *, cog: str):

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f"Loaded {cog}")

    @commands.command(name="unload", hidden=True, description="Unloads a cog")
    @commands.check(checks.is_psuedo)
    async def c_unload(self, ctx, *, cog: str):

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f"Unloaded {cog}")

    @commands.command(name="reload", hidden=True, description="Reloads a cog")
    @commands.check(checks.is_psuedo)
    async def c_reload(self, ctx, *, cog: str):

        try:
            self.bot.load_extension(cog)
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f"Reloaded {cog}")

    @commands.command(name="setstreamerid", description="Set the streamer id for main twitch streamer")
    @commands.check(checks.is_bot_enabled)
    async def set_streamer_id(self, ctx, streamer_id):
        config = Config(ctx.guild)
        config.streamer_id = streamer_id
        config.update_config()
        await ctx.send("Successfully set streamer id!")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="setprefix", description="Sets prefix for the bot")
    async def set_prefix(self, ctx, prefix):
        current_config = Config(ctx.guild)
        current_config.prefix = str(prefix)
        current_config.update_config()
        await ctx.send(f"Prefix has been updated to {prefix}")


def setup(bot):
    bot.add_cog(Admin(bot))
