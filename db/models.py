from sqlalchemy import delete
from sqlalchemy import create_engine
from sqlalchemy import Table, Boolean, Column, String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Guilds(Base):
    __tablename__ = 'guilds'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(20))
    owner_id = Column(BigInteger)
    config = relationship('Configs', backref='guilds', cascade='all, delete')
    roles = relationship('Roles', backref='guilds', cascade='all, delete')
    sounds = relationship('SoundsAssociation', backref='guilds', cascade='all, delete')
    commands = relationship('Commands', backref='guilds', cascade='all, delete')
    streamers = relationship('StreamersAssociation', backref='guilds', cascade='all, delete')


class Configs(Base):
    __tablename__ = 'configs'
    id = Column(BigInteger, ForeignKey('guilds.id'), primary_key=True)
    # guild = relationship('Guilds', back_populates='configs')
    # guild_id = Column(BigInteger, ForeignKey('guilds.id'), primary_key=True)
    prefix = Column(String(10))


class Roles(Base):
    __tablename__ = 'roles'
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    # guild = relationship('Guilds', back_populates='roles', cascade='all, delete')
    name = Column(String(20))
    emoji = Column(String(50))
    # This data should be in config
    reaction_message_id = Column(BigInteger)
    reaction_channel_id = Column(BigInteger)


class Sounds(Base):
    __tablename__ = 'sounds'
    id = Column(Integer, primary_key=True)
    # guild_id = Column(Integer, ForeignKey('guilds.id'), primary_key=True)
    guild = relationship('SoundsAssociation', backref='sounds')
    name = Column(String(20))
    url = Column(String(500))
    file_directory = Column(String(100))


class SoundsAssociation(Base):
    __tablename__ = 'soundsassociation'
    id = Column(Integer, primary_key=True)
    # guild = relationship('Guilds', back_populates='sounds')
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    # sound = relationship('Sounds', back_populates='guilds')
    sound_id = Column(Integer, ForeignKey('sounds.id'))
    command = Column(String(20))


class Commands(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    # guild = relationship('Guilds', back_populates='commands')
    name = Column(String(20))
    response = Column(String(500))


class Streamers(Base):
    __tablename__ = 'streamers'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    guild = relationship('StreamersAssociation', backref='streamers')
    name = Column(String(20))
    url = Column(String(500))


class StreamersAssociation(Base):
    __tablename__ = 'streamersassociation'
    guild_id = Column(BigInteger, ForeignKey('guilds.id'), primary_key=True)
    streamer_id = Column(BigInteger, ForeignKey('streamers.id'), primary_key=True)
    announcement_channel_id = Column(BigInteger)
    alert = Column(Boolean)


if __name__ == '__main__':
    def delete_tables(engine, base):
        for tbl in base.metadata.sorted_tables:
            if not tbl.name == 'commands':
                # engine.execute(tbl.delete())
                tbl.drop(engine)


    engine = create_engine('postgresql://psuedo@192.168.0.179/discordbot_dev', echo=True)
    user_input = input("1. Create Tables\n"
                       "2. Delete Tabels\n"
                       "3. Renew Tables\n> ")
    if user_input == '1':
        Base.metadata.create_all(engine)
    elif user_input == '2':
        delete_tables(engine, Base)
    elif user_input == '3':
        delete_tables(engine, Base)
        Base.metadata.create_all(engine)
