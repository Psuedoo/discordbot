from discord.ext import commands
from .utils.checks import *
from db.db_handler import DatabaseHandler
from db.models import Commands

class Mod(commands.Cog):
    """*Mod commands for mod things*"""
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.db_handler = DatabaseHandler()

    @commands.command(name="addcommand")
    @commands.check(is_mod)
    async def add_command(self, ctx, command_name, command_response):
        if command_name and command_response:
            await self.db_handler.insert(
                [
                    Commands(
                        guild_id=str(ctx.guild.id),
                        name=command_name,
                        response=command_response,
                    )
                ]
            )
            await ctx.send("Added command")
        else:
            await ctx.send('lol idk bro')

    @commands.command(name="getcommands")
    @commands.check(is_mod)
    async def get_commands(self, ctx):
        commands = await self.db_handler.get_commands(ctx.guild)
        await ctx.send(commands)

    @commands.command(name="getcommand")
    @commands.check(is_mod)
    async def get_command(self, ctx, command_name):
        response = await self.db_handler.get_command(ctx.guild, command_name)
        await ctx.send(response)

    @commands.command(name="removecommand")
    @commands.check(is_mod)
    async def remove_command(self, ctx, command_name):
        command = await self.db_handler.remove_command(ctx.guild, command_name)
        if command:
            await ctx.send(f'{command_name} has been removed.')
        else:
            await ctx.send(f'{command_name} was not found.')

    @commands.command(name="createreactionmessage")
    @commands.check(is_mod)
    async def create_reaction_message(self, ctx):
        reaction_message = await ctx.send('embed')

        await self.db_handler.set_reaction_message(ctx.guild, reaction_message)

        await ctx.author.send("Added reaction role message.")

        roles = await self.db_handler.get_reaction_roles(ctx.guild)

        for role in roles:
            await reaction_message.add_reaction(role['emoji'])

        # Maybe loop roles, add roles with assigned emojis


    # TODO: Add command for getting reaction role message info
    @commands.command(name="getreactionmessage")
    @commands.check(is_mod)
    async def get_reaction_message(self, ctx):
        reaction_message = await self.db_handler.get_reaction_message(ctx.guild)
        await ctx.send(reaction_message)

    @commands.command(name="getroles")
    @commands.check(is_mod)
    async def get_roles(self, ctx):
        roles = await self.db_handler.get_roles(ctx.guild)
        await ctx.send(roles)

    @commands.command(name="getreactionroles")
    @commands.check(is_mod)
    async def get_reaction_roles(self, ctx):
        roles = await self.db_handler.get_reaction_roles(ctx.guild)
        await ctx.send(roles)


    @commands.command(name="setroleemoji")
    @commands.check(is_mod)
    async def set_role_emoji(self, ctx, role, emoji):
        print(role[3:-1])
        await self.db_handler.set_role_emoji(ctx.guild, role[3:-1], emoji)

def setup(bot):
    bot.add_cog(Mod(bot))