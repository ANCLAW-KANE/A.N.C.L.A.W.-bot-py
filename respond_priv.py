import aiosqlite
import traceback

from vkbottle import Keyboard, KeyboardButtonColor, Callback

from CONFIG import IdGroupVK
from online_tools import RandomMember, getUserName
from sessions import api_group, max_user_id
from tools import json_config, logger, data_msg, keyboard_params, DB_Manager


######################################################################################################
class privileges(object):
    def __init__(self, sender, peer, obj, kb=None, txt=None):
        if kb is None: kb = [None]
        self.txt = txt
        self.sender = sender
        self.peer = peer
        self.obj = obj
        self.kb = kb
        self.cnvmgid = self.obj.conversation_message_id
        self.EVIL_GODS = json_config().cfg_json()['EVIL_GODS']

    ################## привелегия для удаления сообщений не админов(ультимативный мут) #################
    async def EVIL_GOD(self):
        BD = await aiosqlite.connect('peers.db')
        edit = await BD.cursor()
        await edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.peer}")
        E_G = await edit.fetchone()
        # print(self.sender)
        try:
            if self.sender not in self.EVIL_GODS and 0 < self.sender < max_user_id:
                if E_G[1] == '1': await api_group.messages.delete(peer_id=self.peer, cmids=self.cnvmgid,
                                                                  group_id=IdGroupVK, delete_for_all=1)
                if E_G[3] == '1':
                    await api_group.messages.delete(peer_id=self.peer, conversation_message_ids=self.cnvmgid,
                                                    group_id=IdGroupVK, delete_for_all=1)
                    data_msg.msg = f"{await getUserName(self.sender)} *Впечатан в землю*"
                if E_G[4] == '1':
                    data_msg.msg = f"{await RandomMember(self.peer)} насилует {await RandomMember(self.peer)}"
        except:
            logger(f"\n_____________________\n{traceback.format_exc()}\n_____________________\n\n\n", "ERROR.log")
        await BD.close()

    ######################################################################################################
    async def check(self):
        if self.sender in self.EVIL_GODS:
            z = DB_Manager(database='peers.db', query=f"SELECT * FROM peers WHERE peer_id = {self.peer}",
                           m1='', m2='', peer=str(self.peer), update="", on_index=None, type_=str, arg=str(self.peer))
            privilege = {
                '*присутствие злого бога*':
                    (await z(m1='Безмолвие', m2='*Безмолвие Уходит*',
                             update=f"UPDATE peers SET e_g_mute = ? where peer_id = ?",
                             on_index=1)).key,
                '*ваши головы подняты слишком высоко*':
                    (await z(m1='*Раздавлены*', m2='*Гравитация отключена*',
                             update=f"UPDATE peers SET e_g_head = ? where peer_id = ?",
                             on_index=3)).key,
                '*адская похоть*':
                    (await z(m1='Исполнено Похоть', m2='*Похоть развеяна*',
                             update=f"UPDATE peers SET e_g_ex = ? where peer_id = ?",
                             on_index=4)).key,
            }
            if self.txt in privilege:
                key = privilege.get(self.txt)
                if key is not None: await key()

            if self.kb[0] in privilege:
                key = privilege.get(self.kb[0])
                if key is not None: await key()

            elif self.txt == '* EVIL GOD *':
                data_msg.msg = f'Доступно только админам бота\n______________________________\n'
                for z in list(privilege):
                    data_msg.msg += f"🔥 {z} 🔥\n\n"
                data_msg.keyboard = Keyboard(False, True) \
                    .add(Callback("*присутствие злого бога*", payload={
                    "GOD":
                        keyboard_params(False, False, False, False, "*присутствие злого бога*").build()}),
                         color=KeyboardButtonColor.NEGATIVE).row() \
                    .add(Callback("*ваши головы подняты слишком высоко*", payload={
                    "GOD":
                        keyboard_params(False, False, False, False, "*ваши головы подняты слишком высоко*").build()}),
                         color=KeyboardButtonColor.NEGATIVE).row() \
                    .add(Callback("*адская похоть*", payload={
                    "GOD":
                        keyboard_params(False, False, False, False, "*адская похоть*").build()}),
                         color=KeyboardButtonColor.NEGATIVE).get_json()
######################################################################################################
