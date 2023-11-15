
from loguru import logger
from vk_modules.hadlers_rules import PrefixCommandRule
from tools import data_msg, check_dict_key,unpack_keys
from builders import ExtendParams, NameBuilder , String_parse
from enums import Commands
from vk_modules.func_modules.managers import manager
from vk_modules.func_modules.administration_module import Administration
from vk_modules.func_modules.cabal_module import Cabal
from vk_modules.func_modules.funny_module import Funny
from vk_modules.func_modules.info_module import Info
from vk_modules.func_modules.generators import Generate
from vkbottle.bot import Message , BotLabeler

######################################################################################################
class Respondent_command(ExtendParams,String_parse,NameBuilder,Administration,Funny,Info,Cabal,Generate,manager):
    def __init__(self, txt, fromid, peer, obj,):
        self.fromid = fromid
        self.peer = peer
        self.obj = obj
        self.send_msg = data_msg()
        ExtendParams.__init__(self)
        String_parse.__init__(self,txt,obj)
        NameBuilder.__init__(self,fromid,peer)
        self.parse('/')
        Administration.__init__(self)
        Funny.__init__(self)
        Info.__init__(self)
        Cabal.__init__(self)
        Generate.__init__(self)
        manager.__init__(self)
    ######################################################################################################
    # def send(self,msg):
    #    msg = TEXT_SPLIT(msg,4000)
    #    for z in msg: vk.messages.send(random_id=random.randint(0, 999999), message=z, peer_id=self.peer)
    #######################################/settings менеджер ######################################
    async def manager_f(self):
        arg2 = {
                Commands.settings_wrq.value: self.builder_data,
                Commands.settings_count.value: self.count,
                Commands.settings_chat.value: self.show_settings,
                Commands.settings_marry.value: self.marry_toggle,
                Commands.settings_words.value: self.toggle_word,
            }
        if self.args_len and self.args_len >= 1:
            key = check_dict_key(arg2, self.list_args[0])
            if key: await key()
        else:
            msg = '/settings:\n'
            msg += unpack_keys(arg2,'🔧')
            self.send_msg.msg = msg

    #################################################################################################


    async def check(self):
        await self.construct()
        command = {
            Commands.ban.value: self.manager_kick,
            Commands.mem.value: self.get_album_photos_mem,
            Commands.cabal.value: self.cabal_module,
            Commands.settings.value: self.manager_f,
            Commands.info.value: self.info_module,
            Commands.mute.value: self.manager_mute,
            Commands.gen.value: self.check_g
        }
        key = check_dict_key(command, self.word_comm)
        if key:
            await key()
            await self.send_msg.send(self.obj)

######################################################################################################


labeler = BotLabeler()

@labeler.message(PrefixCommandRule(),blocking=False)
async def command(msg: Message):
    logger.log("STATE","\n_________________________CMD_________________________")
    await Respondent_command(msg.text, msg.from_id, msg.peer_id, msg).check()
