from db.models import *
from db import db_handler


async def set_streamer_id(guild, streamer_id):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_set_streamer_id, guild.id, streamer_id)


def local_set_streamer_id(session, guild_id, streamer_id):
    guild = session.query(Configs).filter(Configs.id == guild_id).one_or_none()
    guild.streamer_id = streamer_id
    session.commit()


async def set_twitch(guild, channel_name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_set_twitch, guild.id, channel_name)


def local_set_twitch(session, guild_id, channel_name):
    guild = session.query(Guilds).filter(Guilds.id == guild_id).one_or_none()
    guild.twitch_channel = channel_name
    session.commit()


async def get_twitch(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_twitch, guild.id)


def local_get_twitch(session, guild_id):
    guild = session.query(Guilds).filter(Guilds.id == guild_id).one_or_none()
    return guild.twitch_channel


async def fix_sounds(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_fix_sounds, guild.id)


def local_fix_sounds(session, guild_id):
    sounds = session.query(SoundsAssociation).filter(SoundsAssociation.guild_id == guild_id)
    for sound in sounds:
        sound.channel_name = local_get_twitch(session, guild_id)
    session.commit()