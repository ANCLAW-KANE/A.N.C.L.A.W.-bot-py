from sqlalchemy import Integer, Column, MetaData, Text, UniqueConstraint, Table, delete, select, update, insert,DateTime
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.exc import ObjectNotExecutableError,DBAPIError
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

from tools import Formatter,check_index


path = 'sqlite+aiosqlite:///database_module/'

peerDB = create_async_engine(f'{path}peer.db')
quotesDB = create_async_engine(f'{path}peer_quotes.db')
rolesDB = create_async_engine(f'{path}peer_roles.db')
wordsDB = create_async_engine(f'{path}peer_words.db')
markovDB = create_async_engine(f'{path}peer_texts_markov.db')

BasePeer = declarative_base()
mdWords = MetaData()
mdRoles = MetaData()
mdQuotes = MetaData()
mdMarkov = MetaData()

##########################################################################################################################

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

class Mutes(BasePeer):
    __tablename__ = "mutes"
    id = Column(primary_key=True,type_=Integer(),autoincrement=True)
    peer_id = Column(autoincrement=False,type_=Integer())
    user_id = Column(autoincrement=False,type_=Integer())
    data_end = Column(type_=DateTime())

##########################################################################################################################

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

    async def tableMarkov(self):
        return Table(self.peer,mdMarkov,
            Column(name='txt', type_=Text(),primary_key=True,autoincrement=False),
            extend_existing=True
        )
    
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
    mdM = await DynamicsTables(peer).tableMarkov()
    await check_exist_table(wordsDB,peer,mdW)
    await check_exist_table(rolesDB,peer,mdR)
    await check_exist_table(quotesDB,peer,mdQ)
    await check_exist_table(markovDB,peer,mdM)


###################################################### TOOLS ###############################################################

class DBexec():
    def __init__(self,bind,query):
        self.bind = bind
        self.session = scoped_session(sessionmaker(bind=bind,class_=AsyncSession, expire_on_commit=False, autoflush=True))()
        self.query = query

    async def dbselect(self,fetch="all" ):
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
##########################################################################################################################

class DBmanager:
    def __init__(self,session,table,table_param,condition,messages: list) -> None:
        self.session = session
        self.table = table
        self.table_param = table_param
        self.condition = condition
        self.messages = messages

    async def key(self,value)-> str:  # для переключения 0 1 значений в БД
        try:
            param = await DBexec(self.session, select(self.table_param).where(self.condition)).dbselect(fetch='one')
            if param == 0:
                param = 1
                msg = self.messages[0]
            elif param == 1:
                param = 0
                msg = self.messages[1]
            await DBexec(self.session,update(self.table).where(self.condition).values({f"{value}": param})).dbedit()
            return msg
        except Exception as e: return f"Не выполнено, проверьте аргументы.{e}"

   
class Executor_with_access:# воспомогательный класс для некоторых запросов с проверкой прав

    def __init__(self,session,query,sender , message,access=None) -> None:
        self.session = session
        self.query = query
        self.sender = sender
        self.message = message
        self.access = access

    async def exec(self)-> str:
        if self.sender in self.access or self.access is None:
            try:
                await DBexec(self.session,self.query).dbedit()
                msg = self.message
                pass
            except DBAPIError:
                    msg = "Не выполнено, проверьте аргументы. (Или данная запись уже есть)"
        else:
            msg = "Нет прав"
        return msg
    
############################################ Repository Dynamics Tables strings ############################################
strings = {
            'delete_ids': "Операция не выполнена, проверьте аргументы. Шаблон команды (В <> одно из параметров):\n"\
                f"/settings <word,role,quote> delete\n1 2 3 4 ... (список id)",
            'update_roles': "Неверный формат, шаблон для создания(или обновления) роли : \n /settings role create\n"\
             f" Команда_без_пробелов\n эмоджи \n Строка действия \n Эмоджи \n",
             'update_words': "Операция не выполнена, укажите id для обновления:\n"\
                f"/settings <quote,word> update <id>\n Обновлённая строка>"
        }
