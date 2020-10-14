import os
import re
import discord
from tinydb import TinyDB, Query 
from config import Config
from sound_class import SoundFile
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



class Sound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.db = TinyDB(os.path.expanduser('~/coding/sounds/sounds.json'))

    @commands.Cog.listener(name="on_message")
    async def sound_command_listener(self, message):

        Command = Query()

        if message.content.startswith('!'):
            command = message.content[1:]
        elif not message.content.startswith('!'):
            return

        if self.db.search(Command.command_name == command):
            audio_src = self.db.search(Command['command_name'] == command)
            audio_src = audio_src[0]['file']
            await self.voice_client.play(discord.FFmpegOpusAudio(os.path.expanduser(audio_src)))
            await message.channel.send(f"You've called a command.")


    @commands.command(name="join")
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        self.voice_client = await channel.connect()

    @commands.command(name="leave")
    async def leave(self, ctx):
        channel = ctx.author.voice.channel
        await self.voice_client.disconnect()

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="soundadd")
    async def soundadd(self, ctx, name, url):
        sound = SoundFile(name, url, title=name)
        sound.download_sound()
        await ctx.send(f"Added {name} to sounds!")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="viewsounds")
    async def viewsounds(self, ctx):
        sounds = []
        for sound in self.db:
            sounds.append(sound)
        await ctx.send(sounds)

def setup(bot):
    bot.add_cog(Sound(bot))
