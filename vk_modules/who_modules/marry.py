from vk_modules.kb_handlers.func_handler_keyboard import KeyboardRepository
from tools import Patterns, keyboard_params

class FuncMarry():
    def __init__(self,fromid):
        self.fromid = fromid

    ################################################################################################
    async def clear_marry(self):
        await self.RepoMarry.clear_all_marry_fromid()
        self.send_msg.msg = f"Теперь вы свободны от отношений!"
        self.send_msg.keyboard = None
    
    async def _check_polygam_and_create(self,key):
        marry_polygam =await self.RepoMarry.get_polygam_marry()
        print(await self.RepoMarry.get_married_from_ids())
        if marry_polygam == 1 or (marry_polygam == 0 and await self.RepoMarry.get_married_from_ids() < 1):
            await self.RepoMarry.create_new_marry(self.id,self.sender, self.name)
            self.send_msg.msg = f"{self.name} ! Пользователь {self.sender} сделал вам предложение руки и сердца."
            self.send_msg.keyboard = key
        else:
            self.send_msg.msg = "Администратор запретил множественные браки в этом чате!"
            self.send_msg.keyboard = None
         
    async def create_marry(self):
        params = await self.RepoMarry.peer_params_marry(selfid=self.id)
        key = KeyboardRepository.MarryKB(keyboard_params(user_sender= self.fromid, 
                                                         user_recipient= self.id,
                                                         conv_msg_id_old= self.conv_id+1).build())
        #print(f"married_from_ids {await self.RepoMarry.get_married_from_ids()}",f"params {params}")
        if params:
            if params['await'] == 1:
                self.send_msg.msg = f"Брак уже подан и находится в ожидании!\n{self.name} примите или отклоните"
                self.send_msg.keyboard = key
            elif params['allow'] == 1: self.send_msg.msg = f"Вы уже в браке с этим человеком!\n" 
        else: await self._check_polygam_and_create(key)
            
    async def unmarry(self):
        await self.RepoMarry.unmarry_fromid(self.id)
        self.send_msg.msg = f"Вы отозвали брак с {self.name}!"
        self.send_msg.keyboard = None
    
    async def marry_query_handler(self):
        if Patterns.pattern_bool(self.string_args,[Patterns.club_pattern]) == False: 
            if 'холост' in self.string_all: 
                await self.clear_marry()
            if self.id is not None:
                await self.create_marry()
                if 'развод' in self.string_all: await self.unmarry()
        else: self.send_msg.msg = "Нельзя подать брак сообществу, так как оно вам не ответит"
    ################################################################################################
    async def marry_list(self):
        string = None
        msgstring = ""
        if self.args_len == 1:
            strings = { 
                "ожидание": ["Ждут согласия 👫\n", "💝", self.RepoMarry.awaited_marry ],
                "я": ["Ваши браки  👫\n", "💝", self.RepoMarry.marry_allow]
            }
            string = strings.get(self.list_args[0], None)
        else: string = [" Помолвлены 👩‍❤‍👨\n", "💞", self.RepoMarry.marry_all_allow]
        if string is not None:
            data =  await string[2]()
            if not data: msgstring = "Ничего не найдено"
            else:
                msgstring += f"{string[0]}"
                for z in data: msgstring += f"{string[1]} {z[0]} - {z[1]} {string[1]}\n"
        self.send_msg.msg = msgstring
################################################################################################