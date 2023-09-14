from loguru import logger
from sqlalchemy import select
from vkbottle.bot import Message, BotLabeler
from CONFIG import IdGroupVK
from keyboards import KeyboardRepository
from database_module.Tables import Peers,peerDB,DBexec
from hadlers_rules import PrefixPrevilegesRule
from online_tools import RandomMember, getUserName
from sessions import api_group, max_user_id
from tools import json_config, data_msg, DB_Manager

######################################################################################################
class privileges(object):
    def __init__(self, sender, peer, obj, kb=None, txt=None):
        if kb is None: kb = [None]
        self.txt = txt
        self.sender = sender
        self.peer = peer
        self.obj = obj
        self.send_msg = data_msg()
        self.kb = kb
        self.cnvmgid = self.obj.conversation_message_id
        self.EVIL_GODS = json_config().read_key(dir="sys",key='EVIL_GODS')
        self.EVIL_GODS = json_config().read_key(dir="sys",key='EVIL_GODS')
    ################## привелегия для удаления сообщений не админов(ультимативный мут) #################
    async def EVIL_GOD(self):
        E_G = await DBexec(peerDB,select(Peers).where(Peers.peer_id == self.peer)).dbselect("one")
        """SessionPeer = scoped_session(sessionmaker(bind=peerDB,class_=AsyncSession, expire_on_commit=False, autoflush=True))()
        async with SessionPeer as s:
            async with s.begin_nested():
                E_G = (await s.execute(select(Peers).where(Peers.peer_id == self.peer))).fetchone()
            await s.close()"""
        #print("eg ",E_G)
        # print(self.sender)
        try:
            if self.sender not in self.EVIL_GODS and 0 < self.sender < max_user_id:
                if E_G[1] == '1': await api_group.messages.delete(peer_id=self.peer, cmids=self.cnvmgid,
                                                                  group_id=IdGroupVK, delete_for_all=1)
                if E_G[3] == '1':
                    await api_group.messages.delete(peer_id=self.peer, conversation_message_ids=self.cnvmgid,
                                                    group_id=IdGroupVK, delete_for_all=1)
                    self.send_msg.msg = f"{await getUserName(self.sender)} *Впечатан в землю*"
                if E_G[4] == '1':
                    self.send_msg.msg = f"{await RandomMember(self.peer)} насилует {await RandomMember(self.peer)}"
        except:
            pass
            #logger(f"\n_____________________\n{traceback.format_exc()}\n_____________________\n\n\n", "ERROR.log")

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
                self.send_msg.msg = f'Доступно только админам бота\n______________________________\n'
                for z in list(privilege):
                    self.send_msg.msg += f"🔥 {z} 🔥\n\n"
                self.send_msg.keyboard = KeyboardRepository.PrivlegesKB()
######################################################################################################

labeler = BotLabeler()

@labeler.message(PrefixPrevilegesRule(),blocking=False)
async def command(msg: Message):
    logger.log("STATE","\n_________________________PRG_________________________")
    await privileges(txt=msg.text, sender=msg.from_id, peer=msg.peer_id, obj=msg).check()