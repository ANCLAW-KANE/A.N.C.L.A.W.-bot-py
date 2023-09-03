from sqlalchemy import Integer, Column, MetaData, Text, UniqueConstraint, Table
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

path = 'sqlite+aiosqlite:///database_module/'

peerDB = create_async_engine(f'{path}peer.db')
quotesDB = create_async_engine(f'{path}peer_quotes.db')
rolesDB = create_async_engine(f'{path}peer_roles.db')
wordsDB = create_async_engine(f'{path}peer_words.db')

BasePeer = declarative_base()
mdWords = MetaData()
mdRoles = MetaData()
mdQuotes = MetaData()

###############################################################################

class Peers(BasePeer):
    __tablename__ = "peers"
    peer_id = Column(autoincrement=False,primary_key=True,type_=Integer())
    count_period = Column(autoincrement=False,type_=Integer())
    e_g_mute = Column(autoincrement=False,type_=Integer())
    e_g_head = Column(autoincrement=False,type_=Integer())
    e_g_ex = Column(autoincrement=False,type_=Integer())
    resend = Column(autoincrement=False,type_=Integer())
    poligam_marry = Column(autoincrement=False,type_=Integer())
    words = Column(autoincrement=False,type_=Integer())
    quotes = Column(autoincrement=False,type_=Integer())

class Nodes(BasePeer):
    __tablename__ = "nodes"
    peer_id = Column(autoincrement=False,primary_key=True,type_=Integer())
    tg_id = Column(autoincrement=False,type_=Integer())
    vk_tg_allow = Column(autoincrement=False,type_=Integer())
    tg_vk_allow = Column(autoincrement=False,type_=Integer())

class Marry(BasePeer):
    __tablename__ = "marry"
    id = Column(primary_key=True,type_=Integer(),autoincrement=True)
    peer_id = Column(autoincrement=False,type_=Integer())
    man1 = Column(autoincrement=False,type_=Integer())
    man2 = Column(autoincrement=False,type_=Integer())
    man1name = Column(type_=Text())
    man2name = Column(type_=Text())
    allow = Column(autoincrement=False,type_=Integer())
    await_state = Column(autoincrement=False,type_=Integer())

class Nicknames(BasePeer):
    __tablename__ = "nicknames"
    peer_id = Column(autoincrement=False,primary_key=True,type_=Integer())
    user_id = Column(autoincrement=False,type_=Integer())
    nickname = Column(type_=Text())


###############################################################################

class DynamicsTables():
    def __init__(self,peer) -> None:
        self.peer = peer
    
    async def tableWords(self):
        return Table(self.peer,mdWords,
            Column(name='id', type_=Integer(),primary_key=True,autoincrement=True),
            Column(name='key', type_=Text()),
            Column(name='val', type_=Text()),
            extend_existing=True
        )
    
    async def tableRoles(self):# разобраться с автоинк
        return Table(self.peer,mdRoles,
            Column(name='id', type_=Integer(), primary_key=True,autoincrement=True),
            Column(name='command', type_=Text(), unique=True,autoincrement=False),
            Column(name='emoji_1', type_=Text()),
            Column(name='txt', type_=Text()),
            Column(name='emoji_2', type_=Text()),
            UniqueConstraint('id', 'command', name='new_pk'),
            extend_existing=True
        )
    
    async def tableQuotes(self):
        return Table(self.peer,mdQuotes,
            Column(name='id', type_=Integer(),primary_key=True,autoincrement=True),
            Column(name='quote', type_=Text()),
            extend_existing=True
        )

###############################################################################

async def create_peer_table(peer: str):
    if not isinstance(peer, str):
        peer = str(peer)
    mdW = await DynamicsTables(peer).tableWords()
    mdR = await DynamicsTables(peer).tableRoles()
    mdQ = await DynamicsTables(peer).tableQuotes()
    async with wordsDB.begin() as connect: await connect.run_sync(mdW.metadata.create_all,checkfirst=True)
    async with rolesDB.begin() as connect: await connect.run_sync(mdR.metadata.create_all,checkfirst=True)
    async with quotesDB.begin() as connect: await connect.run_sync(mdQ.metadata.create_all,checkfirst=True)

class DBexec():
    def __init__(self,bind,query):
        self.bind = bind
        self.session = scoped_session(sessionmaker(bind=bind,class_=AsyncSession, expire_on_commit=False, autoflush=True))()
        self.query = query

    async def dbselect(self,fetch:str="all"):
        async with self.session as s:
            async with s.begin_nested():
                if fetch == "one":
                    result = (await s.execute(self.query)).fetchone()[0]
                if fetch == "all":
                    result = (await s.execute(self.query)).fetchall()
            await s.close()
        return result
    
    async def dbedit(self):
        async with self.session as s:
            async with s.begin_nested():
                await s.execute(self.query)
                await s.commit()
        await s.close()
