from builders import ExtendParams,String_parse,NameBuilder
from database_module.Tables import MarryRepository,RoleRepository
from tools import data_msg,Patterns
from handlers.who_modules.marry import FuncMarry
from handlers.who_modules.roles import Roles


class RoleCommand(ExtendParams,String_parse,NameBuilder,Roles,FuncMarry):
    def __init__ (self, fromid, peer, obj=None, txt=None):
        self.obj = obj
        self.fromid = fromid
        self.peer = peer
        self.send_msg = data_msg()
        ExtendParams.__init__(self)
        String_parse.__init__(self,txt,obj)
        NameBuilder.__init__(self,fromid,peer)
        Roles.__init__(self,fromid)
        FuncMarry.__init__(self,fromid)
        self.params()
        self.parse("!")
        self.RepoMarry = MarryRepository(self.peer,fromid)
        self.RepoRoles = RoleRepository(self.peer,fromid)

    ######################################################################################################
    async def str_command(self):
        s_obj = None
        if self.args_len != None:
            if self.args_len >= 1 and  Patterns.pattern_bool(self.string_args,
                    [Patterns.user_pattern, Patterns.club_pattern],"or") == False: s_obj = self.string_args
        if s_obj:
            items = {
                    "кто": self.who,
                    "вероятность": self.probability,
                    "факт": self.fact,
                    "я": self.role_sender
                }
            i = items.get(self.word_comm,None) 
            if i: await i(s_obj)
    ######################################################################################################
    async def func_command(self):
        items_func = {
                "забив": self.battle,
                "брак": self.marry_query_handler,
                "браки": self.marry_list,
                "ник": self.nickname
            }  
        if self.word_comm in items_func:
            i = items_func.get(self.word_comm)
            if i: await i()

    ######################################################################################################
    async def Check(self):
        await self.construct()
        """print(f"self.reply = {self.reply}\n" ,
            f"self.kb_l = {self.kb_l}\n" , f"self.tag = {self.tag}\n" , f"self.id = {self.id}\n" , f"self.name = {self.name}\n" , 
            f"self.string_all = {self.string_all}\n" , f"self.list_args = {self.list_args}\n" , f"self.str_len = {self.str_len}\n", 
            f"self.args_len = {self.args_len}\n" , f"self.word_comm = {self.word_comm}\n" , f"self.find_tag = {self.find_tag}\n" , f"self.conv_id = {self.conv_id}\n") """ 
        if self.string_all is not None:
            await self.role_func()
            await self.str_command()
            await self.func_command()
            await self.send_msg.send(self.obj)

######################################################################################################