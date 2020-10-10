import random
import discord
import requests
import json 
from config import Config
from cogs.utils import checks
from discord.ext import commands
from discord.abc import Messageable
from discord.utils import get


def instantiate_configs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return Config(guild)

    else:
        configs = []
        for guild in guilds:
            configs.append(Config(guild))
        return configs



class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        
    # TODO : Added listener for un-react and remove the corresponding role

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        
        if reaction.member.bot:
            return
        else:

            guild = await self.bot.fetch_guild(reaction.guild_id)
            current_config = instantiate_configs(self.bot.guilds, guild.id)

            message_id = current_config.role_message_id 
            channel_id = current_config.role_message_channel_id

            if message_id == reaction.message_id and channel_id == reaction.channel_id:
                
                # Reactor's User ID
                user_id = reaction.user_id

                emoji = reaction.emoji

                user = reaction.member

                for role in current_config.roles.values():
                    if emoji.name == role.get('emoji'):
                        # Assigns role to corresponding reacted emoji
                
                        roles = discord.utils.get(guild.roles, name=role.get('name'))
                        await user.add_roles(roles)
                        print(f"Assigned {role.get('name')} to {user_id}.")


    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        current_config = instantiate_configs(self.bot.guilds, role.guild.id)
        current_config.roles[role.id] = {'name': role.name, 'emoji': None}
        current_config.update_config()


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        current_config = instantiate_configs(self.bot.guilds, role.guild.id)
        current_config.roles.pop(f"{role.id}")
        current_config.update_config()

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        current_config = instantiate_configs(self.bot.guilds, before.guild.id)
       
        config_role = current_config.roles.get(before.id)
        config_role['name'] = after.name
        
        current_config.update_config()


    @commands.command(name="randomnumber", aliases=["randnum",])
    async def randomnumber(self, ctx, max_number=1000):
        await ctx.send(random.randint(1, max_number))

    @commands.command(name="randomchoice", aliases=["rc",])
    async def randomchoice(self, ctx, *choices):
        await ctx.send(f"I have chosen {random.choice(choices)}.")

    @commands.command(name="joke")
    async def joke(self, ctx):
        url = "https://icanhazdadjoke.com/"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        await ctx.send(response.json()['joke'])

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="setchannel")
    async def setchannel(self, ctx):

        guild_id = ctx.message.channel.guild.id
        
        current_config = instantiate_configs(ctx.bot.guilds, guild_id)
        
        current_config.role_message_channel_id = int(ctx.message.channel.id)
            
        current_config.update_config()

        linked_roles = {}

        for role in current_config.roles.values():
            if role.get('emoji'):
                linked_roles['name'] = role.get('name')
                linked_roles['emoji'] = role.get('emoji')

        

        role_embed = discord.Embed(title="Reaction Roles")

        for role in linked_roles.items():
            role_embed.add_field(name=f"{role.get('name')}", value=f"{role.get('emoji')}")

        await ctx.send("React with the following emojis for the corresponding role:")
        message = await ctx.send(embed=role_embed)

        current_config.role_message_id = int(message.id)

        current_config.update_config()

    

    # TODO : After role creation, add to config file
    @commands.check(checks.is_bot_enabled)
    @commands.command(name="createrole")
    async def createrole(self, ctx, role_name):
        role = await ctx.message.channel.guild.create_role(name=role_name)
    
        await ctx.send(f"{role_name} has been successfully created.")



    @commands.check(checks.is_bot_enabled)
    @commands.command(name="linkemoji")
    async def linkemoji(self, ctx, role_name, emoji):
        roles = {}
        linked_role = None
        
        # Roles of the server
        guild_roles = ctx.channel.guild.roles
        
        current_config = instantiate_configs(self.bot.guilds, ctx.message.channel.guild.id)

        if any(emoji == role.get('emoji') for role in current_config.roles.values()):
            await ctx.send("That emoji is already in use.")
            return
        
        else:
            for role in current_config.roles.values():
                if role.get('name') == role_name and emoji:
                    role['emoji'] = emoji
                    await ctx.send(f"Linked {role.get('name')} with {emoji}")
                    
                    channel = await self.bot.fetch_channel(current_config.role_message_channel_id)
                    message = await channel.fetch_message(current_config.role_message_id)
                    
                    role_embed = message.embeds[0]
                    role_embed.add_field(name=f"{role.get('name')}", value=f"{role.get('emoji')}")
                    await message.edit(embed=role_embed)

                    await message.add_reaction(emoji)
                    
                    break

        
        current_config.update_config()

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="unlinkemoji")
    async def unlinkemoji(self, ctx, emoji):
        current_config = instantiate_configs(self.bot.guilds, ctx.message.channel.guild.id)
        unlinked_emoji = False

        for role in current_config.roles.values():
            if role.get('emoji') == emoji:
                role['emoji'] = None
                unlinked_emoji = True
                await ctx.send(f"Unlinked {emoji} from {role.get('name')}.")
                break

        if not unlinked_emoji:
            await ctx.send(f"Couldn't find a role linked with {emoji}.")

        current_config.update_config()

def setup(bot):
    bot.add_cog(Basic(bot))
