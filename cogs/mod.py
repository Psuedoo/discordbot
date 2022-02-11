from discord import Embed
from discord.ext import commands
from .utils.checks import *
from db.db_handler import DatabaseHandler
from db.models import Commands, Roles

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

    @commands.command(name="createreactionmessage", aliases=["crm"])
    @commands.check(is_mod)
    async def create_reaction_message(self, ctx):

        embed = Embed(title="Roles", description="React to this message for the corresponding roles!")
        roles = await self.db_handler.get_reaction_roles(ctx.guild)

        reaction_message = await ctx.send(embed=embed)

        await self.db_handler.set_reaction_message(ctx.guild, reaction_message)

        for role in roles:
            embed.add_field(name=f"{role['name']}", value=f"{role['emoji']}", inline=False)
            await reaction_message.add_reaction(role['emoji'])

        await reaction_message.edit(embed=embed)



    async def get_reaction_message(self, ctx):
        reaction_message_info = await self.db_handler.get_reaction_message(ctx.guild)

        reaction_message_channel = [
            channel for channel in ctx.guild.channels if str(channel.id) == reaction_message_info['channel_id']
        ]

        reaction_message_channel = reaction_message_channel[0]

        reaction_message = await reaction_message_channel.fetch_message(reaction_message_info['message_id'])

        return reaction_message
        
    async def add_reaction_role(self, ctx, role):
        reaction_message = await self.get_reaction_message(ctx)

        embed = reaction_message.embeds[0]
        embed.add_field(name=f"{role.name}", value=f"{role.emoji}")

        await reaction_message.add_reaction(role.emoji)
        await reaction_message.edit(embed=embed)

    async def remove_reaction_role(self, ctx, role):
        if role.emoji:
            reaction_message = await self.get_reaction_message(ctx)

            embed = reaction_message.embeds[0]
            
            for index, field in enumerate(embed.fields):
                if field.value == role.emoji:
                    embed.remove_field(index)
            
            await reaction_message.clear_reaction(role.emoji)

            await reaction_message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.db_handler.insert(
            [
                Roles(
                    id=str(role.id),
                    guild_id=str(role.guild.id),
                    name=role.name,
                    emoji=None
                )
            ]
        )
        print(f'You created and added {role} to the database')

    @commands.Cog.listener()
    async def on_guild_role_update(self, before_role, after_role):
        await self.db_handler.update_role(before_role.guild, before_role, after_role)
        print(f'You updated {before_role} -> {after_role}')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.db_handler.remove_role(role.guild, role.id)
        print(f'You removed {role}')


    @commands.command(name="getroles")
    @commands.check(is_mod)
    async def get_roles(self, ctx):
        embed = Embed(title="Server Roles")
        roles = await self.db_handler.get_roles(ctx.guild)

        for role in roles:
            embed.add_field(
                name=f'{role["name"]}',
                value=f'id={role["id"]}, emoji={role["emoji"]}'
            )

        await ctx.send(embed=embed)

    @commands.command(name="getreactionroles", aliases=["grr"])
    @commands.check(is_mod)
    async def get_reaction_roles(self, ctx):
        roles = await self.db_handler.get_reaction_roles(ctx.guild)
        await ctx.send(roles)


    @commands.command(name="setroleemoji", aliases=["sre"])
    @commands.check(is_mod)
    async def set_role_emoji(self, ctx, role, emoji):
        role_id = role[3:-1]
        await self.db_handler.set_role_emoji(ctx.guild, role_id, emoji)
        role = await self.db_handler.get_role(ctx.guild, role_id)
        await self.add_reaction_role(ctx, role)

    @commands.command(name="removeroleemoji", aliases=["rre"])
    @commands.check(is_mod)
    async def remove_role_emoji(self, ctx, role):
        role_id = role[3:-1]
        role = await self.db_handler.get_role(ctx.guild, role_id)
        await self.db_handler.remove_role_emoji(ctx.guild, role_id)
        await self.remove_reaction_role(ctx, role)

def setup(bot):
    bot.add_cog(Mod(bot))