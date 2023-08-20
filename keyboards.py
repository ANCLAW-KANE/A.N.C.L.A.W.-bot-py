from respond_who import WHO
from respond_priv import privileges
from tools import keyboard_params
from sessions import api_group


class keyboard_event(object):
    def __init__(self, pay, msg=None):
        self.msg = msg
        self.pay = pay
        self.pay_key_sep = str(list(self.pay.keys())[0]).split("_", 1)
        self.pay_state = self.pay_key_sep[1] if len(self.pay_key_sep) > 1 else self.pay_key_sep[0]
        self.pay_val = list(self.pay.values())[0]
        keyboard_params.user_sender = self.pay_val[0] if self.pay_val[0] else None
        keyboard_params.conv_msg_id_new = self.pay_val[2] if self.pay_val[2] else self.msg.conversation_message_id
        keyboard_params.conv_msg_id_old = self.pay_val[3] if self.pay_val[3] else None
        keyboard_params.pay_dir = self.pay_val[4] if self.pay_val[4] else None

    async def debug(self, *args):
        print(self.pay, self.pay_key_sep, "///", self.pay_val, self.pay_state)
        await api_group.messages.send(message=f"self.pay_state = {self.pay_state}\n"
                                              f"отправил :  {keyboard_params.user_sender}\n "
                                              f"ответил :  {keyboard_params.user_respond}\n"
                                              f"текущее :  {keyboard_params.conv_msg_id_new}\n"
                                              f"из payload :  {keyboard_params.conv_msg_id_old}\n"
                                              f"pay {keyboard_params.pay_dir}",
                                      peer_id=self.msg.peer_id, random_id=0)
        await api_group.messages.send(message=f"from :{args[0]}\n{self.pay}\n"
                                              f"{self.pay_key_sep}\n{self.pay_val}",
                                      peer_id=self.msg.peer_id, random_id=0)

    async def check_Callback(self):
        keyboard_params.user_respond = self.pay_val[1] if self.pay_val[1] else self.msg.user_id
        pay = {
            'M': WHO(obj=self.msg,
                     fromid=int(self.msg.user_id),
                     peer=int(self.msg.peer_id),
                     kb=[keyboard_params.user_sender,
                         keyboard_params.user_respond,
                         keyboard_params.conv_msg_id_new,
                         self.pay_state]).marry_control,

            'GOD': privileges(obj=self.msg,
                              sender=int(self.msg.user_id),
                              peer=int(self.msg.peer_id),
                              kb=[keyboard_params.pay_dir]).check

        }
        if self.pay_key_sep[0] or self.pay_key_sep in pay:
            #await self.debug(self.msg.user_id)
            if self.pay_key_sep[0] is not None: await pay.get(self.pay_key_sep[0])()
        keyboard_params().clear()

    async def check_event_msg(self):  # для совместимости с некоторыми клиентами (Kate mobile и тд)
        keyboard_params.user_respond = self.pay_val[1] if self.pay_val[1] else self.msg.from_id
        pay = {
            'M': WHO(obj=self.msg,
                     fromid=int(self.msg.from_id),
                     peer=int(self.msg.peer_id),
                     kb=[keyboard_params.user_sender,
                         keyboard_params.user_respond,
                         int(keyboard_params.conv_msg_id_new) - 1,
                         self.pay_state]).marry_control,

            'GOD': privileges(obj=self.msg,
                              sender=int(self.msg.from_id),
                              peer=int(self.msg.peer_id),
                              kb=[keyboard_params.pay_dir]).check

        }
        if self.pay_key_sep[0] or self.pay_key_sep in pay:
            #await self.debug(self.msg.from_id)
            if self.pay_key_sep[0] is not None: await pay.get(self.pay_key_sep[0])()
        keyboard_params().clear()
