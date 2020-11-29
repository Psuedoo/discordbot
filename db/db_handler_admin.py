from db.models import *
from db import db_handler


async def set_streamer_id(guild, streamer_id):
    async with await db_handler.connection() as c:
        return await c.run_sync(local_set_streamer_id, guild.id, streamer_id)


def local_set_streamer_id(session, guild_id, streamer_id):
    guild = session.query(Configs).filter(Configs.id == guild_id).one_or_none()
    guild.streamer_id = streamer_id
    session.commit()
