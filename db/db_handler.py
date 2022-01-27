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
                            prefix=os.getenv('PREFIX', '/'),
                            role_message_id = None,
                            role_channel_id = None
                        ),
                    ]

                    await self.insert(data)

                    for role in guild.roles:
                        data = [
                            Roles(
                                id=str(role.id),
                                name=role.name,
                                emoji=None
                            )
                        ]

                        await self.insert(data)

    def guild_exists(self, session, guild_id):
        guilds = session.query(Guilds).filter(Guilds.id == str(guild_id))
        return len(guilds.all()) > 0
        # try return not (guilds is None) TELL PYGON THE OUTCOME (needs the one_or_none)

    async def get_prefix(self, guild):
        async with await self.connection() as c:
            return await c.run_sync(self.local_get_prefix, guild.id)


    def local_get_prefix(self, session, guild_id):
        prefix = session.query(Configs).filter(id == str(guild_id)).first()
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

    async def remove_command(self, guild, command_name):
        async with await self.connection() as c:
            return await c.run_sync(self.local_remove_command, guild.id, command_name)

    def local_remove_command(self, session, guild_id, command_name):
        command = session.query(Commands).filter(Commands.guild_id == str(guild_id), Commands.name == command_name).delete()
        session.commit()

        return command

    async def set_reaction_message(self, guild, message):
        async with await self.connection() as c:
            return await c.run_sync(self.local_set_reaction_message, guild.id, message.id, message.channel.id)
    
    def local_set_reaction_message(self, session, guild_id, message_id, channel_id):
        config = session.query(Configs).filter(Configs.id == str(guild_id)).first()
        config.role_message_id = str(message_id)
        config.role_channel_id = str(channel_id)
        session.commit()

    async def get_reaction_message(self, guild):
        async with await self.connection() as c:
            return await c.run_sync(self.local_get_reaction_message, guild.id)
    
    def local_get_reaction_message(self, session, guild_id):
        config = session.query(Configs).filter(Configs.id == str(guild_id)).first()

        return {
            'message_id': config.role_message_id,
            'channel_id': config.role_channel_id
        }