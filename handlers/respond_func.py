
import random, math
from loguru import logger
from vkbottle import DocMessagesUploader
from hadlers_rules import PrefixCommandRule
from online_tools import get_list_album, GetMembers,kick
from tools import json_config,  data_msg,Patterns,Writer
from managers import base_config, manager
from sessions import global_catalog_command, api_group, vb ,api_user
from CONFIG import IdGroupVK
from vkbottle.bot import Message , BotLabeler
from vkbottle.exception_factory import VKAPIError
from builders import ExtendParams, NameBuilder , String_parse

######################################################################################################
######################################################################################################
######################################################################################################
class Respondent_command(ExtendParams,String_parse,NameBuilder):
    def __init__(self, txt, fromid, peer, obj,):
        self.fromid = fromid
        self.peer = peer
        self.obj = obj
        ExtendParams.__init__(self)
        String_parse.__init__(self,txt,obj)
        NameBuilder.__init__(self,fromid,peer)
        self.params()
        self.parse('/')
        #self.line = str(self.TEXT).splitlines()
        #self.sep = str(self.line[0]).split(sep=' ')
        #self.sep_query = str(self.line[0]).split(sep=' ', maxsplit=2)
        #self.len_sep = len(self.sep)
        #self.len_sep_query = len(self.sep_query)
        #self.reply = fself.obj.reply_message
        self.OWNER_ALBUM_PHOTO = json_config().read_key('sys','OWNER_ALBUM_PHOTO')
        self.EVIL_GODS = json_config().read_key('sys','EVIL_GODS')
        self.Members = None
        self.send_msg = data_msg()

    ######################################################################################################

    # def send(self,msg):
    #    msg = TEXT_SPLIT(msg,4000)
    #    for z in msg: vk.messages.send(random_id=random.randint(0, 999999), message=z, peer_id=self.peer)
    ######################################################################################################
    # def send_attachments(self,text,att):
    #    vk.messages.send(random_id=random.randint(0, 999999), message=text, peer_id=self.peer,attachment=att)
    #######################################/settings менеджер ######################################
    async def manager_f(self):
        #n = 5
        #word_sep = str(self.line[0]).split(sep=' ', maxsplit=n - 1)
        # await fself.obj.answer(f"До обработки { Debug(obj=self.line).obj_size()} {Debug(obj=word_sep).obj_size()} \n  {self.line}  {word_sep}")
        ################# наполнение ################
        #for add in range(n):
        #    if len(self.line) < n: self.line.append('')
        #    if len(word_sep) < n: word_sep.append('')
        ######## зачистка от лишних пробелов ########
        #for z in word_sep:
        #    z.replace(' ', '')
        #for z in range(len(self.line)):
        #    self.line[z] = self.line[z].rstrip('\n ').lstrip()
        #await fself.obj.answer(f"{word_sep}\n{self.line}")
        #############################################
        # await fself.obj.answer(f"После обработки { Debug(obj=self.line).obj_size()} {Debug(obj=word_sep).obj_size()} \n  {self.line}  {word_sep}")
        mgr = manager(self.string_all, self.fromid, self.peer)
        bcfg = base_config(self.string_all, self.fromid, self.peer)
        arg2 = {
            'word': ['💻user ', mgr.word],
            'role': ['💻user ', mgr.role],
            'quote': ['💻user ', mgr.quote],
            'count': ['💻user ', mgr.count],
            'chat': ['💻user ', mgr.show_settings],
            'marry': ['💻user ', mgr.marry_toggle],
            'toggle_red': ['⚙🔧bot-admin ', mgr.global_resend_toggle],
            'node': ['⚙🔧bot-admin ', mgr.edit_node],
            'json-edit': ['⚙🔧bot-admin ', bcfg.edit],
            'json-show': ['⚙🔧bot-admin ', bcfg.show],
            'json-params': ['⚙🔧bot-admin ', bcfg.info_param],
            'json-pe': ['⚙🔧bot-admin ', bcfg.add_info],
        }
        if self.string_all[1] in arg2: await arg2.get(self.string_all[1])[1]()
        elif self.string_all[1] == '-c':
            self.send_msg.msg = '⚙🔧bot-admin - доcтупно только разработчикам и администраторам бота \n ' \
                           '💻user - доступно для всех\n\n'
            for c in arg2: self.send_msg.msg += f"/settings {c} - {arg2.get(c)[0]}\n"

    #######################################/i - инфокоманды ######################################
    async def info_module(self):
        inf = {
            'idchat': [self.peer, 'ID чата'],
            'id': [self.fromid, 'Ваш ID'],
        }

        if self.args_len is not None and self.args_len >= 1:
            if self.list_args[0] in inf:
                key = inf.get(self.list_args[1])
                self.send_msg.msg = f"{key[1]} - {key[0]}"
            elif self.list_args[0] == '-c':
                mess = '/i:\n'
                for z in list(inf): mess += f"ℹ️ - {z} - {inf.get(z)[1]}\n"
                self.send_msg.msg = mess
            if self.reply:
                inf_reply = {
                    'idm': [self.reply.conversation_message_id, 'ID сообщения'],
                    'id': [self.reply.from_id, 'ID пользователя'],
                }
                if self.list_args[1] in inf_reply:
                    key = inf_reply.get(self.list_args[0])
                    self.send_msg.msg = f"{key[1]} - {key[0]}"


    #######################################/мем ######################################
    async def get_album_photos_mem(self):
        try:
            offset_max = 0
            photoList = []
            list_a = await get_list_album()
            parse_album = str(random.choice(list_a)).split(sep='_')
            if int(parse_album[1]) > 50: offset_max = math.floor(int(parse_album[1]) / 50)
            if parse_album[1] != '0':
                alb_ph = await api_user.photos.get(owner_id=self.OWNER_ALBUM_PHOTO,
                                                   album_id=parse_album[0], count=50,
                                                   offset=random.randint(0, offset_max) * 50)
                for photo in alb_ph.items:  photoList.append(str(photo.id))
                if photoList is not None or not []:
                    self.send_msg.attachment = f"photo{str(self.OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}"
        except:
            self.send_msg.msg = f'Мем спизжен китайцами , повторите позже...'
            self.send_msg.attachment = 'photo388145277_456240127'

    #######################################/кик ######################################
    async def manager_kick(self):
        self.Members = (await GetMembers(self.peer))
        if self.fromid in self.Members['admins'] or self.fromid in self.EVIL_GODS:
            try:
                if self.args_len is not None and self.args_len >= 1:
                    ids = Patterns.get_mentions(self.string_args)
                    if ids['users'] != [] or ids["invert_ids_clubs"] != []:
                        for i in ids['users'] + ids["invert_ids_clubs"]:
                            await kick(chat=self.obj.chat_id, user=i['id'],member=i['id'])
                elif self.reply:  await  kick(chat=self.obj.chat_id, user=self.reply.from_id,member=self.reply.from_id)    
            except VKAPIError as e: self.send_msg.msg = f"НЕЛЬЗЯ МУДИЛА \n{e}"
        else: self.send_msg.msg = "Ты не админ"

    #################################################################################################
    #######################################    cabal_module    ######################################
    ####################################### E X T E R M I N A T U S ######################################
    async def KILL_ALL_MEMBERS(self):
        self.Members = (await GetMembers(self.peer))
        for i in self.Members['members']: 
            await api_group.messages.remove_chat_user(chat_id=self.obj.chat_id, user_id=i, member_id=i)

    async def catalog(self):
        self.send_msg.msg = global_catalog_command

    async def download_log(self):
        #path = f'./temps/logs-{self.peer}.zip'
        path = await Writer.create_bytes_archive(Writer.create_list_zip('./logs'))
        #await Writer.create_file_archive(path,Writer.create_list_zip('./logs'))
        doc = DocMessagesUploader(vb.api)
        self.send_msg.attachment = await doc.upload(f'logs-{self.peer}.zip',path , peer_id = self.peer)

    async def cabal_module(self):
        if self.args_len is not None and self.args_len >= 1 and self.fromid in self.EVIL_GODS:
            cab_com = {
                    'kill_all_members=active': self.KILL_ALL_MEMBERS,
                    'catalog': self.catalog,
                    'log': self.download_log,
                }
            if self.list_args[0] in cab_com:
                key = cab_com.get(self.list_args[0])
                if key is not None: await key()
            elif self.list_args[0] == '-c':
                self.send_msg.msg = '/cabal:\n'
                for z in list(cab_com): self.send_msg.msg += f"ℹ️ - {z}\n"

    async def check(self):
        await self.construct()
        command = {
            'кик': self.manager_kick,
            'мем': self.get_album_photos_mem,
            'cabal': self.cabal_module,
            'settings': self.manager_f,
            'i': self.info_module,
        }
        if self.word_comm in command:
            key = command.get(self.word_comm, None)
            if key:
                await key()
                await self.send_msg.send(self.obj)

######################################################################################################
######################################################################################################
######################################################################################################

labeler = BotLabeler()

@labeler.message(PrefixCommandRule(),blocking=False)
async def command(msg: Message):
    logger.log("STATE","\n_________________________CMD_________________________")
    await Respondent_command(msg.text, msg.from_id, msg.peer_id, msg).check()
