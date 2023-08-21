import random, math, re, traceback, sqlite3
from online_tools import get_tag, get_list_album, GetMembers, kick, send_to_specific_peer
from tools import json_config, Debug, logger, FSM, data_msg
from managers import base_config, manager
from sessions import vk, vk_user, vk_full, global_catalog_command, upload, file_log, api_user
from CONFIG import IdGroupVK
from enums import States_cook


######################################################################################################
######################################################################################################
######################################################################################################
class Respondent_command(object):
    def __init__(self, TEXT, _FROM, PEER, OBJ):
        self.TEXT = TEXT
        self._FROM = _FROM
        self.PEER = PEER
        self.OBJ = OBJ
        self.line = str(self.TEXT).splitlines()
        self.sep = str(self.line[0]).split(sep=' ')
        self.sep_query = str(self.line[0]).split(sep=' ', maxsplit=2)
        self.len_sep = len(self.sep)
        self.len_sep_query = len(self.sep_query)
        self.reply = self.OBJ.reply_message
        self.OWNER_ALBUM_PHOTO = json_config().cfg_json()['OWNER_ALBUM_PHOTO']
        self.EVIL_GODS = json_config().cfg_json()['EVIL_GODS']
        self.Members = None

    ######################################################################################################

    # def send(self,msg):
    #    msg = TEXT_SPLIT(msg,4000)
    #    for z in msg: vk.messages.send(random_id=random.randint(0, 999999), message=z, peer_id=self.PEER)
    ######################################################################################################
    # def send_attachments(self,text,att):
    #    vk.messages.send(random_id=random.randint(0, 999999), message=text, peer_id=self.PEER,attachment=att)
    #######################################/settings менеджер ######################################
    async def manager_f(self):
        n = 5
        word_sep = str(self.line[0]).split(sep=' ', maxsplit=n - 1)
        # await self.OBJ.answer(f"До обработки { Debug(obj=self.line).obj_size()} {Debug(obj=word_sep).obj_size()} \n  {self.line}  {word_sep}")
        ################# наполнение ################
        for add in range(n):
            if len(self.line) < n: self.line.append('')
            if len(word_sep) < n: word_sep.append('')
        ######## зачистка от лишних пробелов ########
        for z in word_sep:
            z.replace(' ', '')
        for z in range(len(self.line)):
            self.line[z] = self.line[z].rstrip('\n ').lstrip()
        #await self.OBJ.answer(f"{word_sep}\n{self.line}")
        #############################################
        # await self.OBJ.answer(f"После обработки { Debug(obj=self.line).obj_size()} {Debug(obj=word_sep).obj_size()} \n  {self.line}  {word_sep}")
        mgr = manager(self.line, word_sep, self._FROM, self.PEER)
        bcfg = base_config(word_sep, self._FROM, self.PEER)
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
        if word_sep[1] in arg2: await arg2.get(word_sep[1])[1]()
        elif word_sep[1] == '-c':
            data_msg.msg = '⚙🔧bot-admin - доcтупно только разработчикам и администраторам бота \n ' \
                           '💻user - доступно для всех\n\n'
            for c in arg2: data_msg.msg += f"/settings {c} - {arg2.get(c)[0]}\n"

    #######################################/i - инфокоманды ######################################
    async def info_module(self):
        inf = {
            'idchat': [self.PEER, 'ID чата'],
            'id': [self._FROM, 'Ваш ID'],
        }

        if self.len_sep >= 2:
            if self.sep[1] in inf:
                key = inf.get(self.sep[1])
                data_msg.msg = f"{key[1]} - {key[0]}"
            elif self.sep[1] == '-c':
                mess = '/i:\n'
                for z in list(inf): mess += f"ℹ️ - {z} - {inf.get(z)[1]}\n"
                data_msg.msg = mess
            if self.OBJ.reply_message is not None:
                inf_reply = {
                    'idm': [self.OBJ.reply_message.conversation_message_id, 'ID сообщения'],
                    'id': [self.OBJ.reply_message.from_id, 'ID пользователя'],
                }
                if self.sep[1] in inf_reply and self.OBJ.reply_message:
                    key = inf_reply.get(self.sep[1])
                    data_msg.msg = f"{key[1]} - {key[0]}"



    ############################################################################
    async def debug(self):
        print(self.sep[2])
        # try:
        dbg = Debug(pid=self.sep[2])
        # except: dbg = Debug()
        print(dbg.__dict__)
        d = {
            'mem': dbg.process_mem_size(),
            'mem-map': dbg.process_mem_map(),
        }
        if self.len_sep >= 2:
            if self.sep[1] in d: data_msg.msg = f"{d.get(self.sep[1])}\n"
            elif self.sep[1] == '-c':
                data_msg.msg = '/d:\n'
                for z in list(d):  data_msg.msg += f"ℹ️ - {z}\n"

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
                    data_msg.msg = ''
                    data_msg.attachment = f"photo{str(self.OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}"
        except Exception as e:
            logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
            data_msg.msg = f'блядь я мем пробухал\n {e}'
            data_msg.attachment = 'photo388145277_456240127'

    #######################################/кик ######################################
    async def manager_kick(self):
        self.Members = (await GetMembers(self.PEER))
        if self._FROM in self.Members['admins'] or self._FROM in self.EVIL_GODS:
            try:
                if self.len_sep == 2:
                    t = (await get_tag(self.sep[1]))
                    if t['tag_id'] in self.sep[1]: await kick(chat_id=self.PEER - 2000000000, member_id=t['tag_id'])
                else:
                    if self.reply: await kick(chat_id=self.PEER - 2000000000, member_id=self.reply.from_id)
            except Exception as e:
                await logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n",
                       "ERROR.log")
                data_msg.msg = f"НЕЛЬЗЯ МУДИЛА \n{e}"
        else:
            data_msg.msg = "Ты не админ"

    #################################################################################################
    #######################################    cabal_module    ######################################
    #######################################/invite ######################################
    async def invite_user(self):
        try:
            if self.len_sep == 4 and self.sep[2] == re.findall("[0-9]{1,10}", self.sep[2])[0] and \
                    self.sep[3] == re.findall("[0-9]{1,10}", self.sep[3])[0]:
                await api_user.messages.add_chat_user(chat_id=self.sep[2], user_id=self.sep[3],
                                                      visible_messages_count=1000)
        except Exception as e:
            logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
            data_msg.msg = f"НЕЛЬЗЯ МУДИЛА \n{e}"

    #######################################очистка доков в группе ######################################
    async def clear_docs(self):
        d = vk_user.docs.get(owner_id='-' + str(IdGroupVK))
        docs = []
        for item in d['items']: docs.append(str(item['id']))
        for doc_ in docs: await api_user.docs.delete(owner_id='-' + str(IdGroupVK), doc_id=doc_)
        data_msg.msg = 'Удаление завершено'

    ####################################### E X T E R M I N A T U S ######################################
    async def KILL_ALL_MEMBERS(self):
        self.Members = (await GetMembers(self.PEER))
        for member in self.Members['members']: await kick(chat_id=self.PEER - 2000000000, member_id=member)

    async def catalog(self):
        data_msg.msg = global_catalog_command

    async def download_log(self):
        u = []
        att = []
        for f in file_log:
            try:
                u += [upload.document(doc=f, title=f, group_id=IdGroupVK, to_wall=0)]
            except:
                logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n",
                       "ERROR.log")
                pass
        for f in u: att.append(f"doc{str(f['doc']['owner_id'])}_{str(f['doc']['id'])}")
        vk.messages.send(random_id=0, peer_id=self.PEER, attachment=att)

    async def sql_cmd(self):
        if len(self.line) == 2 and self.len_sep == 3:
            try:
                BD = self.sep[2]
                query = self.line[1]
                base = sqlite3.connect(BD)
                cur = base.cursor()
                cur.execute(query)
                print(base.total_changes, base.in_transaction)
                if cur.__hash__() >= 1:
                    base.commit()
                    data_msg.msg = "Успешно"
                else:
                    data_msg.msg = "Изменений не  произошло"
            except Exception as e:
                data_msg.msg = f"Ошибка выполнения: {e}"

    async def cabal_module(self):
        if self.len_sep >= 2:
            if self._FROM in self.EVIL_GODS:
                cab_com = {
                    'kill_all_members=active': self.KILL_ALL_MEMBERS,
                    'clear_docs_init': self.clear_docs,
                    'invite': self.invite_user,
                    'catalog': self.catalog,
                    'log': self.download_log,
                    'sql': self.sql_cmd,
                }
                if self.sep[1] in cab_com:
                    key = cab_com.get(self.sep[1])
                    if key is not None: await key()
                elif self.sep[1] == '-c':
                    data_msg.msg = '/cabal:\n'
                    for z in list(cab_com):  data_msg.msg += f"ℹ️ - {z}\n"



######################################################################################################
######################################################################################################
######################################################################################################
class COMMAND(object):
    def __init__(self, TEXT, _FROM, PEER, OBJ):
        self.TEXT = TEXT
        self._FROM = _FROM
        self.PEER = PEER
        self.OBJ = OBJ
        self.CMD = str(self.TEXT).split(sep=' ')[0]

    ##################################################################################
    async def check(self):
        respond = Respondent_command(self.TEXT, self._FROM, self.PEER, self.OBJ)
        command = {
            '/кик': respond.manager_kick,
            '/мем': respond.get_album_photos_mem,
            '/cabal': respond.cabal_module,
            '/settings': respond.manager_f,
            '/i': respond.info_module,
            '/d': respond.debug,
        }
        if self.CMD in command:
            key = command.get(self.CMD)
            if key is not None: await key()

######################################################################################################
######################################################################################################
######################################################################################################
