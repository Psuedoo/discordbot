import os
import asyncio
import sqlalchemy as db
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from .models import Configs, Guilds, initialize_db

class DatabaseHandler:
    def __init__(self):
        self.USERNAME = os.getenv("POSTGRES_USER", None)
        self.PASSWORD = os.getenv("POSTGRES_PASSWORD", None)
        self.SERVER_IP = os.getenv("SERVER_IP", None)
        self.DATABASE_NAME = os.getenv("POSTGRES_DB", None)
        self.session = initialize_db()

    async def connection(self):
        engine = create_async_engine(f'postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@{self.SERVER_IP}/{self.DATABASE_NAME}', echo=True)
        session = AsyncSession(bind=engine)
        return session

    async def insert(self, data=[]):
        async with await self.connection() as c:
            c.add_all(data)
            await c.commit()
    
    async def initialize_guilds(self, guilds=[]):
        async with await self.connection() as c:
            for guild in guilds:
                if not await c.run_sync(self.guild_exists, guild.id):
                    print(f'Adding {guild.name} to database.')

                    data = [
                        Guilds(
                            id=str(guild.id),
                            name=guild.name,
                            owner_id=str(guild.owner_id)
                        ),
                        Configs(
                            id=str(guild.id),
                            prefix=os.getenv('PREFIX', '/')
                        )
                    ]

                    await self.insert(data)

    def guild_exists(self, session, guild_id):
        guilds = session.query(Guilds).filter(str(Guilds.id) == str(guild_id))
        return len(guilds.all()) > 0