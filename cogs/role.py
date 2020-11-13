import discord
import db.db_handler_role
from db.models import *
from config import Config
from cogs.utils import checks
from discord.ext import commands


class ReactionRole(commands.Cog):
    """*Commands for a react to assign role message*"""

    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
        self.hidden = False

    # TODO : Added listener for un-react and remove the corresponding role
    async def role_embed_remove(self, guild, del_role=None, emoji=None):
        for role in await db.db_handler_role.get_emoji_roles(guild):
            if role.get('emoji'):
                if emoji and role.get('emoji') == emoji or del_role and role.get('name') == del_role.name:
                    emoji = role.get('emoji')
                    channel_id, message_id = await db.db_handler_role.get_channel(guild)
                    if channel_id and message_id:
                        channel = await self.bot.fetch_channel(channel_id)
                        message = await channel.fetch_message(message_id)

                    role_embed = message.embeds[0]
                    for index, field in enumerate(role_embed.fields):
                        if field.name == role.get('name'):
                            role_embed.remove_field(index)
                    await message.edit(embed=role_embed)

                    await message.remove_reaction(emoji, self.bot.user)
                    return {'name': role.get('name'), 'emoji': emoji}

                    break
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.member.bot:
            return
        else:
            guild = await self.bot.fetch_guild(reaction.guild_id)
            channel_id, message_id = await db.db_handler_role.get_channel(guild)

            if message_id == reaction.message_id and channel_id == reaction.channel_id:

                for role in await db.db_handler_role.get_emoji_roles(guild):
                    if reaction.emoji.name == role.get('emoji'):
                        # Assigns role to corresponding reacted emoji

                        roles = discord.utils.get(guild.roles, name=role.get('name'))
                        await reaction.member.add_roles(roles)
                        print(f"Assigned {role.get('name')} to {reaction.user_id}.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):

        guild = await self.bot.fetch_guild(reaction.guild_id)

        channel_id, message_id = await db.db_handler_role.get_channel(guild)

        if message_id == reaction.message_id and channel_id == reaction.channel_id:

            user = await guild.fetch_member(reaction.user_id)

            for role in await db.db_handler_role.get_emoji_roles(guild):
                if reaction.emoji.name == role.get('emoji'):
                    # Removes role to corresponding reacted emoji

                    roles = discord.utils.get(guild.roles, name=role.get('name'))
                    await user.remove_roles(roles, reason="Unreacted from react message")
                    print(f"Removed {role.get('name')} from {reaction.user_id}.")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        data = [Roles(id=role.id,
                      guild_id=role.guild.id,
                      name=role.name,
                      emoji=None)]

        await db.db_handler.insert(data)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await db.db_handler_role.delete_role(role)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        await db.db_handler_role.update_role_name(before, after.name)

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="setchannel", description="Sets a channel for the role react message")
    async def setchannel(self, ctx):
        role_embed = discord.Embed(title="Reaction Roles")

        for role in await db.db_handler_role.get_emoji_roles(ctx.guild):
            role_embed.add_field(name=f"{role.get('name')}", value=f"{role.get('emoji')}")

        await ctx.send("React with the following emojis for the corresponding role:")
        message = await ctx.send(embed=role_embed)
        for role in await db.db_handler_role.get_emoji_roles(ctx.guild):
            await message.add_reaction(role.get('emoji'))
        await db.db_handler_role.set_channel(ctx.guild, ctx.channel, message)
        await ctx.message.delete()

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="createrole", description="Creates a role")
    async def createrole(self, ctx, role_name):
        await ctx.message.channel.guild.create_role(name=role_name)

        await ctx.message.delete()
        message = await ctx.send(f"{role_name} has been successfully created.")
        await message.delete(delay=10)

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="linkemoji", description="Links an emoji to a role for the reaction role message")
    async def linkemoji(self, ctx, role_to_link, emoji):

        mentioned_roles = ctx.message.role_mentions

        # Making sure there is a role linked to the command message
        if len(mentioned_roles) > 1:
            await ctx.send("Please only mention one role")
            return
        else:
            mentioned_role = mentioned_roles[0]

        roles = await db.db_handler_role.get_emoji_roles(ctx.guild)

        # Verifying the emoji isn't already in use
        if any(emoji == role.get('emoji') for role in roles):
            await ctx.send("That emoji is already in use.")
            return

        # If emoji isn't in use, link it
        else:
            # Linking emoji in db
            await db.db_handler_role.link_emoji(ctx.guild, mentioned_role, emoji)

            channel_id, message_id = await db.db_handler_role.get_channel(ctx.guild)

            if message_id and channel_id:
                print('found message_id and channel_id')
                channel = await self.bot.fetch_channel(channel_id)
                message = await channel.fetch_message(message_id)

                role = await db.db_handler_role.get_role(mentioned_role)

                role_embed = message.embeds[0]
                role_embed.add_field(name=f"{role.name}", value=f"{role.emoji}")
                await message.edit(embed=role_embed)

                await message.add_reaction(emoji)
                await ctx.message.delete()

    # TODO: Some of this seems redundant with embed remove, look into that
    @commands.check(checks.is_bot_enabled)
    @commands.command(name="unlinkemoji", description="Unlinks an emoji from a role for the role reaction message")
    async def unlinkemoji(self, ctx, emoji, role=None):

        unlinked_role = await self.role_embed_remove(ctx.guild, emoji=emoji)

        channel_id, message_id = await db.db_handler_role.get_channel(ctx.guild)

        if channel_id and message_id:
            channel = await self.bot.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)

            await message.clear_reaction(emoji)
            await ctx.message.delete()

            unlinked_role = None
            for role in await db.db_handler_role.get_emoji_roles(ctx.guild):
                if role.get('emoji') == emoji:
                    unlinked_role = role

            response = await ctx.send(f"Unlinked {unlinked_role.get('emoji')} from {unlinked_role.get('name')}.")
            await response.delete(delay=10)

        if not unlinked_role:
            await ctx.send(f"Couldn't find a role linked with {emoji}.")

        await db.db_handler_role.unlink_emoji(ctx.guild, emoji)


def setup(bot):
    bot.add_cog(ReactionRole(bot))
