import random,sqlite3,re
from  vk_api.keyboard import VkKeyboardColor
from tools import BD_COUNT,get_one_col_list
from online_tools import get_tag,getUserName,send_to_specific_peer,RandomMember,create_keyboard
from sessions import vk
from CONFIG import IdGroupVK

class WHO(object):
    def __init__(self, fromid,peer,obj = None,msg = None, kb = None):
        self.obj = obj
        self.msg = msg
        self.fromid = fromid
        self.peer = peer
        self.from_kb = kb
        self.sender = f"@id{self.fromid}({ getUserName(self.fromid)})"
        self.msgstring = ''
        self.comm = get_one_col_list('peers_roles.db', f"SELECT command FROM '{self.peer}'")
        ######################################
        if self.obj is not None:
            self.string_ = str(self.obj).lower().split(sep=' ')
            self.s_len_ = len(self.string_)
            self.string = str(self.obj).lower().split(maxsplit=1,sep=' ')
            self.s_len = len(self.string)
            self.word_comm = self.string[0].replace('!', '')
            if self.s_len_ > 1: self.find_tag = list(filter(re.compile(r"\[id\w+").match, self.string_))
            else:self.find_tag = None
        else:  self.string_ = self.string = self.s_len_ = self.s_len = self.word_comm = None
        ######################################
        if self.msg is not None:
            self.reply = self.msg.get('reply_message', False)
            self.conv_id = self.msg['conversation_message_id']
        else:
            self.conv_id = None
            self.reply = False
        ######################################
        try:
            try:
                self.tag = get_tag(self.find_tag[0])
                self.id = int(self.tag[2])
                self.name = f"@id{self.tag[0]}({getUserName(self.tag[0])})" if '@' in self.tag[1] \
                    else f"@id{self.tag[0]}({self.tag[1]})"
            ######################################
            except:
                if int(self.reply['from_id']) > 0:
                    self.tag = self.reply['from_id']
                    self.id = int(self.tag)
                    self.name = f"@id{self.tag}({getUserName(self.tag)})"
                else: self.tag = self.id = self.name = None
        except: self.tag = self.id = self.name = None
        ######################################
        self.kb_l = [self.fromid,self.id, self.conv_id]

    ############################################################### MARRY #######################################################
    def marry_control(self):
        #print(self.peer,self.fromid,self.from_kb)
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f'SELECT * FROM marry where peer_id = {self.peer} and man1 = {self.from_kb[0]} and man2 = {self.fromid}')
        params = edit.fetchone()
        info = False
        if params is not None:
            if self.peer == params[1] and self.fromid == self.from_kb[1] == params[3] and params[2] == self.from_kb[0]:
                if params[6]==0 and params[7]==1:
                    if self.from_kb[3] == 'ACCEPT':
                        q = f"UPDATE marry SET allow = {1} , await = {0} where peer_id = {self.peer} and " \
                            f"man1 = {self.from_kb[0]} and man2 = {self.fromid}"
                        message = f"@id{self.fromid}({getUserName(self.fromid)})  и  @id{self.from_kb[0]}" \
                                  f"({getUserName(self.from_kb[0])}) поженились! Поздравьте молодую пару!"
                    else:
                        q = f"DELETE FROM marry where peer_id = {self.peer} and " \
                            f"man1 = {self.from_kb[0]} and man2 = {self.fromid}"
                        message = f"@id{self.from_kb[0]}({getUserName(self.from_kb[0])}) ! \n" \
                                 f"@id{self.fromid}({getUserName(self.fromid)})отказался от вашего предложеня"
                    edit.execute(q)
                    vk.messages.edit(peer_id=self.peer, conversation_message_id=self.from_kb[2] + 1,
                                     group_id=IdGroupVK, message=message)
                    BD.commit()
                else: info = "Брак не зарегистрирован или уже оформлен"
            else: info = "Куда ты жмешь -_-"
        else: info = "Ты не подавал брак с кем-либо"
        if info: send_to_specific_peer(info,self.peer)
        # vk_Srv.notifications.sendMessage(user_ids=[self.fromid],user_id=self.fromid,message="тест",group_id=IdGroupVK)
        BD.close()

    ################################################################################################
    def marry_query(self):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        m = None
        if 'холост' in self.string_:
            m =[f"DELETE FROM marry where peer_id = {self.peer} and man1 = {self.fromid} or man2 = {self.fromid}",
            f"Теперь вы свободны от отношений!",None]
        elif self.id is not None:
            froms = len(get_one_col_list('peers.db', f"SELECT man1 FROM marry where peer_id = "
                                                     f"{self.peer} and man1 = {self.fromid}"))
            params = edit.execute(f"SELECT allow,await,id FROM marry where peer_id = "
                         f"{self.peer} and (man1 = {self.fromid} and man2 = {self.id})"
                         f"or (man1 = {self.id} and man2 = {self.fromid})").fetchone()
            marry_polygam = edit.execute(f"SELECT poligam_marry FROM peers where peer_id = {self.peer}").fetchone()[0]
            num = BD_COUNT(edit.execute(f"SELECT * from marry"), 0)
            key = create_keyboard(False,True,[
                ["Принять",VkKeyboardColor.POSITIVE,{"M_ACCEPT":self.kb_l}],
                ["Отклонить",VkKeyboardColor.NEGATIVE,{"M_DENY":self.kb_l}] ])
            if 'развод' in self.string_:
                m =[f"DELETE FROM marry where peer_id = {self.peer} and (man1 = {self.fromid} and man2 = {self.id})"
                    f" or (man1 = {self.id} and man2 = {self.fromid})",f"Вы отозвали брак с {self.name}!", None]
            ##############################
            else:
                #print(marry_polygam, params)
                if params is None:
                    if marry_polygam == 1 or (marry_polygam == 0 and froms <= 1):
                        m =[f'INSERT OR IGNORE INTO marry VALUES({max(num) + 1},{self.peer},{self.fromid},'
                            f'{self.id},"{getUserName(self.fromid)}","{getUserName(self.id)}",{0},{1})',
                        f"{self.name} ! Пользователь {self.sender} сделал вам предложение руки и сердца.",key]
                    else:   m =['',"Администратор запретил множественные браки в этом чате!", None]
                ##############################
                else:
                    if params[1] == 1: m = ['',f"Брак уже подан и находится в ожидании!\n{self.name} примите или отклоните",key]
                    if params[0] == 1: m = ['',f"Вы уже в браке с этим человеком!\n",None]
        if m is not None:
            edit.execute(m[0])
            send_to_specific_peer(m[1],self.peer,m[2])
        BD.commit()
        BD.close()

    ################################################################################################
    def marry_list(self):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"DELETE FROM marry where man1name = 'None' or man2name = 'None'")
        string = None
        if len(self.string_) >=2:
            strings = {
                "ожидание":["Ждут согласия 👫\n", "💝",f"SELECT man1name ,man2name from marry where allow = 0"],
                "я":["Ваши браки  👫\n", "💝",f"SELECT man1name ,man2name from marry "
                                        f"where (man1 = {self.fromid} or man2 = {self.fromid}) and allow = 1"]
            }
            if self.string_[1] in strings:
                string = strings.get(self.string_[1])
            elif self.string_[1] == "обновить":
                string = None
                ids = edit.execute(f"SELECT man1 ,man2 from marry").fetchall()
                users = []
                for i in ids:
                    for a in range(0,1):
                        if i[a] not in users: users.append(i[a])
                for z in users:
                    user = getUserName(z)
                    edit.executescript(
                        f'UPDATE marry SET man1name = "{user}" where man1 = {z};'
                        f'UPDATE marry SET man2name = "{user}" where man2 = {z}')
                    BD.commit()
                self.msgstring = "Имена обновлены"
        else: string =  [" Помолвлены 👩‍❤‍👨\n","💞",f"SELECT man1name ,man2name from marry where allow = 1"]
        if string is not None:
            self.msgstring +=f"{string[0]}"
            data = edit.execute(string[2]).fetchall()
            if not data:self.msgstring = "Ничего не найдено"
            else:
                for z in data: self.msgstring +=f"{string[1]} {z[0]} - {z[1]} {string[1]}\n"
        BD.close()

    def role(self):
        BD = sqlite3.connect('peers_roles.db')
        edit_role = BD.cursor()
        edit_role.execute(f"SELECT emoji_1, txt, emoji_2 FROM '{self.peer}' where command = '{self.word_comm}' ")
        key = edit_role.fetchall()[0]
        self.msgstring = f"{key[0]}   {self.sender}  {key[1]}  {self.name}  {key[2]}"
        BD.close()

    ######################################################################################################
    def WHO_GET(self):
        if self.string is not None:
            if self.s_len >= 2: s_obj = self.string[1] ;
            else: s_obj = self.name ;
        ######################################### Обработка #########################################
            items = {
                "!кто": f"❓ ➡    {RandomMember(self.peer)}    ⬅  :    {s_obj}",
                "!вероятность": f"📊 Вероятность для  (  {s_obj}  ) :   {str(random.randint(0, 100))} %",
                "!забив": f"📣🐖   Забив :\n\n 🇺🇦  {self.sender}  🇺🇦        🆚        ✡  {self.name}  ✡\n\n🏆   Победил:  \
                           {random.choice([self.sender, self.name])}     🏆",
                "!факт": f"❗ Факт (  {s_obj}  )   {random.choice(['Ложь ⛔', 'Правда ✅'])} ",
                    }
            if self.string[0] in items: self.msgstring = items.get(self.string[0])
        ##########################################################################################################
            items_upgrade = {
                "!брак": self.marry_query,
                "!браки": self.marry_list,
            }
            #print(self.string)
            if self.string[0] in items_upgrade:
                i = items_upgrade.get(self.string[0])
                if i is not None: i()
        ################################################# role #################################################
            if self.word_comm in self.comm: self.role()
        ###########################################################################################################
            if self.msgstring != '' and self.msgstring.find('None') == -1:send_to_specific_peer(self.msgstring,self.peer)
