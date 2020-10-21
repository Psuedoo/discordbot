import os
import discord
import asyncio
import json
from tinydb import TinyDB, Query 
from config import Config
from command_class import CustomCommand
from cogs.utils import checks
from discord.ext import commands
from discord.abc import Messageable
from discord.utils import get

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
        self.poll_file = open("poll_file.json", 'w')

    def update(self):
        self.poll_file.write(json.dumps(self.poll_data), indent=2)
    
    @commands.Cog.listener(name="on_reaction_add")
    async def on_vote(self, reaction, user):
        # Check if reactions on poll message
        # Check if reaction is a valid option
        # Add user to list of voters
        pass

    @commands.command(name="pollcreate")
    async def create_poll(self, ctx, poll_name, duration=60):
        message = await ctx.send(f"Poll: {poll_name}")

        self.poll_data = {'poll_name': poll_name,
                'author': ctx.author,
                'duration': duration,
                'poll_message_id': message.id, 
                'options': {},
                }

        self.update()

    @commands.command(name="polladd")
    async def add_poll_option(self, ctx, option, emoji):
        options = self.poll_data.get('options')
        options[option] = {'emoji': emoji, 'voters': []}
        self.update()


    @commands.command(name="pollend")
    async def end_poll(self, ctx, poll_name=None):
        # Ends specified poll, if a jerk and doesn't say which poll, try to figure it out
        pass

def setup(bot):
    bot.add_cog(Poll(bot))
