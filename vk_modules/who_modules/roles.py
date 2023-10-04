
import random
from database_module.peer_repo import PeerRepository
from vk_modules.online_tools import RandomMember

class Roles():
    def __init__(self,fromid):
        self.fromid = fromid

    async def role_func(self):# обработчик ролевых
        roles = await self.RepoRoles.check_roles()
        if roles and self.word_comm in roles: 
            key = await self.RepoRoles.get_roles(self.word_comm)
            self.send_msg.msg = f"{key[0]}   {self.sender}  {key[1]}  {self.name}  {key[2]}"

    async def battle(self):
        if self.sender != None and self.name != None:
            self.send_msg.msg = "📣🐖   Забив :\n\n 🇺🇦  {}  🇺🇦        🆚        ✡  {}  ✡\n\n🏆   Победил:  \
                    {}     🏆".format(self.sender,self.name,random.choice([self.sender, self.name]))
            
    async def who(self,obj):
        self.send_msg.msg = "❓ ➡    {}    ⬅  :    {}".format(await RandomMember(self.peer),obj)

    async def fact(self,obj):
        self.send_msg.msg =  "❗ Факт (  {}  )   {} ".format(obj,random.choice(['Ложь ⛔', 'Правда ✅']))
        
    async def probability(self,obj):
        self.send_msg.msg = "📊 Вероятность для  (  {}  ) :   {} %".format(obj,str(random.randint(0, 100)))

    async def role_sender(self,obj):
        self.send_msg.msg = f"{self.sender} {obj}"

    async def nickname(self):
        if self.args_len and self.args_len >=2:
                nick = ' '.join(self.list_args[1:])
                if len(nick) > 32:
                    self.send_msg.msg = "Ник не должен превышать 32 символов"
                else:
                    if self.list_args[0] == "мне":
                        await PeerRepository(self.peer,self.fromid).set_nickname(nick)#проверить
                        self.send_msg.msg = f" Ник установлен на ( {nick} )"
                    if self.tag:
                        await PeerRepository(self.peer,self.id).set_nickname(nick)
                        self.send_msg.msg = f" Ник для {self.name} установлен на ( {nick} )"


################################################################################################
