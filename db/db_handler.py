import os
import asyncio
import sqlalchemy as db
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from .models import *

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
        guilds = session.query(Guilds).filter(Guilds.id == str(guild_id))
        return len(guilds.all()) > 0
        # try return not (guilds is None) TELL PYGON THE OUTCOME (needs the one_or_none)

    def get_prefix(self, guild_id):
        if guild_exists(guild_id):
            prefix = session.query(Configs).filter(id == str(guild_id)).first()
        else:
            prefix = "!"
        return prefix

    # def get_command(self, session, guild_id, command):
    #     commands = session.query(Commands).filter(Commands.guild_id == str(guild_id))
    #     if command in commands.all():
    #         return command

    async def get_commands(self, guild):
        async with await self.connection() as c:
            return await c.run_sync(self.local_get_commands, guild.id)

    def local_get_commands(self, session, guild_id):
        commands = session.query(Commands).filter(Commands.guild_id == str(guild_id))
        return [{'name': command.name, 'response': command.response} for command in commands]

    async def get_command(self, guild, command_name):
        async with await self.connection() as c:
            return await c.run_sync(self.local_get_command, guild.id, command_name)

    def local_get_command(self, session, guild_id, command_name):
        command = session.query(Commands).filter(Commands.guild_id == str(guild_id), Commands.name == command_name).first()
        return command.response

