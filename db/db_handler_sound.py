import os
from db.models import *
from db import db_handler


async def sound_exists(url):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_sound_exists, url)


def local_sound_exists(session, url):
    row = session.query(Sounds).filter(Sounds.url == url).one_or_none()
    if row:
        return row.id
    return False


async def association_exists(guild, url):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_assocation_exists, guild.id, url)


def local_assocation_exists(session, guild_id, url):
    sound_id = local_sound_exists(session, url)
    if not sound_id:
        return False
    row = session.query(SoundsAssociation).filter(SoundsAssociation.guild_id == guild_id,
                                                  SoundsAssociation.sound_id == sound_id).one_or_none()
    if row:
        return True
    return False


async def get_sound_id(name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_get_sound_id, name)


def local_get_sound_id(session, name):
    row = session.query(Sounds).filter(Sounds.name == name).one_or_none()
    return row.id


async def delete_sound(guild, command_name):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_delete_sound, guild.id, command_name)


def local_delete_sound(session, guild_id, command_name):
    association = session.query(SoundsAssociation).filter(SoundsAssociation.command == command_name,
                                                          SoundsAssociation.guild_id == guild_id).one_or_none()
    if association:
        sound_id = association.sound_id
        all_associations = session.query(SoundsAssociation).filter(SoundsAssociation.sound_id == sound_id)
        sound = session.query(Sounds).filter(Sounds.id == sound_id).one_or_none()
        sounds_list = [sound.command for sound in all_associations]

        if len(sounds_list) > 1:
            session.delete(association)
        elif len(sounds_list) == 1:
            if os.path.isfile(sound.file_directory):
                os.remove(sound.file_directory)

            session.delete(association)
            session.query(Sounds).filter(Sounds.id == sound_id).delete()

    else:
        return

    session.commit()
