import os
import discord
import asyncio
import youtube_dl
import secrets
from pathlib import Path
from cogs.utils import checks
from discord.ext import commands

from db import db_handler, db_handler_sound, db_handler_admin
from db.models import Sounds
from db.models import SoundsAssociation


class Sound(commands.Cog):
    """*Commands for sound functionality*"""

    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
        self.queue = asyncio.Queue()
        self.lock = asyncio.Lock()
        self.hidden = False
        self.path = Path.cwd() / 'sounds'

        if not self.path.is_dir():
            self.path.mkdir()

    async def _handle_play(self, item, client):
        future = asyncio.Future()
        loop = asyncio.get_event_loop()

        def after(*args):
            loop.call_soon_threadsafe(future.set_result, args)

        client.play(discord.FFmpegOpusAudio(os.path.expanduser(item)),
                    after=after)
        callback_args = await future
        return callback_args

    async def handle_queue(self, client):
        while not self.queue.empty():
            if not client.is_playing():
                item = await self.queue.get()
                await self._handle_play(item, client)
                self.queue.task_done()

    async def sound_handler(self, sound, discord_id, client):
        sound = await self.get_sound_file(sound, discord_id)
        if sound:
            await self.queue.put(sound)
            async with self.lock:
                task = asyncio.create_task(self.handle_queue(client))
                await self.queue.join()
                await asyncio.gather(task)
        else:
            print("No sound")

    async def get_sound_file(self, command_name, discord_id=None):
        guild = self.bot.get_guild(int(discord_id))
        return await db_handler_sound.get_sound_directory(guild, command_name)

    def download_sound(self, url, file_path):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': f'{file_path}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio'
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in self.path.iterdir():
            if file.stem == file_path.stem:
                return file

    def generate_ydl_opts(self, file_path):
        return

    @commands.command(name="join", description="Joins the voice chat of command author")
    async def join(self, ctx=None, twitch_channel=None, discord_id=None):

        # If Twitch_channel_name == guild.fetch_member(config.streamer_id) and streamer is in VC: Join that vc
        if not ctx:
            guild = self.bot.get_guild(int(discord_id))
            streamer_id = await db_handler_sound.get_streamer_id(guild)
            streamer = await guild.fetch_member(streamer_id)
            channel = streamer.voice.channel
            if channel:
                return await channel.connect()
            else:
                print("No channel to connect to")

        elif ctx and ctx.voice_client:
            channel = ctx.author.voice.channel
            return await ctx.voice_client.move_to(channel)
        elif ctx and not ctx.voice_client:
            channel = ctx.author.voice.channel
            return await channel.connect()

    @commands.command(name="leave", description="Disconnects the bot from the voice channel")
    async def leave(self, ctx=None):
        await ctx.voice_client.disconnect()

    # TODO : Sometimes when trying to add sound it doesn't do audio only
    @commands.check(checks.is_bot_enabled)
    @commands.command(name="soundadd", description="Adds a sound to the sound library")
    async def soundadd(self, ctx, command_name, url):
        # Generates a name and directory based on name
        name = secrets.token_urlsafe(16)
        file_path = Path.cwd() / 'sounds' / f'{name}'

        # Determining if the sound or solely an association exists
        sound_id = await db_handler_sound.sound_exists(url)
        association_sound_id = await db_handler_sound.association_exists(ctx.guild, url)

        channel_name = await db_handler_admin.get_twitch(ctx.guild)

        # There is a valid sound, but no association
        if sound_id and not association_sound_id:
            data = [SoundsAssociation(guild_id=ctx.guild.id,
                                      sound_id=sound_id,
                                      command=command_name,
                                      channel_name=channel_name)]
            await db_handler.insert(data)
            await ctx.send(f'{command_name} has been added!')

        # There is no sound (there can't be an association if there is no sound)
        elif not sound_id:
            file_path = self.download_sound(url, file_path)
            data = [Sounds(name=name,
                           url=url,
                           file_directory=str(file_path))]
            await db_handler.insert(data)

            sound_id = await db_handler_sound.get_sound_id(name)

            data = [SoundsAssociation(guild_id=ctx.guild.id,
                                      sound_id=sound_id,
                                      command=command_name,
                                      channel_name=channel_name)]
            await db_handler.insert(data)

            await ctx.send(f'{command_name} has been added!')
        else:
            await ctx.send(f'{command_name} already exists!')

    @commands.command(name="play", description="Plays a sound from the sound library")
    async def play(self, ctx, sound):
        if not ctx.voice_client:
            await self.join(ctx)
        await self.sound_handler(sound, ctx.guild.id, ctx.voice_client)

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="sounddelete", description="Deletes a sound from the sound library")
    async def sound_delete(self, ctx, command_name):
        try:
            await db_handler_sound.delete_sound(ctx.guild, command_name)
        except:
            await ctx.send(f'Could not delete {command_name}.')
        else:
            await ctx.send(f'Successfully deleted {command_name}')

    # TODO : Make viewsounds look prettier
    @commands.check(checks.is_bot_enabled)
    @commands.command(name="viewsounds", description="Shows the sounds in the sound library")
    async def viewsounds(self, ctx):
        await ctx.send(await db_handler_sound.view_guild_sounds(ctx.guild))


def setup(bot):
    bot.add_cog(Sound(bot))
