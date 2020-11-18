from cogs.utils import checks
from discord.ext import commands
from db.db_handler import insert
from db.db_handler_command import *
from db.models import Commands


class CustomCommand(commands.Cog):
    """*Commands regarding custom commands*"""
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
        self.hidden = False

    @commands.command(name="addcommand", description="Adds a custom command")
    @commands.check(checks.is_bot_enabled)
    async def add_custom_command(self, ctx, command_name, command_response):
        data = [Commands(guild_id=ctx.guild.id,
                         name=command_name,
                         response=command_response)]
        await insert(data)
        await ctx.send(f"Successfully added {command_name}!")

    @commands.command(name="deletecommand", description="Deletes a custom command")
    @commands.check(checks.is_bot_enabled)
    async def delete_custom_command(self, ctx, command_name):
        await delete_command(ctx.guild, command_name)
        await ctx.send(f"Successfully deleted {command_name}!")

    # TODO: Make it display the commands in a fancy way with embeds
    @commands.command(name="viewcommands", description="Displays the custom commands")
    async def view_custom_commands(self, ctx):
        commands = await get_command_names(ctx.guild)
        await ctx.send(commands)


def setup(bot):
    bot.add_cog(CustomCommand(bot))
