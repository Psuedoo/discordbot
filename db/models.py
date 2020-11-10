from sqlalchemy import Table, Boolean, Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Guilds(Base):
    __tablename__ = 'guilds'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    owner_id = Column(Integer)
    config = relationship('Configs', back_populates='configs')
    roles = relationship('Roles', back_populates='roles')
    sounds = relationship('SoundsAssociation', back_populates='guilds')
    commands = relationship('Commands', back_populates='commands')
    streamers = relationship('StreamersAssociation', back_populates='guilds')


class Configs(Base):
    __tablename__ = 'configs'
    id = Column(Integer, ForeignKey('parent.id'), primary_key=True)
    guild = relationship('Guilds', back_populates='guilds')
    prefix = Column(String(10))


class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    guild = relationship('Guilds', back_populated='guilds')
    name = Column(String(20))
    emoji = Column(String(50))
    reaction_message_id = Column(Integer)
    reaction_channel_id = Column(Integer)


class Sounds(Base):
    __tablename__ = 'sounds'
    id = Column(Integer, primary_key=True)
    guild = relationship('SoundsAssociation', back_populates='sounds')
    name = Column(String(20))
    url = Column(String(500))
    file_directory = Column(String(100))


class SoundsAssociation(Base):
    __tablename__ = 'soundsassociation'
    guild= relationship('Guilds', back_populates='sounds')
    sound = relationship('Sounds', back_populates='guilds')
    command = Column(String(20))


class Commands(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True)
    guild = relationship('Guilds', back_populates='guilds')
    name = Column(String(20))
    response = Column(String(500))


class Streamers(Base):
    __tablename__ = 'streamers'
    id = Column(Integer, primary_key=True)
    guild = relationship('StreamersAssocation', back_populates='streamers')
    name = Column(String(20))
    url = Column(String(500))


class StreamersAssociation(Base):
    __tablename__ = 'streamersassociation'
    guild = relationship('Guilds', back_populate='streamers')
    streamer = relationship('Streamers', back_populates='guilds')
    announcement_channel_id = Column(Integer)
    alert = Column(Boolean)