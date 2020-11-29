import os
import discord
from cogs.utils import checks
from discord.ext import commands
from db import db_handler, db_handler_streamer
from db.models import Streamers, StreamersAssociation


class Streamer(commands.Cog):
    """*Commands for the twitch streamers list*"""

    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds
        self.TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
        self.hidden = True

    # TODO: Add live notifications for streamers in config
    @commands.command(name="whoslive", description="Shows what streamers are currently live from the streamer library")
    async def whos_live(self, ctx, streamer):
        # reponse = requests.get()
        pass

    # TODO: Streamers.guild_id -> List; check list for associations and add if not in it
    @commands.check(checks.is_bot_enabled)
    @commands.command(name="addstreamer", description="Adds a streamer to the streamer library")
    async def add_streamer(self, ctx, streamer_url):

        streamer_id = await db_handler_streamer.streamer_exists(streamer_url)
        association_streamer_id = await db_handler_streamer.association_exists(ctx.guild, streamer_url)

        if streamer_id and not association_streamer_id:

            data = [StreamersAssociation(guild_id=ctx.guild.id,
                                         streamer_id=streamer_id,
                                         announcement_channel_id=ctx.guild.system_channel.id,
                                         alert=False)]
            await db_handler.insert(data)

            await ctx.send("They have been added!")
        elif not streamer_id and not association_streamer_id:

            streamer_name = streamer_url[streamer_url.rfind("/") + 1:]

            streamer_data = [Streamers(name=streamer_name,
                                       url=streamer_url)]

            await db_handler.insert(streamer_data)

            streamer_id = await db_handler_streamer.get_streamer_id(streamer_name)

            data = [StreamersAssociation(guild_id=ctx.guild.id,
                                         streamer_id=streamer_id,
                                         announcement_channel_id=ctx.guild.system_channel.id,
                                         alert=False)]
            await db_handler.insert(data)

            await ctx.send(f"{streamer_name} has been added!")
        else:
            await ctx.send("Streamer already exists!")

    @commands.check(checks.is_bot_enabled)
    @commands.command(name="removestreamer", description="Removes a streamer from the streamer library")
    async def remove_streamer(self, ctx, streamer_name):
        try:
            await db_handler_streamer.remove_streamer(ctx.guild, streamer_name.lower())
            await ctx.send(f'{streamer_name} has been removed!')
        except:
            await ctx.send(f'Could not remove {streamer_name}')

    @commands.command(name="viewstreamers", description="Displays the streamers in the streamer library")
    async def view_streamers(self, ctx):
        streamers = await db_handler_streamer.get_streamers(ctx.guild)
        if streamers:
            embed = discord.Embed(title="Streamers", description="Our community streamers")
            for streamer in streamers:
                embed.add_field(name=streamer['name'], value=streamer['url'], inline=False)
            await ctx.send(embed=embed)
        elif not streamers:
            await ctx.send('There are no streamers linked in the community')

    @commands.command(name="viewstreamer", description="Displays a certain streamer from the streamer library")
    async def view_streamer(self, ctx, streamer_name):
        streamer = await db_handler_streamer.get_streamer(streamer_name)
        if streamer:
            await ctx.send(f'{streamer.name}: {streamer.url}')
        else:
            await ctx.send(f'{streamer_name} not found.')


def setup(bot):
    bot.add_cog(Streamer(bot))
