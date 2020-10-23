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
    def __init__(self, name, message=None):
        self.path = Path('.') / 'polls' / f'{name}_poll.json'
        if self.path.is_file():
            poll_data = self.get_poll_data()
        else:
            poll_data = {}
        
        self.name = poll_data.get('name', name)
        self.author_id = poll_data.get('author_id', message.author.id)
        self.author_name = poll_data.get('author_name', message.author.display_name)
        self.message_id = poll_data.get('message_id', message.id)
        self.message_channel_id = poll_data.get('message_channel_id', message.channel.id)
        self.duration = poll_data.get('duration', 180)
        self.options = poll_data.get('options', {})

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
                "options": self.options
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


    async def update(self, poll):
        poll.update_poll()
        await self.update_poll_message(poll)


    async def update_poll_message(self, poll):
        if self.poll_message:
            try:
                embed = self.poll_message.embeds[0]
            except IndexError:
                embed = discord.Embed()

            embed.clear_fields()
            for option in poll.options:
                embed.add_field(name=poll.options[option].get('name'), value=option)
            await self.poll_message.edit(embed=embed)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if self.poll.message_id == reaction.message.id and not user.bot:
            for option in self.poll.options:
                if reaction.emoji == option:
                    self.poll.options[option].get('voters').append(user.display_name)
                    await self.update(self.poll)

        else:
            pass  # Reaction wasn't on the poll


    @commands.command(name="pollcreate")
    async def create_poll(self, ctx, poll_name):
        self.poll_message = await ctx.send(f"Poll: {poll_name}")

        self.poll = Poll(poll_name, self.poll_message)

    @commands.command(name="polladd")
    async def add_poll_option(self, ctx, poll_name, option_name, emoji):
        if self.poll:
            self.poll.options[emoji] = {'name': option_name, 'voters': []}
            await self.poll_message.add_reaction(emoji)
            await self.update(self.poll)
        else:
            await self.create_poll(poll_name)

    @commands.command(name="pollremove")
    async def remove_poll_option(self, ctx, poll_name, emoji):
        if self.poll:
            try:
                self.poll.options.pop(emoji)
                await self.update(self.poll)
            except:
                print("Error removing poll option")
        else:
            print("No current poll")

    @commands.command(name="pollend")
    async def end_poll(self, ctx, poll_name=None):
        if self.poll and os.path.exists(self.poll.path):
            voters = [{option: len(self.poll.options[option].get('voters'))} for option in self.poll.options]
            await ctx.send(voters)
            os.remove(self.poll.path)
            self.poll = None
            print("Poll file removed.")
        else:
            print("Something went wrong.")



def setup(bot):
    bot.add_cog(PollCog(bot))
