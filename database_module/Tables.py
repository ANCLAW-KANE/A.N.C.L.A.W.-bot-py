from sqlalchemy import Integer, Column, MetaData, Text, UniqueConstraint, Table, delete, select, update, DateTime
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.exc import ObjectNotExecutableError,DBAPIError
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from typing import Union , Any , List



path = 'sqlite+aiosqlite:///database_module/'

peerDB = create_async_engine(f'{path}peer.db')
hashDB = create_async_engine(f'{path}hash.db')
rolesDB = create_async_engine(f'{path}peer_roles.db')
wordsDB = create_async_engine(f'{path}peer_words.db')
markovDB = create_async_engine(f'{path}peer_texts_markov.db')

BasePeer = declarative_base()
BaseHash = declarative_base()
mdWords = MetaData()
mdRoles = MetaData()
mdMarkov = MetaData()

##########################################################################################################################

class Peers(BasePeer):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "peers"
    peer_id = Column(autoincrement=False,primary_key=True,type_=Integer())
    e_g_mute = Column(autoincrement=False,type_=Integer())
    e_g_head = Column(autoincrement=False,type_=Integer())
    e_g_ex = Column(autoincrement=False,type_=Integer())
    resend = Column(autoincrement=False,type_=Integer())
    poligam_marry = Column(autoincrement=False,type_=Integer())
    words = Column(autoincrement=False,type_=Integer())
    g_txt = Column(autoincrement=False,type_=Integer())
    g_dem = Column(autoincrement=False,type_=Integer())
    g_ldem = Column(autoincrement=False,type_=Integer())
    g_sticker = Column(autoincrement=False,type_=Integer())
    g_text_state = Column(autoincrement=False,type_=Integer())
    g_long_text_state = Column(autoincrement=False,type_=Integer())
    
class HashAudio(BaseHash):
    __tablename__ = "hashaudio"
    md5hash = Column(primary_key=True,autoincrement=False,type_=Text())
    url = Column(type_=Text())
    name_audio = Column(type_=Text())

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
    mdM = await DynamicsTables(peer).tableMarkov()
    await check_exist_table(wordsDB,peer,mdW)
    await check_exist_table(rolesDB,peer,mdR)
    await check_exist_table(markovDB,peer,mdM)


###################################################### TOOLS ###############################################################

class DBexec():
    FETCH_ONE = 'one'
    FETCH_LINE = 'line'
    FETCH_ALL = 'all'
    def __init__(self,bind,query: Union[List,Any]):
        self.bind = bind
        self.session = scoped_session(
            sessionmaker(bind=bind,class_=AsyncSession, expire_on_commit=False, autoflush=True))()
        self.query = query

    async def dbselect(self,fetch=FETCH_ALL):
        """
        fetch : 
            FETCH_ALL запрос на всю выборку (default),\n
            FETCH_ONE запрос на один параметр из списка,\n
            FETCH_LINE запрос на список параметров,
        """ 
        async with self.session as s:
            async with s.begin_nested():
                query = await s.execute(self.query)
                if fetch == DBexec.FETCH_ONE:
                    try: result = query.fetchone()[0]
                    except: result = None##
                elif fetch == DBexec.FETCH_LINE:
                    result = query.fetchone()
                elif fetch == DBexec.FETCH_ALL:
                    result = query.fetchall()
            await s.close()
        return result
    
    async def dbedit(self):
        async with self.session as s:
            async with s.begin_nested():
                if isinstance(self.query,list):
                    for obj in self.query:
                        await s.merge(obj)
                    await s.commit()
                else:
                    await s.execute(self.query)
                    await s.commit()
        await s.close()
##########################################################################################################################

class DBmanager:
    def __init__(self,session,table,table_param,condition,messages: list[str]) -> None:
        self.session = session
        self.table = table
        self.table_param = table_param
        self.condition = condition
        self.messages = messages

    def __invert__(self,param): # для переключения 0 1 значений в БД
        return (1,self.messages[0]) if param == 0 else ((0,self.messages[1]))

    async def key(self,value)-> str: 
        try:
            param_key = await DBexec(self.session, select(self.table_param).where(self.condition)).dbselect(fetch=DBexec.FETCH_ONE)
            param , msg = self.__invert__(param=param_key)
            await DBexec(self.session,update(self.table).where(self.condition).values({f"{value}": param})).dbedit()
            return msg
        except Exception as e: return f"Не выполнено, проверьте аргументы.{e}"

   
class Executor_with_access:# воспомогательный класс для некоторых запросов с проверкой прав

    def __init__(self,session,query,sender , message:str,access : list =None) -> None:
        self.session = session
        self.query = query
        self.sender = sender
        self.message = message
        self.access = access

    async def exec(self)-> str:
        if self.sender not in self.access or self.access is not None:
            return "Нет прав"
        try:
            await DBexec(self.session,self.query).dbedit()
            return self.message
        except DBAPIError:
            return "Не выполнено, проверьте аргументы. (Или данная запись уже есть)"
    
############################################ Repository Dynamics Tables strings ############################################
strings = {
            'delete_ids': "Операция не выполнена, проверьте аргументы. Шаблон команды (В <> одно из параметров):\n"\
                f"/settings <word,role> delete\n1 2 3 4 ... (список id)",
            'update_roles': "Неверный формат, шаблон для создания(или обновления) роли : \n /settings role create\n"\
             f" Команда_без_пробелов\n эмоджи \n Строка действия \n Эмоджи \n",
             'update_words': "Операция не выполнена, укажите id для обновления:\n"\
                f"/settings word update <id>\n Обновлённая строка>"
        }
