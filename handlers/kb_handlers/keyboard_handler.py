import json
from handlers.kb_handlers.func_handler_keyboard import KeyboardEventHandler
from sessions import api_group


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
            'M': self.marry_control,
            'GOD': self.privileges_control

        }
        if self.keys['dir'] or self.pay_key_sep in pay:
            #await self.debug()
            if self.keys['dir'] is not None: 
                await pay.get(self.keys['dir'])()

