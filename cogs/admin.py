from cogs.utils import checks
from discord.ext import commands
from db import db_handler, db_handler_admin


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
        await db_handler_admin.set_streamer_id(ctx.guild, streamer_id)
        await ctx.send("Successfully set streamer id!")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="setprefix", description="Sets prefix for the bot")
    async def set_prefix(self, ctx, prefix):
        await db_handler.set_prefix(ctx.guild, prefix)
        await ctx.send(f"Prefix has been updated to {prefix}")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="settwitch", description="Sets the Twitch channel for the discord")
    async def set_twitch(self, ctx, channel_name):
        try:
            await db_handler_admin.set_twitch(ctx.guild, channel_name)
            await db_handler_admin.fix_sounds(ctx.guild)
            await ctx.send('Successfully set the Twitch channel!')
        except:
            await ctx.send('Couldnt set the Twitch')


def setup(bot):
    bot.add_cog(Admin(bot))
