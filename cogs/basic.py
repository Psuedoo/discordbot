import random
import discord
import requests
from discord.ext import commands
from discord.abc import Messageable

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    

def setup(bot):
    bot.add_cog(Basic(bot))
