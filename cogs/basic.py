import random
import discord
import requests
import json
#from bot import get_configs
from cogs.utils import checks
from discord.ext import commands
from discord.abc import Messageable
from discord.utils import get

def get_configs(bot):
    guild_configs = {} 

    for guild in bot.guilds:

        with open(f'configs/{guild.id}_config.json') as f:
            data = json.load(f)
            guild_configs[guild.id] = data

    return guild_configs


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO : Added listener for un-react and remove the corresponding role

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, *reactions):
       
        for reaction in reactions:
            print(reaction)

        for guild in self.bot.guilds:
            guild_id = guild.id 

            configs = get_configs(self.bot)
            

            current_config = configs[guild_id]
          
            message_id = current_config['role_message_id']
            channel_id = current_config['role_message_channel_id']

            if message_id and channel_id:
                
                channel = await self.bot.fetch_channel(channel_id)
                message = await channel.fetch_message(message_id)

                # Reactor's User ID
                user_id = reaction.user_id
                #user = await guild.fetch_member(user_id)
                emoji = reaction.emoji

                user = reaction.member

                for role in current_config['roles']:
                    if emoji.name == role['emoji']:
                        # Assigns role to corresponding reacted emoji
                
                        roles = discord.utils.get(guild.roles, name=role['name'])
                        await user.add_roles(roles)
                        print(f"Assigned {role['name']} to {user_id}.")

               

    @commands.command(name="reactions")
    async def reactions(self, ctx):
        message_id = 762503476340064288
        message = await ctx.channel.fetch_message(message_id)
        for reaction in message.reactions:
            print(reaction)

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

    # ISSUE : Can only use 'ctx.fetch_message()' in channel that command was run
    # FIX   : Maybe supply channel id first? Maybe just run command in same channel?
    @commands.check(checks.is_bot_enabled)
    @commands.command(name="setmessageid")
    async def setmessageid(self, ctx, msg_id):
        guild_id = ctx.message.channel.guild.id
        configs = get_configs(ctx.bot)

        current_config = configs[guild_id]
        current_config['role_message_id'] = int(msg_id)
        
        message = await ctx.fetch_message(int(msg_id))
        
        current_config['role_message_channel_id'] = message.channel.id
        
        with open(f"configs/{guild_id}_config.json", "w") as config_file:
            config_file.write(json.dumps(current_config, indent=2))
        
        await ctx.send(f"Message ID has been updated to {msg_id}\nMessage Channel ID has been updated to {message.channel.id}")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="createrole")
    async def createrole(self, ctx, role_name):
        await ctx.message.channel.guild.create_role(name=role_name)
        await ctx.send(f"{role_name} has been successfully created.")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="linkemoji")
    async def linkemoji(self, ctx, role_name, emoji):
        roles = {}
        linked_role = None
        
        # Roles of the server
        guild_roles = ctx.channel.guild.roles

        # Iterating over every role
        for role in guild_roles:

            # Checking each role to see if role_name is a valid role
           
            if role.name == role_name and emoji:
                roles[role] = f"{emoji}"
                linked_role = role
            else:
                continue
        
        # Confirmation Message
        if linked_role:
            await ctx.send(f"Linked {linked_role.name} with {emoji}")
        else:
            await ctx.send("I found no role...")

        # Updating config with new emoji
        guild_id = ctx.message.channel.guild.id
        configs = get_configs(ctx.bot)

        current_config = configs[guild_id]
       
        roles = current_config['roles']

        for role in roles:
            if role['role_id'] == linked_role.id:
                role['emoji'] = emoji
                break
            else:
                continue
        
        
        
        with open(f"configs/{guild_id}_config.json", "w") as config_file:
            config_file.write(json.dumps(current_config, indent=2))
        
    @commands.command(name="emojirole")
    async def emojirole(self, ctx, role_name):
        guild_id = ctx.message.channel.guild.id
        configs = get_configs(ctx.bot)

        current_config = configs[guild_id]
        

        if role_name:
            for role in ctx.channel.guild.roles:
                if role.name == role_name:
                    searched_role = role

            for role in current_config['roles']:
                if role['role_id'] == searched_role.id:
                    await ctx.send(role['emoji'])




def setup(bot):
    bot.add_cog(Basic(bot))
