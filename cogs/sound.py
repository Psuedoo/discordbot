import os
import discord
import asyncio
import youtube_dl
from pathlib import Path
from tinydb import TinyDB, Query
from config import Config
from cogs.utils import checks
from discord.ext import commands


def instantiate_configs(guilds):
    return [Config(guild) for guild in guilds if guild]


def instantiate_dbs(guilds):
    return [TinyDB(Config(guild).sounds) for guild in guilds if guild]


class SoundFile:
    def __init__(self, guild, command_name=None, url=None, title=None):
        self.command_name = command_name
        self.url = url
        self.guild = guild
        self.guild_id = guild.id
        self.config = Config(guild)
        self.path = Path.cwd() / 'sounds'
        if not self.path.is_dir():
            self.path.mkdir()

        if title:
            self.title = title
        else:
            self.title = '%(title)s'

        self.file_path = self.path / self.title
        self.db_path = self.path / f'sounds_{self.guild_id}.json'

        self.ydl_opts = {'format': 'bestaudio',
                         'noplaylist': True,
                         'outtmpl': f'{self.file_path}.%(ext)s',
                         'postprocessors': [{'key': 'FFmpegExtractAudio'}]}

        self.db = TinyDB(self.db_path)
        self.config.sounds = self.db_path
        self.config.update_config()

    def download_sound(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

        for file in self.path.iterdir():
            if file.stem == self.file_path.stem:
                self.file_path = file

    def add_command(self):
        if not self.file_path.is_file():
            self.download_sound()

        if self.command_name in [sound.get('command_name') for sound in self.db]:
            return
        else:

            config = Config(self.guild)
            command_info = {'file': str(self.file_path),
                            'command_name': str(self.command_name)}

            self.db.insert(command_info)
            config.update_config()


class Sound(commands.Cog):
    """*Commands for sound functionality*"""
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
        else:
            print("No sound")

    def get_sound_file(self, sound, discord_id=None):
        Command = Query()
        guild = self.bot.get_guild(int(discord_id))
        config = Config(guild)
        db = TinyDB(config.sounds)

        return db.search(Command.command_name == sound)[0]['file']

    @commands.command(name="join", description="Joins the voice chat of command author")
    async def join(self, ctx=None, twitch_channel=None, discord_id=None):

        # If Twitch_channel_name == guild.fetch_member(config.streamer_id) and streamer is in VC: Join that vc
        if not self.voice_client:
            if ctx:
                channel = ctx.author.voice.channel
                self.voice_client = await channel.connect()
            else:
                guild = self.bot.get_guild(int(discord_id))
                config = Config(guild)
                streamer = await guild.fetch_member(int(config.streamer_id))
                channel = streamer.voice.channel
                if channel:
                    self.voice_client = await channel.connect()
                else:
                    print("No channel to connect to")

    @commands.command(name="leave", description="Disconnects the bot from the voice channel")
    async def leave(self, ctx=None):
        await self.voice_client.disconnect()
        self.voice_client = None

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="soundadd", description="Adds a sound to the sound library")
    async def soundadd(self, ctx, name, url):
        sound = SoundFile(ctx.guild, name, url, title=name)
        try:
            sound.add_command()
            await ctx.send(f"Added {name} to sounds!")
        except:
            await ctx.send(f"Couldn't add {name} to sounds.")

    @commands.command(name="play", description="Plays a sound from the sound library")
    async def play(self, ctx, sound):
        await self.sound_handler(sound, ctx.guild.id)

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="sounddelete", description="Deletes a sound from the sound library")
    async def sound_delete(self, ctx, name):
        Command = Query()
        config = Config(ctx.guild)
        db = TinyDB(config.sounds)
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
    @commands.command(name="viewsounds", description="Shows the sounds in the sound library")
    async def viewsounds(self, ctx):
        config = Config(ctx.guild)
        db = TinyDB(config.sounds)
        sounds = [sound.get('command_name') for sound in db]
        await ctx.send(sounds)


def setup(bot):
    bot.add_cog(Sound(bot))
