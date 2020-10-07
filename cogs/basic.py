import random
import discord
import requests
import json
#from bot import get_configs
from cogs.utils import checks
from discord.ext import commands
from discord.abc import Messageable

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


    # Bot has to:
    # find channel.message to attach reactions to
    # tie certain reactions to certain roles
    # listen for users to click reaction
    # if user clicks reaction, assign corresponding role


    @commands.Cog.listener()
    async def on_raw_reaction_add(*reactions):
       
       for reaction in reactions:
            print(reaction)


       # message_id = 762503476340064288
       # channel = bot.Guild.id
       # message = await channel.fetch_message(message_id)
       # 
       # print(message)
       # users = await message.reaction.users()
       # print(users)
        

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
    async def linkemoji(self, ctx, role_name, emoji=None):
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
            elif role.name == role_name and not emoji:
                roles[role] = ":one:"
                linked_role = role
            else:
                continue

        if linked_role:
            await ctx.send(f"Linked {linked_role.name} with {emoji}")
        else:
            await ctx.send("I found no role...")

    # TODO : Stream content for 10/5 : 10/6 night: 
    # TODO : Create commands to edit the config
    # TODO :    -- ?setmsgid <message_id> COMPLETE?
    # TODO :    -- ?setchannel <#channel> COMPLETE?
    # TODO :    -- ?createroll <role_name>
    # TODO :    -- ?linkemoji <role_name> <emoji=None> (if emoji=None, pick random one from emoji list in config)

    # TODO : Then and only then, after all the above are finished, we can fix the listener for assigning roles
    #           based on reaction to a message. We could do it normally, but we want it to be dynamic across servers.



def setup(bot):
    bot.add_cog(Basic(bot))
