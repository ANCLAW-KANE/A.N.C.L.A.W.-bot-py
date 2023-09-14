from online_tools import getUserName
from tools import Patterns
from sessions import max_user_id
from database_module.Tables import PeerRepository

class ExtendParams:
    def params(self):
        self.sender = ""        # имя отправителя
        self.reply = None       # ответ на сообщение
        self.kb_l = None        # создание параметров клавиатуры 
        self.tag = None         # временнная переменная в NameBuilder
        self.id = None          # id из тега
        self.name = None        # имя из тега
        self.string_all = None  # разбиение строки
        self.list_args = None   # получение списка аргументов
        self.string_args = ' '  # строка из аргументов
        self.str_len = None     # количество элементов всей строки
        self.args_len = None    # количество полученных аргументов
        self.word_comm = None   # команда
        self.find_tag = None    # хранение тега
        self.conv_id = None     # id сообщения в чате

class NameBuilder:
    def __init__(self,fromid,peer):
        self.fromid = fromid
        self.peer = peer

    async def construct(self):
        await self._parse_tags()
        await self._sender_name()

    async def _sender_name(self):# получение имени отправителя
        if 0 < int(self.fromid) < max_user_id:
            prfx = 'id'
            group = False
        else: 
            prfx = 'club'
            group = True
        id = abs(self.fromid)
        if await self.nickname_check(id):
            self.sender = f"@{prfx}{id}({(await self.nickname_check(id))[0]})"
        else: self.sender = f"@{prfx}{id}({await getUserName(id,group)})"

    async def _get_reply(self):
        if self.reply:
            if 0 < int(self.reply.from_id) < max_user_id:
                prfx = 'id'
                group = False
            else: 
                prfx = 'club'
                group = True
            self.tag = self.reply.from_id
            self.id = abs(int(self.tag))
            if await self.nickname_check(self.id):
                self.name = f"@{prfx}{self.id}({(await self.nickname_check(self.id))[0]})"
            else: self.name = f"@{prfx}{self.id}({await getUserName(self.id,group)})"

    async def nickname_check(self,id):
        nick = await PeerRepository(self.peer,id).check_nick()
        return nick

    async def _parse_tags(self):
        if self.reply is None and self.find_tag and (self.find_tag['users'] or self.find_tag['clubs']):
                    if self.find_tag['users'] != []: 
                        self.tag =  self.find_tag['users'][0]#только первое найденное упоминание
                        prfx = 'id'
                        group = False
                    else:
                        self.tag = self.find_tag['clubs'][0]
                        prfx = 'club'
                        group = True
                    self.id = int(self.tag['id'])
                    if '@' not in self.tag['text']:
                        self.name =  f"@{prfx}{self.id}({self.tag['text']})" # тег если упоминание с текстом
                    else:
                        #тег если есть ник в бд
                        self.name = f"@{prfx}{self.id}({(await self.nickname_check(self.id))[0]})"\
                                    if await self.nickname_check(self.id)\
                                    else f"@{prfx}{self.id}({await getUserName(self.id,group)})" # тег с простым упоминанием
        else: await self._get_reply()

######################################################################################################
class String_parse:
    def __init__(self,msg,obj):
        self.msg = msg
        self.obj = obj

    def parse(self,prefix):
        if self.msg is not None:
            self.string_all = str(self.msg).lower().split(sep=' ') 
            self.str_len = len(self.string_all)
            if self.str_len > 1: 
                self.list_args = self.string_all[1:]  # аргументы
                self.args_len = len(self.list_args) 
                self.string_args = ' '.join(self.list_args)
                self.find_tag = Patterns.get_mentions(self.msg) # упоминания
                print(self.find_tag)
            self.word_comm = self.string_all[0].replace(prefix, '')     
        if self.obj is not None:
            self.reply = self.obj.reply_message
            self.conv_id = self.obj.conversation_message_id