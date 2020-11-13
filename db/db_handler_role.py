from db.models import *
from db import db_handler


async def link_emoji(guild, role, emoji):
    async with await db_handler.connection() as c:
        await c.run_sync(local_link_emoji, guild.id, role.id, emoji)


def local_link_emoji(session, guild_id, role_id, emoji):
    row = session.query(Roles).filter(Roles.guild_id == guild_id, Roles.id == role_id).one_or_none()
    if row:
        row.emoji = emoji
        session.commit()


async def unlink_emoji(guild, emoji):
    async with await db_handler.connection() as c:
        await c.run_sync(local_unlink_emoji, guild.id, emoji)


def local_unlink_emoji(session, guild_id, emoji):
    row = session.query(Roles).filter(Roles.guild_id == guild_id, Roles.emoji == emoji).one_or_none()
    row.emoji = None
    session.commit()


async def get_emoji_roles(guild):
    async with await db_handler.connection() as c:
        roles = await c.run_sync(local_get_emoji_roles, guild.id)
        return roles


def local_get_emoji_roles(session, guild_id):
    rows = session.query(Roles).filter(Roles.guild_id == guild_id).order_by(Roles.emoji)
    roles = []
    for row in rows:
        if row.emoji:
            role = {}
            role['name'] = row.name
            role['emoji'] = row.emoji
            roles.append(role)
        else:
            continue

    return roles


async def get_role_message_info(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_role_message_info, guild)


def local_get_role_message_info(session, guild_id):
    row = session.query(Configs).filter(Configs.id == guild_id).one_or_none()
    return row.reaction_message_id, row.reaction_channel_id


async def get_role(role):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_role, role.id)


def local_get_role(session, role_id):
    row = session.query(Roles).filter(Roles.id == role_id).one_or_none()
    return row


async def update_role_name(role, new_name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_update_role_name, role.id, new_name)


def local_update_role_name(session, role_id, new_name):
    row = local_get_role(session, role_id)
    row.name = new_name
    row.commit()


async def delete_role(role):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_delete_role, role.id)


def local_delete_role(session, role_id):
    session.query(Roles).filter(Roles.id == role_id).one_or_none().delete()
    session.commit()


async def set_channel(guild, channel, message):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_set_channel, guild.id, channel.id, message.id)


def local_set_channel(session, guild_id, channel_id, message_id):
    row = session.query(Configs).filter(Configs.id == guild_id).one_or_none()
    row.reaction_channel_id = channel_id
    row.reaction_message_id = message_id
    session.commit()


async def get_channel(guild):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_channel, guild.id)


def local_get_channel(session, guild_id):
    row = session.query(Configs).filter(Configs.id == guild_id).one_or_none()
    return row.reaction_channel_id, row.reaction_message_id
