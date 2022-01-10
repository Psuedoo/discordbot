import os
from sqlalchemy import create_engine, Table, Boolean, Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm.session import sessionmaker

Base = declarative_base()

def initialize_db():
    USERNAME = os.getenv("POSTGRES_USER", None)
    PASSWORD = os.getenv("POSTGRES_PASSWORD", None)
    SERVER_IP = os.getenv("SERVER_IP", None)
    DATABASE_NAME = os.getenv("POSTGRES_DB", None)

    engine = create_engine(f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{SERVER_IP}/{DATABASE_NAME}', echo=True)

    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    Base.metadata.bind = engine
    Base.metadata.create_all(checkfirst=True)

    return session

class Guilds(Base):
    __tablename__ = 'guilds'

    id = Column(String(20), primary_key=True)
    name = Column(String(20))
    owner_id = Column(String(20))
    config = relationship('Configs', backref='guilds', cascade= 'all, delete')

class Configs(Base):
    __tablename__ = 'config'

    id = Column(String(20), ForeignKey('guilds.id'), primary_key=True)
    prefix = Column(String(10))
    