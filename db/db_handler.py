import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import *


async def connection():
    engine = create_async_engine('postgresql://psuedo@192.168.0.179/discordbot_dev', echo=True)
    session = AsyncSession(bind=engine)
    return session


async def insert(data=[]):
    async with await connection() as c:
        c.add_all(data)
        await c.commit()


async def initialize_guilds(guilds=[]):
    async with await connection() as c:
        for guild in guilds:
            if not await c.run_sync(guild_exists, guild.id):
                print(f"Adding {guild.name} to database.")
                data = [
                    Guilds(id=guild.id, name=guild.name, owner_id=guild.owner_id),
                    Configs(id=guild.id, prefix='?', reaction_message_id=None, reaction_channel_id=None)
                ]
                for role in guild.roles:
                    data.append(Roles(id=role.id,
                                      guild_id=guild.id,
                                      name=role.name,
                                      emoji=None))
                await insert(data)
            else:
                print(f"{guild.name} already exists in database. Skipping...")


def guild_exists(session, guild_id):
    guilds = session.query(Guilds).filter(Guilds.id == guild_id, Guilds.id > 0)
    if len(guilds.all()) > 0:
        return True


async def get_prefix(guild):
    async with await connection() as c:
        return await c.run_sync(local_get_prefix, guild.id)


def local_get_prefix(session, guild_id):
    row = session.query(Configs.prefix).filter(Configs.id == guild_id).one_or_none()
    return row.prefix


async def set_prefix(guild, prefix):
    async with await connection() as c:
        await c.run_sync(local_set_prefix, guild.id, prefix)


def local_set_prefix(session, guild_id, prefix):
    row = session.query(Configs).filter(Configs.id == guild_id).one_or_none()
    if row:
        row.prefix = prefix
        session.commit()
    else:
        print(f'No config for guild with id: {guild_id}')