from CONFIG import IdGroupVK
from database_module.Tables import MarryRepository
import json
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
                    .add(Callback("*присутствие злого бога*", payload={
                    "GOD":
                        keyboard_params(pay_dir="*присутствие злого бога*").build()}),
                         color=KeyboardButtonColor.NEGATIVE).row() \
                    .add(Callback("*ваши головы подняты слишком высоко*", payload={
                    "GOD":
                        keyboard_params(pay_dir="*ваши головы подняты слишком высоко*").build()}),
                         color=KeyboardButtonColor.NEGATIVE).row() \
                    .add(Callback("*адская похоть*", payload={
                    "GOD":
                        keyboard_params(pay_dir="*адская похоть*").build()}),
                         color=KeyboardButtonColor.NEGATIVE).get_json()

######################################################################################################################

class KeyboardEventHandler:
    def __init__(self):
        self.kb = self.reconstruct_payload
        self.RepoMarry = MarryRepository(self.peer,self.fromid)

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
                    ids = list(range(self.kb['msg_old'],self.kb['msg_new']))
                    if len(ids) == 0:
                        await api_group.messages.edit(peer_id=self.peer, conversation_message_id=self.kb['msg_new'],
                                                  group_id=IdGroupVK, message=message)
                    else:#поиск сообщения для редактирования если точный id заранее не известен
                        ids_info = await api_group.messages.get_by_conversation_message_id(peer_id=self.peer,
                                                                                           conversation_message_ids=ids)
                        for i in ids_info.items:
                            if i.text == f"{Formatter.reformat_mention(params['man2name'])} ! "\
                                f"Пользователь {Formatter.reformat_mention(params['man1name'])} сделал вам предложение руки и сердца."\
                            or i.text == f"Брак уже подан и находится в ожидании!\n"\
                                f"{Formatter.reformat_mention(params['man2name'])} примите или отклоните":
                                await api_group.messages.edit(peer_id=self.peer, conversation_message_id=i.conversation_message_id,
                                                  group_id=IdGroupVK, message=message)
                else:
                    info = "Брак не зарегистрирован или уже оформлен"
            else:
                info = "Куда ты жмешь -_-"
        else:
            info = "Ты не подавал брак"
        try: 
            if info: await api_group.messages.send_message_event_answer(event_id=self.msg.event_id,
                                                                    user_id=self.msg.user_id,
                                                                    peer_id=self.msg.peer_id,
                                                                    event_data=ShowSnackbarEvent(text=info).json())
        except:
            await api_group.messages.send(message=info, peer_id=self.peer, random_id=0)
            
######################################################################################################################

class keyboard_event(KeyboardEventHandler):
    def __init__(self, msg=None):
        try:
            self.msg = msg.object
            self.fromid = self.msg.user_id # берет user_id от события (обрабатывается как ид пользователя нажавшего кнопку)
        except: 
            self.msg = msg
            self.fromid = self.msg.from_id #берет from_id от события (для совместимости с клиентами (Kate mobile и тд))
        self.cmid = self.msg.conversation_message_id
        self.peer = self.msg.peer_id
        if isinstance(self.msg.payload,str): 
            pay = json.loads(self.msg.payload)# ответ от kate mobile
            self.pay = pay['payload'] if pay.get('payload',None) else pay #ответ от vtosters и подобных
        else: self.pay = self.msg.payload #обычный ответ
        self.pay_key_sep = str(list(self.pay.keys())[0]).split("_", 1)  # деление ключа на список аргументов
        self.keys = {
            "dir": self.pay_key_sep[0], # главный аргумент
            "values": list(self.pay.values())[0] # значения payload
        }
        self.reconstruct_payload = { #переработанные параметры из полученного ранее payload
            'sender' :  self.keys['values']['sender']if self.keys['values']['sender'] !=False else self.fromid,
            'recipient':self.keys['values']['recipient'] if self.keys['values']['recipient'] !=False else self.fromid,
            'msg_new' : self.cmid,
            'msg_old':  self.keys['values']['msg_old'],
            'dir':      self.keys['values']['dir'],
            'state':    self.pay_key_sep[1] if len(self.pay_key_sep) > 1 else False, #доп состояние
        }
        KeyboardEventHandler.__init__(self)

    async def debug(self):
        await api_group.messages.send(message=f"директория : {self.keys['dir']}\n"
                                              f"state = {self.reconstruct_payload['state']}\n"
                                              f"отправитель :  {self.reconstruct_payload['sender']}\n "
                                              f"адресат(для кого кнопки) :  {self.reconstruct_payload ['recipient']}\n"
                                              f"предыдущее сообщение :  {self.reconstruct_payload ['msg_new']}\n"
                                              f"id сообщения из payload :  {self.reconstruct_payload ['msg_old']}\n"
                                              f"доп параметры : {self.reconstruct_payload ['dir']}\n"
                                              f"нажавший кнопку : {self.fromid}\n"
                                              f"чат : {self.peer}",
                                      peer_id=self.msg.peer_id, random_id=0)

    async def check_Callback(self):
        
        pay = {
            'M': self.marry_control

            #'GOD': privileges(obj=self.msg,
            #                  sender=int(self.msg.user_id),
            #                  peer=int(self.msg.peer_id),
            #                  kb=[keyboard_params.pay_dir]).check

        }
        if self.keys['dir'] or self.pay_key_sep in pay:
            #await self.debug()
            if self.keys['dir'] is not None: 
                await pay.get(self.keys['dir'])()

