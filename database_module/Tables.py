from sqlalchemy import Integer, Column, MetaData, Text, UniqueConstraint, Table, and_,\
delete, insert,  or_, select, update
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.exc import ObjectNotExecutableError
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from itertools import chain

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
    id = Column(primary_key=True,type_=Integer(),autoincrement=True)
    peer_id = Column(autoincrement=False,type_=Integer())
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

async def check_exist_table(bind,peer,meta):
    async with bind.begin() as connect: 
        try:
            await connect.execute(f"SELECT 1 FROM {peer} LIMIT 1")
        except ObjectNotExecutableError:
            await connect.run_sync(meta.metadata.create_all,checkfirst=True)

async def create_peer_table(peer: str):
    if not isinstance(peer, str):
        peer = str(peer)
    mdW = await DynamicsTables(peer).tableWords()
    mdR = await DynamicsTables(peer).tableRoles()
    mdQ = await DynamicsTables(peer).tableQuotes()
    await check_exist_table(wordsDB,peer,mdW)
    await check_exist_table(rolesDB,peer,mdR)
    await check_exist_table(quotesDB,peer,mdQ)


###############################################################################

class DBexec():
    def __init__(self,bind,query):
        self.bind = bind
        self.session = scoped_session(sessionmaker(bind=bind,class_=AsyncSession, expire_on_commit=False, autoflush=True))()
        self.query = query

    async def dbselect(self,fetch="all"):
        """
        fetch : str = "all"  запрос на всю выборку (default),\n
                      "one"  запрос на один параметр из списка,\n
                      "line" запрос на список параметров,
        """ 
        async with self.session as s:
            async with s.begin_nested():
                if fetch == "one":
                    try: result = (await s.execute(self.query)).fetchone()[0]
                    except: result = None##
                if fetch == "line":
                    result = (await s.execute(self.query)).fetchone()
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

###############################################################################

class MarryRepository:
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MarryRepository, cls).__new__(cls)
        return cls.instance

    def __init__(self,peer,fromid):
        self.peer = peer
        self.fromid = fromid
    ######################################## Select ######################################

    async def get_married_from_ids(self):
        ids = await DBexec(peerDB, select(Marry.man1,Marry.man2).filter(
            and_(Marry.peer_id == self.peer,
                    or_(Marry.man1 == self.fromid,Marry.man2 == self.fromid)))).dbselect()
        return list(chain.from_iterable(ids)).count(self.fromid)

    async def awaited_marry(self):
        return await DBexec(peerDB, select(Marry.man1name, Marry.man2name).where(
            and_(Marry.allow == 0, Marry.await_state == 1,Marry.peer_id == self.peer))).dbselect()
    
    async def marry_all_allow(self):
        return await DBexec(peerDB, select(Marry.man1name, Marry.man2name).where(
            Marry.allow == 1, Marry.peer_id == self.peer)).dbselect()

    
    async def marry_allow(self):
        return await DBexec(peerDB, select(Marry.man1name, Marry.man2name).where(
                          and_(or_(Marry.man1 == self.fromid, Marry.man2 == self.fromid),
                          Marry.allow == 1, Marry.peer_id == self.peer))).dbselect()
    
    async def peer_params_marry(self,selfid):
        params = await DBexec(peerDB,select(Marry.allow,Marry.await_state).where(
            and_(Marry.peer_id == self.peer,or_(
                    and_(Marry.man1 == self.fromid, Marry.man2 == selfid),
                    and_(Marry.man1 == selfid, Marry.man2 == self.fromid))))).dbselect("line")
        print(f"PA {params}")
        if params: return {"await":params[1],"allow": params[0]}
        else: return params

    async def get_polygam_marry(self):
        return await DBexec(peerDB,select(Peers.poligam_marry).where(Peers.peer_id == self.peer)).dbselect("one")

    async def params_marry_control(self,kb):
        fetch = await DBexec(peerDB,select(Marry).where(
            Marry.peer_id == self.peer,Marry.man1 == kb, Marry.man2 == self.fromid)).dbselect()
        params = fetch[0][0] if fetch else None
        if params: return{
            "peer_id": params.peer_id,
            "man1": params.man1,
            "man2": params.man2,
            "man1name": params.man1name,
            "man2name": params.man2name,
            "allow": params.allow,
            "await_state": params.await_state,
        }
        else:return None

    ######################################## Editor #######################################
    async def marry_accept(self,kb):
        await DBexec(peerDB, update(Marry).where(Marry.peer_id == self.peer, Marry.man1 == kb,
                                Marry.man2 == self.fromid).values(allow=1,await_state=0)).dbedit()

    async def marry_deny(self,kb):
        await DBexec(peerDB, delete(Marry).where(Marry.peer_id == self.peer,
                                         Marry.man1 == kb,Marry.man2 == self.fromid)).dbedit()

    async def clear_all_marry_fromid(self):
        await DBexec(peerDB, delete(Marry).where(
            and_(Marry.peer_id == self.peer, 
            or_(Marry.man1 == self.fromid,Marry.man2 == self.fromid)))).dbedit()

    async def create_new_marry(self,selfid,m1,m2):
        await DBexec(peerDB,insert(Marry).values(peer_id = self.peer,man1 = self.fromid,
                                man2 = selfid, man1name = m1, man2name = m2,
                                allow = 0, await_state = 1).prefix_with('OR IGNORE')).dbedit()

    async def unmarry_fromid(self,selfid):
        await DBexec(peerDB, delete(Marry).where(and_(Marry.peer_id == self.peer, or_(
            and_(Marry.man1 == self.fromid, Marry.man2 == selfid),
            and_(Marry.man1 == selfid, Marry.man2 == self.fromid))))).dbedit()
        
    async def marry_delete_fix(self):
        await DBexec(peerDB,delete(Marry).where(or_(Marry.man1name == 'None',Marry.man1name == 'DELETED ',
                                Marry.man2name == 'None',Marry.man2name == 'DELETED '))).dbedit()
        
###############################################################################

class RoleRepository:
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(RoleRepository, cls).__new__(cls)
        return cls.instance

    def __init__(self,peer,fromid):
        self.peer = peer
        self.fromid = fromid
    
    async def check_roles(self):
        tR = await DynamicsTables(self.peer).tableRoles()
        return await DBexec(rolesDB,select(tR.c.command)).dbselect()

    async def get_roles(self,word_comm):
        tR = await DynamicsTables(self.peer).tableRoles()
        return await DBexec(rolesDB,select(tR.c.emoji_1, tR.c.txt, tR.c.emoji_2).where(
                tR.c.command == word_comm)).dbselect("one")

###############################################################################
class PeerRepository:
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PeerRepository, cls).__new__(cls)
        return cls.instance

    def __init__(self,peer,fromid=None):
        self.peer = peer
        self.fromid = fromid

    async def create_settings_peer(self):
        await DBexec(peerDB,insert(Peers).values(peer_id=self.peer, count_period=0, e_g_mute = 0, e_g_head = 0,
            e_g_ex = 0, resend = 1, poligam_marry = 1, quotes = 1 , words = 1).prefix_with('OR IGNORE')).dbedit()
        
    async def check_nick(self):
        return await DBexec(peerDB,select(Nicknames.nickname).where(
            Nicknames.peer_id == self.peer,Nicknames.user_id == self.fromid)).dbselect("line")

    async def set_nickname(self,nick):
        print(await self.check_nick())
        if await self.check_nick():
            print("UPD")
            await DBexec(peerDB,update(Nicknames).where(
                Nicknames.peer_id == self.peer,Nicknames.user_id == self.fromid).values(nickname=nick)).dbedit()
        else: 
            print("INS")
            await DBexec(peerDB,insert(Nicknames).values(peer_id = self.peer, user_id = self.fromid, 
                    nickname = nick).prefix_with('OR IGNORE')).dbedit()
            
    async def get_count(self):
        return await DBexec(peerDB,select(Peers.count_period).where(Peers.peer_id == self.peer)).dbselect("one")


###############################################################################

class WordRepository:
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WordRepository, cls).__new__(cls)
        return cls.instance

    def __init__(self,peer,fromid=None):
        self.peer = peer

    async def get_words(self):
        tw = await DynamicsTables(self.peer).tableWords() 
        return await DBexec(wordsDB,select(tw.c.key,tw.c.val)).dbselect() 



###############################################################################


class QuoteRepository:
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(QuoteRepository, cls).__new__(cls)
        return cls.instance

    def __init__(self,peer,fromid=None):
        self.peer = peer

    async def get_quotes(self):
        tq = await DynamicsTables(self.peer).tableQuotes()
        return await DBexec(quotesDB,select(tq.c.quote)).dbselect()