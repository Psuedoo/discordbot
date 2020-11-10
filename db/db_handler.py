import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession


async def connection():
    engine = create_async_engine('postgresql://psuedo@192.168.0.179/discordbot_dev')
    session = AsyncSession(bind=engine)
    return session

async def create(insert=[]):
    async with await connection() as c:
        c.add_all(insert)
        await c.commit()

