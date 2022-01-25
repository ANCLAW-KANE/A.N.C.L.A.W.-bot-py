import random,math,re,traceback,sqlite3
from online_tools import get_tag,get_list_album,GetMembers,kick,send_to_specific_peer
from tools import json_gen,Debug,TEXT_SPLIT,logger
from managers import base_config,manager
from sessions import vk,vk_user,vk_full,global_catalog_command,upload,file_log
from CONFIG import IdGroupVK

######################################################################################################
######################################################################################################
######################################################################################################
class Respondent_command(object):
    def __init__(self ,TEXT,_FROM,PEER,OBJ):
        self.TEXT = TEXT
        self._FROM = _FROM
        self.PEER = PEER
        self.OBJ = OBJ
        self.line = self.TEXT.splitlines()
        self.sep = str(self.line[0]).split(sep=' ')
        self.len_sep = len(self.sep)
        self.reply = self.OBJ.get('reply_message', False)
        self.OWNER_ALBUM_PHOTO = json_gen().return_config_file_json()['OWNER_ALBUM_PHOTO']
        self.EVIL_GODS = json_gen().return_config_file_json()['EVIL_GODS']
        self.Members = GetMembers(self.PEER)

    ######################################################################################################
    def send(self,msg):
        msg = TEXT_SPLIT(msg,4000)
        for z in msg: vk.messages.send(random_id=random.randint(0, 999999), message=z, peer_id=self.PEER)
    ######################################################################################################
    def send_attachments(self,text,att):
        vk.messages.send(random_id=random.randint(0, 999999), message=text, peer_id=self.PEER,attachment=att)
    #######################################/settings менеджер ######################################
    def manager_f(self):
        n = 5
        lines = str(self.TEXT).splitlines()
        word_sep = str(lines[0]).split(sep=' ', maxsplit=n-1)
        #self.send(f"До обработки { Debug(obj=lines).obj_size()} {Debug(obj=word_sep).obj_size()} \n  {lines}  {word_sep}")
        ################# наполнение ################
        for add in range(n):
            if len(lines) < n: lines.append('')
            if len(word_sep) < n: word_sep.append('')
        ######## зачистка от лишних пробелов ########
        for z in word_sep:  z.replace(' ', '')
        for z in range(len(lines)):
            q = list(lines[z])
            if q != []:
                if q[0]==' ':
                    q.remove(q[0])
                    lines[z]="".join(q)
        #############################################
        #self.send(f"После обработки { Debug(obj=lines).obj_size()} {Debug(obj=word_sep).obj_size()} \n  {lines}  {word_sep}")
        mgr = manager(lines, word_sep, self._FROM, self.PEER)
        bcfg = base_config(word_sep, self._FROM, self.PEER)
        arg2 = {
            'word': ['💻user ', mgr.word],
            'role': ['💻user ', mgr.role],
            'quote': ['💻user ', mgr.quote],
            'count': ['💻user ', mgr.count],
            'chat': ['💻user ', mgr.show_settings],
            'marry': ['💻user ', mgr.marry_toggle],
            'toggle_red':['⚙🔧bot-admin ', mgr.global_resend_toggle],
            'node': ['⚙🔧bot-admin ', mgr.edit_node],
            'json-edit': ['⚙🔧bot-admin ', bcfg.edit],
            'json-show': ['⚙🔧bot-admin ', bcfg.show],
            'json-params': ['⚙🔧bot-admin ', bcfg.info_param],
            'json-pe': ['⚙🔧bot-admin ', bcfg.add_info],
        }
        if word_sep[1] in arg2:
            arg2.get(word_sep[1])[1]()
        elif word_sep[1] == '-c':
            s = '⚙🔧bot-admin - доcтупно только разработчикам и администраторам бота \n 💻user - доступно для всех\n\n'
            for c in arg2:
                s += f"/settings {c} - {arg2.get(c)[0]}\n"
            self.send(s)
    #######################################/i - инфокоманды ######################################
    def info_module(self):
        inf = {
            'idchat': [str(self.PEER),'ID чата'],
            'id': [str(self._FROM),'Ваш ID'],
        }
        if self.len_sep >= 2:
            if self.sep[1] in inf:
                key = inf.get(self.sep[1])
                self.send(f"{key[1]} - {key[0]}")
            elif self.sep[1] == '-c':
                mess = '/i:\n'
                for z in list(inf): mess += f"ℹ️ - {z} - {inf.get(z)[1]}\n"
                self.send(mess)

    ############################################################################
    def debug(self):
        print(self.sep[2])
        #try:
        dbg = Debug(pid=self.sep[2])
        #except: dbg = Debug()
        print(dbg.__dict__)
        d = {
            'mem': dbg.process_mem_size(),
            'mem-map' : dbg.process_mem_map(),
        }
        if self.len_sep >= 2:
            if self.sep[1] in d: self.send(f"{d.get(self.sep[1])}\n")
            elif self.sep[1] == '-c':
                mess = '/d:\n'
                for z in list(d):  mess += f"ℹ️ - {z}\n"
                self.send(f"{mess}\n")

    #######################################/мем ######################################
    def get_album_photos_mem(self):
        try:
            offset_max = 0
            parse_album = str(random.choice(get_list_album())).split(sep='_')
            if int(parse_album[1]) > 50: offset_max = math.floor(int(parse_album[1]) / 50)
            if parse_album[1] != '0':
                alb_ph = vk_user.photos.get(owner_id=self.OWNER_ALBUM_PHOTO,
                    album_id=parse_album[0], count=50,offset=random.randint(0, offset_max) * 50)
                photoList = []
                for photo in alb_ph['items']: photoList.append(str(photo['id']))
                if photoList is not None:
                    return self.send_attachments('',f"photo{str(self.OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}")
        except Exception as e:
            logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
            return self.send_attachments(f'блядь я мем пробухал\n {e}','photo388145277_456240127')

    #######################################/кик ######################################
    def manager_kick(self):
        if self._FROM in self.Members[2]:
            try:
                if self.len_sep == 2:
                    t = get_tag(self.sep[1])
                    if t[0] in self.sep[1]: kick(chat_id=self.PEER - 2000000000, member_id=t[0])
                else:
                    if self.reply: kick(chat_id=self.PEER - 2000000000, member_id=self.reply['from_id'])
            except Exception as e:
                logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n","ERROR.log")
                self.send(f"НЕЛЬЗЯ МУДИЛА \n{e}")
        else: self.send("Ты не админ")

    #################################################################################################
    #######################################    cabal_module    ######################################
        #######################################/invite ######################################
    def invite_user(self):
        try:
            if self.len_sep == 4 and self.sep[2] == re.findall("[0-9]{1,10}", self.sep[2])[0] and \
            self.sep[3] == re.findall("[0-9]{1,10}", self.sep[3])[0]:
                vk_full.messages.addChatUser(chat_id=self.sep[2], user_id=self.sep[3])
        except Exception as e:
            logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
            self.send(f"НЕЛЬЗЯ МУДИЛА \n{e}")

   #######################################очистка доков в группе ######################################
    def clear_docs(self):
        d = vk_user.docs.get(owner_id='-' + str(IdGroupVK))
        docs = []
        for item in d['items']: docs.append(str(item['id']))
        for doc_ in docs: vk_user.docs.delete(owner_id='-' + str(IdGroupVK), doc_id=doc_)
        self.send('Удаление завершено')

    ####################################### E X T E R M I N A T U S ######################################
    def KILL_ALL_MEMBERS(self):
        list_members = GetMembers(self.PEER)[1]
        for member in list_members:kick(chat_id=self.PEER - 2000000000, member_id=member)

    def catalog(self):
        self.send(global_catalog_command)

    def download_log(self):
        u = []
        att = []
        for f in file_log :
            try: u += [upload.document(doc=f,title=f,group_id=IdGroupVK,to_wall=0)]
            except:
                logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n","ERROR.log")
                pass
        for f in u: att.append(f"doc{str(f['doc']['owner_id'])}_{str(f['doc']['id'])}")
        vk.messages.send(random_id=0, peer_id=self.PEER, attachment=att)

    def sql_cmd(self):
        if len(self.line) == 2 and self.len_sep == 3:
            try:
                BD = self.sep[2]
                query = self.line[1]
                base = sqlite3.connect(BD)
                cur = base.cursor()
                cur.execute(query)
                print(base.total_changes,base.in_transaction)
                if cur.__hash__() >= 1:
                    base.commit()
                    send_to_specific_peer("Успешно",self.PEER)
                else: send_to_specific_peer("Изменений не  произошло",self.PEER)
            except Exception as e: send_to_specific_peer(f"Ошибка выполнения: {e}",self.PEER)

    def cabal_module(self):
        if self.len_sep >= 2:
            if self._FROM in self.EVIL_GODS:
                cab_com = {
                    'kill_all_members=active': self.KILL_ALL_MEMBERS,
                    'clear_docs_init':self.clear_docs,
                    'addUser': self.invite_user,
                    'catalog': self.catalog,
                    'log': self.download_log,
                    'sql': self.sql_cmd,
                }
                if self.sep[1] in cab_com:
                    key = cab_com.get(self.sep[1])
                    if key is not None: key()
                elif self.sep[1] == '-c':
                    mess = '/cabal:\n'
                    for z in list(cab_com):  mess += f"ℹ️ - {z}\n"
                    self.send(f"{mess}\n")
######################################################################################################
######################################################################################################
######################################################################################################
class COMMAND(object):
    def __init__(self,TEXT,_FROM,PEER,OBJ):
        self.TEXT = TEXT
        self._FROM = _FROM
        self.PEER = PEER
        self.OBJ = OBJ
        self.CMD = str(self.TEXT).split(sep=' ')[0]
    ##################################################################################
    def check(self):
        respond = Respondent_command(self.TEXT,self._FROM,self.PEER,self.OBJ)
        command = {
            '/кик': respond.manager_kick,
            '/мем': respond.get_album_photos_mem,
            '/cabal': respond.cabal_module,
            '/settings': respond.manager_f,
            '/i': respond.info_module,
            '/d':respond.debug,
        }
        if self.CMD in command:
            key = command.get(self.CMD)
            if key is not None: key()

######################################################################################################
######################################################################################################
######################################################################################################