from loguru import logger
from vkbottle.bot import Message, BotLabeler
from CONFIG import IdGroupVK
from vk_modules.hadlers_rules import PrefixPrevilegesRule
from vk_modules.kb_handlers.func_handler_keyboard import KeyboardRepository
from vk_modules.online_tools import RandomMember
from sessions_vk import api_group
from enums import max_user_id
from tools import json_config, data_msg
from database_module.cabal_repo import CabalRepository
from builders import ExtendParams, String_parse, NameBuilder

######################################################################################################
class privileges(ExtendParams, String_parse, NameBuilder):
    def __init__(self, fromid, peer, obj, txt=None):
        self.txt = txt
        self.fromid = fromid
        self.peer = peer
        self.obj = obj
        ExtendParams.__init__(self)
        self.params()
        String_parse.__init__(self, txt, obj)
        self.parse('$')
        NameBuilder.__init__(self, fromid, peer)
        self.cRepo = CabalRepository(self.peer, self.fromid)
        self.send_msg = data_msg()
        self.EVIL_GODS = json_config().read_key(dir="sys",key='EVIL_GODS')

    ################## привелегия для удаления сообщений не админов(ультимативный мут) #################
    async def EVIL_GOD(self):
        await self.construct()
        E_G = await self.cRepo.priveleges_get()
        try:
            if self.fromid not in self.EVIL_GODS and 0 < self.fromid < max_user_id:
                if E_G['e_g_mute'] == 1: await api_group.messages.delete(peer_id=self.peer, cmids=self.conv_id,
                                                                  group_id=IdGroupVK, delete_for_all=1)
                if E_G['e_g_head'] == 1:
                    await api_group.messages.delete(peer_id=self.peer, conversation_message_ids=self.conv_id,
                                                    group_id=IdGroupVK, delete_for_all=1)
                    self.send_msg.msg = f"{self.sender} *Впечатан в землю*"
                if E_G['e_g_ex'] == 1:
                    self.send_msg.msg = f"{await RandomMember(self.peer)} насилует {await RandomMember(self.peer)}"
            await self.send_msg.send(self.obj)
        except:
            pass

    ######################################################################################################
    async def check(self):
        if self.fromid in self.EVIL_GODS:
            if self.word_comm == 'evilgod':
                self.send_msg.msg = f'Доступно только админам бота\n______________________________\n'
                self.send_msg.keyboard = KeyboardRepository.PrivlegesKB()
        await self.send_msg.send(self.obj)
######################################################################################################

labeler = BotLabeler()

@labeler.message(PrefixPrevilegesRule(),blocking=False)
async def command(msg: Message):
    logger.log("STATE","\n_________________________PRG_________________________")
    await privileges(txt=msg.text, fromid=msg.from_id, peer=msg.peer_id, obj=msg).check()