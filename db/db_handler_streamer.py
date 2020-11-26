from db.models import *
from db import db_handler
from sqlalchemy import desc


async def streamer_exists(url):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_streamer_exists, url)


def local_streamer_exists(session, url):
    row = session.query(Streamers).filter(Streamers.url == url).one_or_none()
    if row:
        return row.id
    return False


async def association_exists(guild, url):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_association_exists, guild.id, url)


def local_association_exists(session, guild_id, url):
    id = local_streamer_exists(session, url)
    if not id:
        return False
    row = session.query(StreamersAssociation).filter(StreamersAssociation.guild_id == guild_id,
                                                     StreamersAssociation.streamer_id == id).one_or_none()
    if row:
        return row.id
    return False


async def get_streamer_id(name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_streamer_id, name)


def local_get_streamer_id(session, name):
    row = session.query(Streamers).filter(Streamers.name == name).one_or_none()
    return row.id


async def get_newest_streamer_id(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_newest_streamer_id, guild.id)


def local_get_newest_streamer_id(session, guild_id):
    row = session.query(Streamers).filter(Streamers.guild_id == guild_id).order_by(desc(Streamers.id)).first()
    return row.id


async def remove_streamer(guild, name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_remove_streamer, guild.id, name)


def local_remove_streamer(session, guild_id, name):
    row = session.query(Streamers).filter(Streamers.name == name).one_or_none()
    if row:
        streamer_id = row.id

        associations = session.query(StreamersAssociation).filter(StreamersAssociation.streamer_id == streamer_id)

        if len([association for association in associations]) == 1:
            print(f'Only one association found for {name}... removing streamer..')
            session.query(StreamersAssociation).filter(StreamersAssociation.guild_id == guild_id,
                                                       StreamersAssociation.streamer_id == streamer_id).delete()
            session.query(Streamers).filter(Streamers.id == streamer_id).delete()
            session.commit()
            print('Streamer removed!')

        elif len([association for association in associations]) > 1:
            print(f'Found multiple associations, only removing streamer association for {name}')
            session.query(StreamersAssociation).filter(StreamersAssociation.guild_id == guild_id,
                                                       StreamersAssociation.streamer_id == streamer_id).delete()
            session.commit()
            print('Streamer removed!')


async def get_streamers(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_streamers, guild.id)


def local_get_streamers(session, guild_id):
    rows = session.query(StreamersAssociation).filter(StreamersAssociation.guild_id == guild_id)
    streamers = []
    for row in rows:
        streamer = session.query(Streamers).filter(Streamers.id == row.streamer_id).one_or_none()
        streamers.append(
            {
                'name': streamer.name,
                'url': streamer.url
            }
        )

    return streamers


async def get_streamer(name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_streamer, name)


def local_get_streamer(session, name):
    return session.query(Streamers).filter(Streamers.name == name).one_or_none()