import os
import re
import discord
import asyncio
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
        return [Config(guild) for guild in guilds]

def instantiate_dbs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return TinyDB(Config(guild).sounds)

    else:
        return [TinyDB(Config(guild).sounds) for guild in guilds]

class Sound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
        self.voice_client = None
        self.queue = asyncio.Queue()
        self.lock = asyncio.Lock()

    async def _handle_play(self, item):
        future = asyncio.Future()
        loop = asyncio.get_event_loop()

        def after(*args):
            loop.call_soon_threadsafe(future.set_result, args)

        self.voice_client.play(discord.FFmpegOpusAudio(os.path.expanduser(item)),
                    after=after)
        callback_args = await future
        return callback_args

    async def handle_queue(self):
        while not self.queue.empty():
            if not self.voice_client.is_playing():
                item = await self.queue.get()
                await self._handle_play(item)
                self.queue.task_done()

    async def sound_handler(self, sound, discord_id=None):
        sound = self.get_sound_file(sound, discord_id)
        if sound:
            await self.queue.put(sound)
            async with self.lock:
                task = asyncio.create_task(self.handle_queue())
                await self.queue.join()
                await asyncio.gather(task)

    def get_sound_file(self, sound, discord_id=None):
        Command = Query()
        guild = self.bot.get_guild(int(discord_id))
        config = Config(guild)
        db = TinyDB(config.sounds)

        return db.search(Command.command_name == sound)[0]['file']
        
       # for db in dbs:
       #     if sound_file:
       #         return sound_file

    @commands.command(name="join")
    async def join(self, ctx=None, twitch_channel=None, discord_id=None):

        # If Twitch_channel_name == guild.fetch_member(config.streamer_id) and streamer is in VC: Join that vc
        guild = self.bot.get_guild(int(discord_id))
        config = Config(guild)
        if not self.voice_client:
            if ctx:
                channel = ctx.author.voice.channel
                self.voice_client = await channel.connect()
            else:
                streamer = await guild.fetch_member(int(config.streamer_id))
                channel = streamer.voice.channel
                if channel:
                    self.voice_client = await channel.connect()
                else:
                    print("No channel to connect to")
        else:
            pass

    @commands.command(name="leave")
    async def leave(self, ctx=None):
        await self.voice_client.disconnect()
        self.voice_client = None

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="soundadd")
    async def soundadd(self, ctx, name, url):
        sound = SoundFile(guild, name, url, title=name)
        sound.download_sound()
        await ctx.send(f"Added {name} to sounds!")

    @commands.command(name="play")
    async def play(self, ctx, sound):
        await self.sound_handler(sound, ctx.guild.id)

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="sounddelete")
    async def sound_delete(self, ctx, name):
        Command = Query()
        db = instantiate_dbs(self.guilds, ctx.guild)
        table = db.table('_default')
        
        try:
            sound_dir = [sound.get('file') for sound in db if sound.get('command_name') == name][0]
        except IndexError as e:
            await ctx.send("Sound doesn't exist")
            return

        try:
            table.remove(Command.command_name == name)
            os.remove(os.path.expanduser(sound_dir))
        except:
            await ctx.send(f"Failed to delete {name} sound.")
        else:
            await ctx.send(f"Successfully deleted {name} sound!")
        
    @commands.check(checks.is_bot_enabled)
    @commands.command(name="viewsounds")
    async def viewsounds(self, ctx):
        db = instantiate_dbs(self.guilds, ctx.guild)
        sounds = [sound.get('command_name') for sound in db]
        for sound in db:
            sounds.append(sound.get('command_name'))
        await ctx.send(sounds)



def setup(bot):
    bot.add_cog(Sound(bot))
