import random
import re
import aiosqlite

from vkbottle import Keyboard, KeyboardButtonColor, Callback, ShowSnackbarEvent

from CONFIG import IdGroupVK
from online_tools import get_tag, getUserName, RandomMember
from sessions import api_group
from tools import DB_Manager, data_msg, keyboard_params


class WHO(object):
    def __init__(self, fromid, peer, obj=None, msg=None, kb=None):
        self.comm = ''
        self.reply = self.kb_l = self.tag = self.id = self.name = self.string_ = self.string = self.s_len_ \
            = self.s_len = self.word_comm = self.find_tag = self.conv_id = None
        self.obj = obj
        self.msg = msg
        self.fromid = fromid
        self.peer = peer
        self.from_kb = kb
        self.sender = ""
        self.msgstring = ''
        ######################################

    async def name_builder(self):
        if self.msg is not None:
            self.string_ = str(self.msg).lower().split(sep=' ')  # деление всего текста по пробелу
            self.s_len_ = len(self.string_)
            self.string = str(self.msg).lower().split(maxsplit=1, sep=' ')  # деление текста по 1 пробелу
            self.s_len = len(self.string)  #
            self.word_comm = self.string[0].replace('!', '')
            self.comm = await DB_Manager('peers_roles.db', f"SELECT command FROM '{self.peer}'").get_one_col_list()
            if self.s_len_ > 1: self.find_tag = list(filter(re.compile(r"\[id\w+").match, self.string_))
        ######################################
        if self.obj is not None:
            self.reply = self.obj.reply_message
            self.conv_id = self.obj.conversation_message_id
        # print(self.reply)
        # print(self.find_tag)
        ######################################
        if self.reply is None:
            if self.find_tag:
                self.tag = await get_tag(self.find_tag[0])
                self.id = int(self.tag[2])
                self.name = f"@id{self.tag[0]}({await getUserName(self.tag[0])})" if '@' in self.tag[1] \
                    else f"@id{self.tag[0]}({self.tag[1]})"
            ######################################
        else:
            if int(self.reply.from_id) > 0:
                self.tag = self.reply.from_id
                self.id = int(self.tag)
                self.name = f"@id{self.tag}({await getUserName(self.tag)})"
        ######################################

    async def sender_name(self):
        name = await getUserName(self.fromid)
        self.sender = f"@id{self.fromid}({name})"

    ############################################################### MARRY ############################################
    async def marry_control(self):
        BD = await aiosqlite.connect('peers.db')
        edit = await BD.cursor()
        a = await edit.execute(f'SELECT * FROM marry where peer_id = {self.peer} and'
                               f' man1 = {self.from_kb[0]} and man2 = {self.fromid}')
        params = await a.fetchone()
        info = False
        if params is not None:
            if self.peer == params[1] and self.fromid == self.from_kb[1] == params[3] and params[2] == self.from_kb[0]:
                if params[6] == 0 and params[7] == 1:
                    m1, m2 = await getUserName(self.fromid), await getUserName(self.from_kb[0])
                    if self.from_kb[3] == 'ACCEPT':
                        q = f"UPDATE marry SET allow = {1} , await = {0} where peer_id = {self.peer} and " \
                            f"man1 = {self.from_kb[0]} and man2 = {self.fromid}"
                        message = f"@id{self.fromid}({m1})  и  @id{self.from_kb[0]}" \
                                  f"({m2}) поженились! Поздравьте молодую пару!"
                    else:
                        q = f"DELETE FROM marry where peer_id = {self.peer} and " \
                            f"man1 = {self.from_kb[0]} and man2 = {self.fromid}"
                        message = f"@id{self.from_kb[0]}({m2}) ! \n" \
                                  f"@id{self.fromid}({m1}) отказался от вашего предложеня"
                    await edit.execute(q)
                    await BD.close()
                    # await api_group.messages.send(peer_id=self.peer, random_id=0, message=
                    # f"{q}\n{params}\n{self.peer}\n"
                    # f"{self.fromid}\n{self.from_kb}")
                    await api_group.messages.edit(peer_id=self.peer, conversation_message_id=self.from_kb[2],
                                                  group_id=IdGroupVK, message=message)
                    await BD.commit()
                else:
                    info = "Брак не зарегистрирован или уже оформлен"
            else:
                info = "Ты не подавал брак"
        else:
            info = "Куда ты жмешь -_-"
        if info: await api_group.messages.send_message_event_answer(event_id=self.obj.event_id,
                                                                    user_id=self.obj.user_id,
                                                                    peer_id=self.obj.peer_id,
                                                                    event_data=ShowSnackbarEvent(text=info).json())

    ################################################################################################
    async def marry_query(self):
        BD = await aiosqlite.connect('peers.db')
        edit = await BD.cursor()
        m = None
        if 'холост' in self.string_:
            m = f"DELETE FROM marry where peer_id = {self.peer} and man1 = {self.fromid} or man2 = {self.fromid}"
            data_msg.msg = f"Теперь вы свободны от отношений!"
        elif self.id is not None:
            num = (await DB_Manager('peers.db', f"SELECT * from marry", on_index=0).BD_COUNT())
            froms = (await DB_Manager('peers.db', f"SELECT man1 FROM marry where peer_id = "
                                                  f"{self.peer} and man1 = {self.fromid}").get_one_col_list())
            params = (await (await edit.execute(f"SELECT allow,await,id,peer_id FROM marry where peer_id = "
                                                f"{self.peer} and (man1 = {self.fromid} and man2 = {self.id})"
                                                f"or (man1 = {self.id} and man2 = {self.fromid})")).fetchone())
            marry_polygam = (await (await edit.execute(
                f"SELECT poligam_marry FROM peers where peer_id = {self.peer}")).fetchone())[0]
            self.kb_l = keyboard_params(self.fromid, self.id, False, self.conv_id, False).build()
            key = Keyboard(False, True) \
                .add(Callback("Принять", payload={"M_ACCEPT": self.kb_l}), color=KeyboardButtonColor.POSITIVE) \
                .add(Callback("Отклонить", payload={"M_DENY": self.kb_l}),
                     color=KeyboardButtonColor.NEGATIVE).get_json()
            # print(f"kb : {self.kb_l}\nmpgm : {marry_polygam}\nparams : {params}\nfroms : "
            #      f"{froms}\nlen:  {len(froms)}\nnum: {num}")
            if 'развод' in self.string_:
                m = f"DELETE FROM marry where peer_id = {self.peer} and (man1 = {self.fromid} and man2 = {self.id})" \
                    f" or (man1 = {self.id} and man2 = {self.fromid})"
                data_msg.msg = f"Вы отозвали брак с {self.name}!"
            ##############################
            else:
                if (params is None) or (params[3] != self.peer):
                    if marry_polygam == 1 or (marry_polygam == 0 and len(froms) < 1):
                        m1, m2 = await getUserName(self.fromid), await getUserName(self.id)
                        m = f'INSERT OR IGNORE INTO marry VALUES({max(num) + 1},{self.peer},' \
                            f'{self.fromid},{self.id},"{m1}","{m2}",{0},{1})'
                        data_msg.msg = f"{self.name} ! Пользователь {self.sender} сделал вам предложение руки и сердца."
                        data_msg.keyboard = key
                    else:
                        data_msg.msg = "Администратор запретил множественные браки в этом чате!"
                ##############################
                else:
                    if params[1] == 1:
                        data_msg.msg = f"Брак уже подан и находится в ожидании!\n{self.name} примите или отклоните"
                        data_msg.keyboard = key
                    if params[0] == 1: data_msg.msg = f"Вы уже в браке с этим человеком!\n"
        if m is not None:
            BD = await aiosqlite.connect('peers.db')
            edit = await BD.cursor()
            await edit.execute(m)
        await BD.commit()
        await BD.close()

    ################################################################################################
    

    async def marry_list(self):
        string = None
        BD = await aiosqlite.connect('peers.db')
        edit = await BD.cursor()
        if len(self.string_) >= 2:
            strings = {
                "ожидание": ["Ждут согласия 👫\n", "💝",
                             f"SELECT man1name ,man2name from marry "
                             f"where allow = 0 and peer_id = {self.peer}"],
                "я": ["Ваши браки  👫\n", "💝", f"SELECT man1name ,man2name from marry "
                                                f"where (man1 = {self.fromid} or man2 = {self.fromid}) "
                                                f"and allow = 1 and peer_id = {self.peer}"]
            }
            if self.string_[1] in strings:
                string = strings.get(self.string_[1])
        else:
            string = [" Помолвлены 👩‍❤‍👨\n", "💞",
                      f"SELECT man1name ,man2name from marry where allow = 1 and peer_id = {self.peer}"]
        if string is not None:
            self.msgstring += f"{string[0]}"
            data = await(await edit.execute(string[2])).fetchall()
            if not data:
                self.msgstring = "Ничего не найдено"
            else:
                for z in data: self.msgstring += f"{string[1]} {z[0]} - {z[1]} {string[1]}\n"
        await BD.close()

    async def role(self):
        BD = await aiosqlite.connect('peers_roles.db')
        edit_role = await BD.cursor()
        await edit_role.execute(f"SELECT emoji_1, txt, emoji_2 FROM '{self.peer}' where command = '{self.word_comm}' ")
        key = await edit_role.fetchone()
        await BD.close()
        self.msgstring = f"{key[0]}   {self.sender}  {key[1]}  {self.name}  {key[2]}"

    ######################################################################################################
    async def WHO_GET(self):
        await self.name_builder()
        await self.sender_name()
        #await self.marry_fix()
        # print(self.fromid, self.id, self.tag, self.name, self.conv_id, self.sender)
        RandName = await RandomMember(self.peer)
        if self.string is not None:
            s_obj = self.string[1] if self.s_len >= 2 else self.name
            ######################################### Обработка #########################################
            items = {
                "!кто": f"❓ ➡    {RandName}    ⬅  :    {s_obj}",
                "!вероятность": f"📊 Вероятность для  (  {s_obj}  ) :   {str(random.randint(0, 100))} %",
                "!забив": f"📣🐖   Забив :\n\n 🇺🇦  {self.sender}  🇺🇦        🆚        ✡  {self.name}  ✡\n\n🏆   Победил:  \
                           {random.choice([self.sender, self.name])}     🏆",
                "!факт": f"❗ Факт (  {s_obj}  )   {random.choice(['Ложь ⛔', 'Правда ✅'])} ",
                "!я": f"{self.sender} {self.string[1] if self.s_len >= 2 else None}"
            }
            items_func = {
                "!брак": self.marry_query,
                "!браки": self.marry_list,
            }
            ##########################################################################################################
            if self.string[0] in items: self.msgstring = items.get(self.string[0])
            if self.string[0] in items_func:
                i = items_func.get(self.string[0])
                if i is not None: await i()
            ################################################# role #################################################
            if self.word_comm in self.comm: await self.role()
            ###########################################################################################################
            if self.msgstring != '' and self.msgstring.find('None') == -1: data_msg.msg = self.msgstring
