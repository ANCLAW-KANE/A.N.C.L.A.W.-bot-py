from tools import unpack_keys


class Info:

    def __init__(self):
        pass
#######################################/i - инфокоманды ######################################
    async def id_user(self,reply):
        self.send_msg.msg = f"Ваш ID - {self.fromid}"
        if reply: self.send_msg.msg = f"ID пользователя - {self.reply.from_id}"

    async def id_chat(self):
        self.send_msg.msg = f"ID чата - {self.peer}"
        
    async def id_message(self,reply):
        if reply: self.send_msg.msg = f"ID сообщения - {self.reply.conversation_message_id}"
        else: self.send_msg.msg = f"Ответьте на нужное сообщение этой командой для вывода ID сообщения"
    
    async def info_module(self):
        reply_flag = True if self.reply else False
        inf = {
            'idchat': (self.id_chat,()),
            'id': (self.id_user,(reply_flag,)),
            'idm': (self.id_message,(reply_flag,))
        }
        if self.args_len is not None and self.args_len >= 1:
            key = inf.get(self.list_args[0])
            await key[0](*key[1])
        else:
            self.send_msg.msg = f"/i:\n {unpack_keys(inf,'ℹ️')}"

