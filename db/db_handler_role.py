from db.models import *
from db import db_handler


async def link_emoji(guild, role, emoji):
    async with await db_handler.connection() as c:
        await c.run_sync(local_link_emoji, guild.id, role.id, emoji)


# TODO: Add check for single emoji use per role (Add emoji_exists function?)
def local_link_emoji(session, guild_id, role_id, emoji):
    row = session.query(Roles).filter(Roles.guild_id == guild_id, Roles.id == role_id).one_or_none()
    if row:
        row.emoji = emoji
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