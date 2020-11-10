import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import *


async def connection():
    engine = create_async_engine('postgresql://psuedo@192.168.0.179/discordbot_dev')
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
                data = [
                    Guilds(name=guild.name, owner_id=guild.owner_id),
                    Configs(prefix='?')
                ]
                for role in guild.roles:
                    data.append(Roles(name=role.name,
                                      emoji=None,
                                      reaction_message_id=None,
                                      reaction_channel_id=None))
                await insert(data)



def guild_exists(session, guild_id):
    if session.query(Guilds).filter(Guilds.id == guild_id):
        return True
