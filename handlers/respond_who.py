import random
import re
import aiosqlite
from loguru import logger
from sqlalchemy import and_, or_, select

from vkbottle import Keyboard, KeyboardButtonColor, Callback, ShowSnackbarEvent
from vkbottle.bot import Message, BotLabeler
from CONFIG import IdGroupVK
from hadlers_rules import PrefixRoleRule
from online_tools import get_tag, getUserName, RandomMember, send
from sessions import api_group
from tools import DB_Manager, data_msg, keyboard_params
from database_module.Tables import DBexec, DynamicsTables, Marry,rolesDB,peerDB


class RoleCommand(object):
    def __init__(self, fromid, peer, obj=None, msg=None, kb=None):
        self.reply = self.kb_l = self.tag = self.id = self.name = self.string_all = self.string = self.s_len_ \
            = self.s_len = self.word_comm = self.find_tag = self.conv_id = None
        self.string_all = str(self.msg).lower().split(sep=' ')  # деление всего текста по пробелу
        self.s_len_ = len(self.string_all)
        self.string = str(self.msg).lower().split(maxsplit=1, sep=' ')  # деление текста по 1 пробелу
        self.s_len = len(self.string)  #
        self.word_comm = self.string[0].replace('!', '')
        self.obj = obj
        self.msg = msg
        self.fromid = fromid
        self.peer = str(peer)
        self.from_kb = kb
        self.sender = ""
        self.msgstring = ''
        ########################################### Закрытые методы ######################################################

    async def _name_builder(self):
        if self.msg is not None:
            if self.s_len_ > 1: self.find_tag = list(filter(re.compile(r"\[id\w+").match, self.string_all)) #находит тэг в сообщении
        ##################################################################################################################
        if self.obj is not None:
            self.reply = self.obj.reply_message
            self.conv_id = self.obj.conversation_message_id
        print("reply : : : ", self.reply)
        print("findtag : : : ",self.find_tag)
        ##################################################################################################################
        if self.reply is None:
            if self.find_tag:
                self.tag = await get_tag(self.find_tag[0]) 
                self.id = int(self.tag['tag_id'])
                self.name = f"@id{self.tag['tag_id']}({await getUserName(self.tag['tag_id'])})" if '@' in self.tag['tag_name'] \
                    else f"@id{self.tag['tag_id']}({self.tag['tag_name']})"
            ##############################################################################################################
        else:
            if int(self.reply.from_id) > 0:
                self.tag = self.reply.from_id
                self.id = int(self.tag)
                self.name = f"@id{self.tag}({await getUserName(self.tag)})"
        ##################################################################################################################

    async def _sender_name(self):# получение имени отправителя
        name = await getUserName(self.fromid)
        self.sender = f"@id{self.fromid}({name})"
            
    ##################################################################################################################
    async def _str_command(self):
        items = {
                "!кто": f"❓ ➡    {await RandomMember(self.peer)}    ⬅  :    {self.s_obj}",
                "!вероятность": f"📊 Вероятность для  (  {self.s_obj}  ) :   {str(random.randint(0, 100))} %",
                "!забив": f"📣🐖   Забив :\n\n 🇺🇦  {self.sender}  🇺🇦        🆚        ✡  {self.name}  ✡\n\n🏆   Победил:  \
                           {random.choice([self.sender, self.name])}     🏆",
                "!факт": f"❗ Факт (  {self.s_obj}  )   {random.choice(['Ложь ⛔', 'Правда ✅'])} ",
                "!я": f"{self.sender} {self.string[1] if self.s_len >= 2 else None}"
            }
        self.msgstring = items.get(self.string[0],None)

    async def _func_command(self):
        items_func = {
                "!брак": FuncMarry.marry_query,
                "!браки": FuncMarry.marry_list,
                "!ник": Roles.nickname
            }  
        if self.string[0] in items_func:
            i = items_func.get(self.string[0])
            if i: await i()

    ######################################################################################################
    async def Check(self): 
        await self._name_builder()
        await self._sender_name()
        # print(self.fromid, self.id, self.tag, self.name, self.conv_id, self.sender)
        if self.string is not None:
            self.s_obj = self.string[1] if self.s_len >= 2 else self.name
            ######################################### Обработка #########################################
            await Roles.role_func()
            await self._func_command()
            await self._str_command()
            ###########################################################################################################
            if self.msgstring != '' and self.msgstring.find('None') == -1: data_msg.msg = self.msgstring

################################################################################################
class Roles(RoleCommand):
    async def role_func(self):# обработчик ролевых
        tR = await DynamicsTables(self.peer).tableRoles()
        if self.word_comm in await DBexec(rolesDB,select(tR.c.command)).dbselect(): 
            key = await DBexec(rolesDB,select(tR.c.emoji_1, tR.c.txt, tR.c.emoji_2).where(
                tR.c.command == self.word_comm)).dbselect("one")
            self.msgstring = f"{key[0]}   {self.sender}  {key[1]}  {self.name}  {key[2]}"

    async def nickname(self):
        if self.s_len_ >=3:
            nick = str(' '.join(self.string_all[2:]))
            if self.string_all[1] == "мне":
                BD = await aiosqlite.connect('peers.db')
                edit = await BD.cursor()
                await edit.execute(f"INSERT OR IGNORE INTO nicknames VALUES({self.peer},{self.fromid},'{nick}')")
                await BD.commit()

################################################################################################
class FuncMarry(RoleCommand):
    def __init__(self, fromid, peer, obj=None, msg=None, kb=None):
        super().__init__(fromid, peer, obj, msg, kb)

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
        if 'холост' in self.string_all:
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
            if 'развод' in self.string_all:
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
            DBexec(peerDB,m).dbedit()

    ################################################################################################
    

    async def marry_list(self):
        string = None
        if self.s_len_ >= 2:
            strings = { 
                "ожидание": ["Ждут согласия 👫\n", "💝", 
                             select(Marry.man1name, Marry.man2name).where(and_(Marry.allow == 0, Marry.peer_id == self.peer))
                            ],

                "я": ["Ваши браки  👫\n", "💝", 
                      select(Marry.man1name, Marry.man2name).where(
                          and_(or_(Marry.man1 == self.fromid, Marry.man2 == self.fromid),
                          Marry.allow == 1, Marry.peer_id == self.peer))
                    ]
            }
            string = strings.get(self.string_all[1], None)
        else:
            string = [" Помолвлены 👩‍❤‍👨\n", "💞", 
                      select(Marry.man1name, Marry.man2name).where(Marry.allow == 1, Marry.peer_id == self.peer)
                    ]
        if string is not None:
            data = await DBexec(peerDB,string[2]).dbselect()
            if not data:
                self.msgstring = "Ничего не найдено"
            else:
                self.msgstring += f"{string[0]}"
                for z in data: self.msgstring += f"{string[1]} {z[0]} - {z[1]} {string[1]}\n"
################################################################################################

labeler = BotLabeler()

@labeler.message(PrefixRoleRule(),blocking=False)
async def RoleCommand(msg: Message):
    logger.log("STATE","\n_________________________ROL_________________________")
    await RoleCommand(fromid=msg.from_id, peer=msg.peer_id, msg=msg.text, obj=msg).Check()
    await send(msg)