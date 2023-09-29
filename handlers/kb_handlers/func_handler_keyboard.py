from CONFIG import IdGroupVK
from database_module.cabal_repo import CabalRepository
from database_module.marry_repo import MarryRepository
from tools import keyboard_params,Formatter
from sessions import api_group
from vkbottle import Keyboard, KeyboardButtonColor, Callback, ShowSnackbarEvent

class KeyboardRepository:
    def MarryKB(param):
        return Keyboard(False, True) \
            .add(Callback("Принять", payload={"M_ACCEPT": param}),color=KeyboardButtonColor.POSITIVE) \
            .add(Callback("Отклонить", payload={"M_DENY": param}),color=KeyboardButtonColor.NEGATIVE).get_json()
    
    def PrivlegesKB():
        return Keyboard(False, True) \
                    .add(Callback("🔥 *присутствие злого бога* 🔥", payload={
                    "GOD":
                        keyboard_params(pay_dir="присутствие злого бога").build()}),
                         color=KeyboardButtonColor.NEGATIVE).row() \
                    .add(Callback("🔥 *ваши головы подняты слишком высоко* 🔥", payload={
                    "GOD":
                        keyboard_params(pay_dir="ваши головы подняты слишком высоко").build()}),
                         color=KeyboardButtonColor.NEGATIVE).row() \
                    .add(Callback("🔥 *адская похоть* 🔥", payload={
                    "GOD":
                        keyboard_params(pay_dir="адская похоть").build()}),
                         color=KeyboardButtonColor.NEGATIVE).get_json()

######################################################################################################################

class KeyboardEventHandler:
    def __init__(self):
        self.kb = self.reconstruct_payload
        self.RepoMarry = MarryRepository(self.peer,self.fromid)

    async def _find_msg_fix(self,list_msg,message):
        ids = list(range(self.kb['msg_old'],self.kb['msg_new']))
        if len(ids) == 0:
            await api_group.messages.edit(peer_id=self.peer, conversation_message_id=self.kb['msg_new'],
                                                  group_id=IdGroupVK, message=message)
        else:#поиск сообщения для редактирования если точный id заранее не известен
            ids_info = await api_group.messages.get_by_conversation_message_id(peer_id=self.peer,conversation_message_ids=ids)
            for i in ids_info.items:
                if i.text in list_msg:
                    await api_group.messages.edit(peer_id=self.peer, conversation_message_id=i.conversation_message_id,
                                                  group_id=IdGroupVK, message=message)
                    

    async def marry_control(self):
        params = await self.RepoMarry.params_marry_control(self.kb['sender'])
        info = False
        if params is not None:
            if self.peer == params['peer_id']\
                and self.fromid == self.kb['recipient'] == params['man2']\
                and params['man1'] == self.kb['sender']:
                if params['allow'] == 0 and params['await_state'] == 1:
                    if self.kb['state'] == 'ACCEPT':
                        await self.RepoMarry.marry_accept(kb=self.kb['sender'])
                        message = f"{params['man1name']}  и  {params['man2name']} поженились! Поздравьте молодую пару!"
                    if self.kb['state'] == 'DENY':
                        await self.RepoMarry.marry_deny(kb=self.kb['sender'])
                        message = f"{params['man2name']} ! \n {params['man1name']} отказался от вашего предложеня"
                    await self._find_msg_fix(list_msg=[
                        f"{Formatter.reformat_mention(params['man2name'])} ! Пользователь"\
                            f" {Formatter.reformat_mention(params['man1name'])} сделал вам предложение руки и сердца.",
                        f"Брак уже подан и находится в ожидании!\n"\
                            f"{Formatter.reformat_mention(params['man2name'])} примите или отклоните"],message= message)
                else: info = "Брак не зарегистрирован или уже оформлен"
            else: info = "Куда ты жмешь -_-"
        else: info = "Доступ запрещен"
        if info:
            try: 
                await api_group.messages.send_message_event_answer(event_id=self.msg.event_id,
                                                                    user_id=self.msg.user_id,
                                                                    peer_id=self.msg.peer_id,
                                                                    event_data=ShowSnackbarEvent(text=info).json())
            except: await api_group.messages.send(message=info, peer_id=self.peer, random_id=0)
            
    async def privileges_control(self):
        cRepo = CabalRepository(self.peer, self.fromid)
        privilege = {
                'присутствие злого бога': cRepo.set_priveleges_mute,
                'ваши головы подняты слишком высоко':cRepo.set_priveleges_head,
                'адская похоть': cRepo.set_priveleges_ex,
            }
        if self.kb['dir'] in privilege:
            key = privilege.get(self.kb['dir'])
            if key: 
                msg = await key()
                await api_group.messages.send(message=msg, peer_id=self.peer, random_id=0)
######################################################################################################################