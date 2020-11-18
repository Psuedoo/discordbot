from db.models import *
from db import db_handler


async def get_commands(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_commands, guild.id)


def local_get_commands(session, guild_id):
    rows = session.query(Commands).filter(Commands.guild_id == guild_id)
    commands = []
    for row in rows:
        commands.append({'name': row.name, 'response': row.response})

    return commands


async def get_command_names(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_command_names, guild.id)


def local_get_command_names(session, guild_id):
    rows = session.query(Commands.name).filter(Commands.guild_id == guild_id)
    return [row.name for row in rows.all()]


async def get_response(guild, name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_response, guild.id, name)


def local_get_response(session, guild_id, name):
    return session.query(Commands.response).filter(Commands.guild_id == guild_id, Commands.name == name).one_or_none()


async def delete_command(guild, name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_delete_command, guild.id, name)


def local_delete_command(session, guild_id, name):
    session.query(Commands).filter(Commands.guild_id == guild_id, Commands.name == name).delete()
    session.commit()