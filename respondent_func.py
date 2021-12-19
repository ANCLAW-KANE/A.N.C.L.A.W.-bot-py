import sqlite3,random,math,re

from online_tools import RandomMember,getUserName,send_to_specific_peer,get_tag,get_list_album,GetMembers,kick,Invertor
from tools import json_gen
from managers import base_config,manager
from sessions import vk,vk_user,vk_full,global_catalog_command
from CONFIG import IdGroupVK

######################################################################################################
######################################################################################################
######################################################################################################
class privileges(object):
    def __init__(self, txt, sender, peer, obj):
        self.txt = txt
        self.sender = sender
        self.peer = peer
        self.obj = obj
        self.cnvmgid = self.obj['conversation_message_id']
        self.EVIL_GODS = json_gen().return_config_file_json()['EVIL_GODS']
    ################## привелегия для удаления сообщений не админов(ультимативный мут) #################
    def EVIL_GOD(self):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.peer}")
        E_G = edit.fetchone()
        try:
            if self.sender not in self.EVIL_GODS :
                if E_G[1] == '1': vk.messages.delete(peer_id=self.peer,conversation_message_ids=self.cnvmgid,
                                   group_id=IdGroupVK,delete_for_all=1)
                if E_G[3] == '1':
                    vk.messages.delete(peer_id=self.peer, conversation_message_ids=self.cnvmgid,
                                       group_id=IdGroupVK, delete_for_all=1)
                    send_to_specific_peer(f"{getUserName(self.sender)} *Впечатан в землю*", self.peer)
                if E_G[4] == '1':
                    send_to_specific_peer(f"{RandomMember(self.peer)} насилует {RandomMember(self.peer)}", self.peer)
            BD.close()
        except:
            BD.close()

    ######################################################################################################
    def check(self):
        privilege = {
            '*присутствие злого бога*': Invertor(self.sender,self.EVIL_GODS,f"SELECT * FROM peers WHERE peer_id = {self.peer}",
                'Безмолвие','*Уходит*',self.peer,"UPDATE peers SET e_g_mute = ? where peer_id = ?",1,str,self.peer).key,
            '*ваши головы подняты слишком высоко*':Invertor(self.sender,self.EVIL_GODS,f"SELECT * FROM peers WHERE peer_id = {self.peer}",
                '*Раздавлены*','*Уходит*',self.peer,"UPDATE peers SET e_g_head = ? where peer_id = ?",3,str,self.peer).key,
            '*адская похоть*': Invertor(self.sender,self.EVIL_GODS,f"SELECT * FROM peers WHERE peer_id = {self.peer}",
                'Исполнено','*Уходит*',self.peer,"UPDATE peers SET e_g_ex = ? where peer_id = ?",4,str,self.peer).key,
        }
        if self.txt in privilege:
            key = privilege.get(self.txt)
            if key is not None: key()
        elif self.txt == '* EVIL GOD *':
            mess = f'Доступно только админам бота\n______________________________\n'
            for z in list(privilege):
                mess += f"🔥 {z} 🔥\n\n"
            send_to_specific_peer(f"{mess}", self.peer)

######################################################################################################
######################################################################################################
######################################################################################################
class WHO(object):
    def __init__(self,obj,sender,peer):
        self.obj = obj
        self.sender = f"@id{sender}({getUserName(sender)})"
        self.peer = peer
        self.srs = ''
        self.s = str(self.obj).lower().split(maxsplit=1)
        self.s_len = len(self.s)
        try:
            self.tag = get_tag(self.s[1])
            self.name = f"@id{self.tag[0]}({getUserName(self.tag[0])})" \
                if '@' in self.tag[1] \
                else f"@id{self.tag[0]}({self.tag[1]})"
        except :
            self.tag = None
            self.name = None
    ######################################################################################################
    def WHO_GET(self):
        if self.s_len == 2 and self.obj[0] != '/':
            ###################################### Сбор команд role #############################################
            comm = []
            BDROLES = sqlite3.connect('peers_roles.db')
            edit_roles = BDROLES.cursor()
            edit_roles.execute(f"SELECT command FROM '{self.peer}'")
            for command in edit_roles.fetchall():
                comm.append(f"!{command[0]}")
            ######################################### Обработка #########################################
            items = {
                "!кто": f"❓ ➡➡➡    {RandomMember(self.peer)}    ⬅⬅⬅  :    {self.s[1]}",
                "!вероятность": f"📊 Вероятность для  (  {self.s[1]}  ) :   {str(random.randint(0, 100))} %",
                "!забив": f"📣🐖   Забив : \n\n 🇺🇦  {self.sender}  🇺🇦        🆚        ✡  {self.name}  ✡\n\n🏆   Победил:  \
                           {random.choice([self.sender, self.name])}     🏆",
                "!факт": f"❗ Факт (  {self.s[1]}  )   {random.choice(['Ложь ⛔', 'Правда ✅'])} ",
            }
            if self.s[0] in items: self.srs = items.get(self.s[0])
            #### role ####
            elif self.s[0] in comm and self.tag[0]:
                edit_roles.execute(f"SELECT emoji_1, txt, emoji_2 FROM '{self.peer}' "
                                   f"where command = " f"'{self.s[0].replace('!', '')}'")
                key = edit_roles.fetchall()[0]
                self.srs = f"{key[0]}   {self.sender}  {key[1]}  {self.name}  {key[2]}"
            if self.srs != '' and self.srs.find('None') == -1:
                send_to_specific_peer(self.srs,self.peer)

######################################################################################################
######################################################################################################
######################################################################################################
class Respondent_command(object):
    def __init__(self ,TEXT,_FROM,PEER,OBJ):
        self.TEXT = TEXT
        self._FROM = _FROM
        self.PEER = PEER
        self.OBJ = OBJ
        self.sep = str(self.TEXT).split(sep=' ')
        self.len_sep = len(self.sep)
        self.reply = self.OBJ.get('reply_message', False)
        self.OWNER_ALBUM_PHOTO = json_gen().return_config_file_json()['OWNER_ALBUM_PHOTO']
        self.EVIL_GODS = json_gen().return_config_file_json()['EVIL_GODS']
    ######################################################################################################
    def send(self,msg):
        vk.messages.send(random_id=random.randint(0, 999999), message=msg, peer_id=self.PEER)
    ######################################################################################################
    def send_attachments(self,text,att):
        vk.messages.send(random_id=random.randint(0, 999999), message=text, peer_id=self.PEER,attachment=att)
    #######################################/settings менеджер ######################################
    def manager_f(self):
        lines = str(self.TEXT).splitlines()
        word_sep = str(lines[0]).split(sep=' ', maxsplit=4)
        # наполнение
        for add in range(5):
            if len(lines) < 5: lines.append('')
            if len(word_sep) < 5: word_sep.append('')
        mgr = manager(lines, word_sep, self._FROM, self.PEER)
        bcfg = base_config(word_sep, self._FROM, self.PEER)
        arg2 = {
            'word': ['💻user ', mgr.word],
            'role': ['💻user ', mgr.role],
            'quote': ['💻user ', mgr.quote],
            'count': ['💻user ', mgr.count],
            'chat': ['💻user ', mgr.show_settings],
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
        if self.len_sep == 2:
            if self.sep[1] in inf:
                key = inf.get(self.sep[1])
                self.send(f"{key[1]} - {key[0]}")
            elif self.sep[1] == '-c':
                mess = '/i:\n'
                key = list(inf)
                for z in key:
                    mess += f"ℹ️ - {z} - {inf.get(z)[1]}\n"
                self.send(mess)
            elif self.sep[1] == 'cabal-catalog':
                self.send(global_catalog_command)
    #######################################/мем ######################################
    def get_album_photos_mem(self):
        try:
            offset_max = 0
            parse_album = str(random.choice(get_list_album())).split(sep='_')
            if int(parse_album[1]) > 50: offset_max = math.floor(int(parse_album[1]) / 50)
            if parse_album[1] != '0':
                alb_ph = vk_user.photos.get(owner_id=self.OWNER_ALBUM_PHOTO, album_id=parse_album[0], count=50,
                                            offset=random.randint(0, offset_max) * 50)
                photoList = []
                for photo in alb_ph['items']:
                    photoList.append(str(photo['id']))
                if photoList is not None:
                    return self.send_attachments('',f"photo{str(self.OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}")
        except Exception as e:
            return self.send_attachments(f'блядь я мем пробухал\n {e}','photo388145277_456240127')
    ####################################### E X T E R M I N A T U S ######################################
    def KILL_ALL_MEMBERS(self):
        list_members = GetMembers(self.PEER)[1]
        for member in list_members:
            kick(chat_id=self.PEER - 2000000000, member_id=member)
    #######################################/кик ######################################
    def manager_kick(self):
        two_word_sep = str(self.TEXT).split(sep=' ', maxsplit=1)
        try:
            if len(two_word_sep) == 2:
                t = get_tag(two_word_sep[1])
                if t[0] in two_word_sep[1]: kick(chat_id=self.PEER - 2000000000, member_id=t[0])
            else:
                if self.reply: kick(chat_id=self.PEER - 2000000000, member_id=self.reply['from_id'])
        except Exception as e:
             self.send(f"НЕЛЬЗЯ МУДИЛА \n{e}")
    #######################################/invite ######################################
    def invite_user(self):
        three_word_sep = str(self.TEXT).split(sep=' ', maxsplit=2)
        try:
            if len(three_word_sep) == 3 and three_word_sep[0] == '/addUser' and \
               three_word_sep[1] == re.findall("[0-9]{1,10}", three_word_sep[1])[0] and \
               three_word_sep[2] == re.findall("[0-9]{1,10}", three_word_sep[2])[0]:
                vk_full.messages.addChatUser(chat_id=three_word_sep[1], user_id=three_word_sep[2])
        except Exception as e:
            self.send(f"НЕЛЬЗЯ МУДИЛА \n{e}")
    #######################################очистка доков в группе ######################################
    def clear_docs(self):
        d = vk_user.docs.get(owner_id='-'+ str(IdGroupVK))
        docs = []
        for item in d['items']:
            doc = str(item['id'])
            docs.append(doc)
        for doc_ in docs:
            vk_user.docs.delete(owner_id='-'+ str(IdGroupVK),doc_id=doc_)
        self.send('Удаление завершено')

    #################################### переключатель для resend ####################################
    def global_resend_toggle(self):
        if self.len_sep == 2 :
            if re.findall("[0-9]{1,10}", self.sep[1])[0]:
                Invertor(self._FROM,self.EVIL_GODS, f"SELECT * FROM peers  where peer_id = {self.sep[1]}", 'Разрешено',
                    'Запрещено', self.PEER,f"UPDATE peers SET resend = ? where peer_id = ?", 5, int, self.sep[1]).key()
        elif self.len_sep == 1 :
            Invertor(self._FROM, self.EVIL_GODS, f"SELECT * FROM peers where peer_id = {self.PEER}", 'Разрешено',
                'Запрещено', self.PEER, f"UPDATE peers SET resend = ? where peer_id = ?", 5, int, self.PEER).key()

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
            '/cabal:kill_all_members=active': respond.KILL_ALL_MEMBERS,
            '/addUser': respond.invite_user,
            '/settings': respond.manager_f,
            '/i': respond.info_module,
            '/clear_docs_init': respond.clear_docs,
            '/toggle_red': respond.global_resend_toggle,
        }
        if self.CMD in command:
            key = command.get(self.CMD)
            if key is not None: key()
######################################################################################################
######################################################################################################
######################################################################################################