import discord
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

    @commands.command(name="join")
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        self.voice_client = await channel.connect()

    @commands.command(name="leave")
    async def leave(self, ctx):
        channel = ctx.author.voice.channel
        await self.voice_client.disconnect()
         

def setup(bot):
    bot.add_cog(Sound(bot))
