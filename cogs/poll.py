import os
import discord
import asyncio
import json
from pathlib import Path
from config import Config
from command_class import CustomCommand
from cogs.utils import checks
from discord.ext import commands
from discord.abc import Messageable
from discord.utils import get


class Poll:
    def __init__(self, name, author=None, message=None):
        self.path = Path('.') / 'polls' / f'{name}_poll.json'
        if self.path.is_file():
            poll_data = self.get_poll_data()
        else:
            poll_data = {}

        self.name = poll_data.get('name', name)
        self.author_id = poll_data.get('author_id', author.id)
        self.author_name = poll_data.get('author_name', author.display_name)
        self.message_id = poll_data.get('message_id', message.id)
        self.message_channel_id = poll_data.get('message_channel_id', message.channel.id)
        self.duration = poll_data.get('duration', 180)
        self.options = poll_data.get('options', {}) # Dict with option names: {emoji, voter list}

        if len(poll_data) == 0:
            self.update_poll()

    def to_json(self):
        poll_data = {
                "name": self.name,
                "author_id": self.author_id,
                "author_name": self.author_name,
                "message_id": self.message_id,
                "message_channel_id": self.message_channel_id,
                "duration": self.duration,
                "options": self.options # Dict with option names: {emoji, voter list}
        }
        return json.dumps(poll_data, indent=2)


    def update_poll(self):
        with open(self.path.absolute(), "w") as poll_file:
            poll_file.write(self.to_json())

    def get_poll_data(self):
        try:
            with open(self.path.absolute()) as poll_file:
                return json.load(poll_file)
        except FileNotFoundError:
            self.update_poll()
               

class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
        self.poll_dir = f"{os.path.expanduser('~/coding/discordbot/polls')}"


    def add_poll(self):
        with open(self.poll_file, "a") as poll_file:
            json.dump(self.poll_data, poll_file, indent=2)

    def update(self):
        with open(self.poll_file, "w") as poll_file:
            json.dump(self.poll_data, poll_file, indent=2)
        self.poll_push()

    def poll_push(self):
        with open(self.poll_file) as poll_file:
            poll_data = json.load(poll_file)
        print(poll_data)
    
    @commands.Cog.listener(name="on_reaction_add")
    async def on_vote(self, reaction, user):
        # Check if reactions on poll message
        # Check if reaction is a valid option
        # Add user to list of voters
        pass

    @commands.command(name="pollcreate")
    async def create_poll(self, ctx, poll_name):
        message = await ctx.send(f"Poll: {poll_name}")

        poll = Poll(poll_name, ctx.message.author, message)

    @commands.command(name="polladd")
    async def add_poll_option(self, ctx, option, emoji):
        pass        

    @commands.command(name="pollend")
    async def end_poll(self, ctx, poll_name=None):
        # Ends specified poll, if a jerk and doesn't say which poll, try to figure it out
        pass

def setup(bot):
    bot.add_cog(PollCog(bot))
