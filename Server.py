import vk_api , random, telebot,logging,os, magic, re, math , time , requests,sqlite3
from PIL import Image
import mimetypes as mtps
from requests import get
from vk_api import VkApi , audio
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from CONFIG import a, idGroupTelegram , IdGroupVK , teletoken , vktokenGroup  ,\
    vktokenUser, types ,CAPTCHA_EVENT,OWNER_ALBUM_PHOTO,\
    PEER_CRUSH_EVENT,full_permission_user_token,who_module,EVIL_GODS

################### Логирование ###########################
file_log = logging.FileHandler('Log.log', 'a', 'utf-8')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)
################ Служебные переменные #####################
i = 0
tag = ''
size_values = list("smxopqryzw")
tab = {
    'chat_kick_user': '⚠⚠⚠ УДАЛЕН',
    'chat_invite_user': '⚠⚠⚠ ДОБАВЛЕН',
    'chat_invite_user_by_link': '⚠⚠⚠ ПРИГЛАШЕН ПО ССЫЛКЕ',
}

################### Авторизация ###########################
bot = telebot.TeleBot(teletoken)

vk_session: VkApi = vk_api.VkApi(token=vktokenGroup)#Группа
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, IdGroupVK)

def captcha_handler(captcha):#обход капчи
    print(f"Enter captcha code: {captcha.get_url()}")
    vk.messages.send(random_id=random.randint(0, 999999), message=f"Enter captcha code: {captcha.get_url()}",peer_id=CAPTCHA_EVENT)
    for captcha_trigger in longpoll.listen():
        return captcha.try_again( captcha_trigger.object.text)

vk_session_user : VkApi = vk_api.VkApi(token=vktokenUser,captcha_handler=captcha_handler)#Пользователь
vk_user = vk_session_user.get_api()

vk_session_full : VkApi = vk_api.VkApi(token=full_permission_user_token,captcha_handler=captcha_handler)#VKME
vk_full = vk_session_full.get_api()

longpoll_full = VkBotLongPoll(vk_session_full, IdGroupVK)
upload = vk_api.VkUpload(vk_full)
api_audio = vk_api.audio.VkAudio(vk_session_full)

################################## Блок функций #######################################
def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, user_id=member_id,member_id=member_id)

def send(msg):
    vk.messages.send(random_id=random.randint(0, 999999), message=msg, peer_id=respondent.object.peer_id)

def send_attachments(att,text):
    vk.messages.send(random_id=random.randint(0, 999999), message=text, peer_id=respondent.object.peer_id,attachment=att)

def getUserName(object): #извлечение имени и фамилии
        userId = int(object)
        if 0 < userId < 2000000000:
           username = vk.users.get(user_id=userId)
           first_name = username[0]['first_name']
           last_name = username[0]['last_name']
           user = str(first_name + " " + last_name)
           return user

def GetMembers():
    members = vk.messages.getConversationMembers(peer_id=respondent.object.peer_id,group_id=IdGroupVK)
    membList = []
    membListNotAdmin = []
    membListAdmin = []
    for mbs in members['items']:
        member = mbs['member_id']
        admin = mbs.get('is_admin', False)
        if member > 0:
            membList.append(member)
        if member > 0 and admin != True:
            membListNotAdmin.append(member)
        if member > 0 and admin == True:
            membListAdmin.append(member)
    return [membList,membListNotAdmin,membListAdmin]

def RandomMember():
    userID = random.choice((GetMembers()[0]))
    username = vk.users.get(user_id=userID)
    first_name = username[0]['first_name']
    last_name = username[0]['last_name']
    user = str(first_name + " " + last_name)
    randMember = '@id' + str(userID)
    name_in_id = str(randMember + '(' + user + ')')
    return name_in_id

def SendTG(adress,TB):
    bot.send_message(adress, TB)
    logging.info(TB)

def GET_CHAT_TITLE(object):
    get_items_chat = vk.messages.getConversationsById(peer_ids=object)
    for chats in get_items_chat['items']:
        chat_title = chats['chat_settings']['title']
        return chat_title

#def reverse_Nodes():
#    reverseNodes = []
#    for idchat in Nodes.keys():
#        reverseNodes.append((Nodes[idchat], idchat))
#        getreversenode = dict(reverseNodes)
#    return getreversenode

def write_file(name,getfile):
    with open(name, 'bw') as f:
        f.write(getfile)

def clear_docs():
    d = vk_user.docs.get(owner_id='-'+ str(IdGroupVK))
    docs = []
    for item in d['items']:
        doc = str(item['id'])
        docs.append(doc)
    for doc_ in docs:
        vk_user.docs.delete(owner_id='-'+ str(IdGroupVK),doc_id=doc_)
    return 'Удаление завершено'

def get_list_album():
    albums = vk_user.photos.getAlbums(owner_id=OWNER_ALBUM_PHOTO)
    listAlbum = []
    for item in albums['items']:
        album = str(item['id'])
        size = str(item['size'])
        privacy = str(item['privacy_view'])
        if re.compile("'all'").search(privacy):
            listAlbum.append(album+'_'+size)
    return listAlbum

def get_album_photos_mem():
        try:
            offset_max = 0
            parse_album = str(random.choice(get_list_album())).split(sep='_')
            if int(parse_album[1]) > 50: offset_max = math.floor(int(parse_album[1]) / 50)
            if parse_album[1] != '0':
                alb_ph = vk_user.photos.get(owner_id=OWNER_ALBUM_PHOTO, album_id=parse_album[0], count=50 , offset=random.randint(0,offset_max) * 50)
                photoList = []
                for photo in alb_ph['items']:
                    idphoto = str(photo['id'])
                    photoList.append(idphoto)
                if photoList is not None: return send_attachments(f"photo{str(OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}",'')
        except Exception as e : return send_attachments('photo388145277_456240127',f'блядь я мем пробухал\n {e}')

def WHO(object,get_sender):
        s = str(object).lower().split(maxsplit=1)
        if len(s) == 2:
            tag = re.compile('@(\w+)').search(s[1])
            ss = s[0] + ' ' + s[1]
            if s[0] == "!кто" and s[1] is not None:
                srs = "❓ ➡➡➡  " + RandomMember() + '  ⬅⬅⬅  :  ' + s[1]
            elif s[0] == "!вероятность" and s[1] is not None:
                srs = "📊 Вероятность для  (" + s[1] + ') : ' + str(random.randint(0,100)) +'%'
            elif s[0] == "!забив" and tag:
                srs = "📣🐖   Забив : \n\n"+ "🇺🇦" + get_sender + "🇺🇦        🆚        ✡" + s[1] + '✡\n\n🏆   Победил: ' \
                      + random.choice([get_sender , tag.group(0)]) + "   🏆"
            elif s[0] == "!факт" and s[1] is not None:
                srs = "❗ Факт (" + s[1] + ") " + random.choice(['Ложь ⛔', 'Правда ✅'])
            elif s[0] in who_module and tag:
                key = who_module.get(s[0])
                srs = f"{key[0] +  get_sender + key[1] + tag.group(0) + key[2]}"
            else:
                ss = None
                srs = None
        else:
            ss = None
            srs = None
        return [ss,srs]

def convert_img(input,output_name,convert_to):
    ipng = Image.open(input).convert()
    ipng.save(output_name,convert_to)

def KILL_ALL_MEMBERS():
        list_members = GetMembers()[1]
        for member in list_members:
            kick(chat_id= respondent.object['peer_id'] - 2000000000, member_id=member)

def manager_kick():
    two_word_sep = str(respondent.object['text']).split(sep=' ',maxsplit=1)
    try:
        if len(two_word_sep) == 2:
            tag = re.compile('@(\w+)').search(two_word_sep[1])
            tag_id = two_word_sep[1].split(sep='|')[0].replace('[id', '')
            if two_word_sep[0] == '/кик' and tag:  kick(chat_id=peerID - 2000000000, member_id=tag_id)
        else:
            rpl = (respondent.object).get('reply_message', False)
            if rpl:  kick(chat_id=peerID - 2000000000, member_id=respondent.object.reply_message['from_id'])
    except Exception as e:
         send(f"НЕЛЬЗЯ МУДИЛА \n{e}")

def invite_user():
    three_word_sep = str(respondent.object['text']).split(sep=' ', maxsplit=2)
    try:
        if len(three_word_sep) == 3 and three_word_sep[0] == '/addUser' and three_word_sep[1] == re.findall("[0-9]{1,10}",three_word_sep[1])[0] and three_word_sep[2]==re.findall("[0-9]{1,10}",three_word_sep[2])[0]:
            vk_full.messages.addChatUser(chat_id=three_word_sep[1],user_id=three_word_sep[2])
    except Exception as e:
         send(f"НЕЛЬЗЯ МУДИЛА \n{e}")

def EVIL_GOD_Update():
    if respondent.object['from_id'] in EVIL_GODS:
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT * FROM peers WHERE peer_id = {respondent.object['peer_id']}")
        str_E_G = edit.fetchone()
        if str_E_G[1] == '0':
            str_E_G = '1'
            send('Безмолвие')
        else:
            str_E_G = '0'
            send('*Уходит*')
        edit.execute("UPDATE peers SET e_g_mute = ? where peer_id = ?",(str_E_G,respondent.object['peer_id']))
        BD.commit()

def EVIL_GOD():
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    edit.execute(f"SELECT * FROM peers WHERE peer_id = {respondent.object['peer_id']}")
    str_E_G = edit.fetchone()
    if respondent.object['from_id'] not in EVIL_GODS and str_E_G[1] == '1':
        vk.messages.delete(peer_id = respondent.object['peer_id'],conversation_message_ids = respondent.object['conversation_message_id'],group_id=IdGroupVK,delete_for_all=1)

def set_count_period():
    two_word_sep = str(respondent.object['text']).split(sep=' ', maxsplit=1)
    if len(two_word_sep) == 2 and two_word_sep[1] == re.findall("[0-9]{1,3}",two_word_sep[1])[0]:
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute("UPDATE peers SET count_period = ? where peer_id = ?", (int(two_word_sep[1]), respondent.object['peer_id']))
        BD.commit()
        send(f"Значение установлено на {two_word_sep[1]}")

def edit_node():
    if respondent.object['peer_id'] < 2000000000 and respondent.object['peer_id'] in EVIL_GODS:
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        word_sep = str(respondent.object['text']).split(sep=' ', maxsplit=3)
        if len(word_sep) == 4:
            if word_sep[2] == re.findall("[0-9]{1,10}",word_sep[2])[0] and word_sep[3] == re.findall("-[0-9]{9,13}",word_sep[3])[0]:
                try:
                    if word_sep[1] == 'create':
                        edit.execute("INSERT OR IGNORE INTO nodes VALUES(?,?)", (int(word_sep[2]), int(word_sep[3])))
                        BD.commit()
                        send("Соединено")
                    if word_sep[1] == 'update':
                        edit.execute("UPDATE nodes SET tg_id = ? where peer_id = ?",(int(word_sep[3]),int(word_sep[2])))
                        BD.commit()
                        send("Обновлено")
                    if word_sep[1] == 'delete':
                        edit.execute("DELETE FROM nodes where peer_id = ? and tg_id = ?", (int(word_sep[2]), int(word_sep[3])))
                        BD.commit()
                        send("Удалено")
                except Exception as e:
                    send(f"Не успешно: {e}")
        if len(word_sep) == 2:
            if word_sep[1] == 'list':
                edit.execute("SELECT * FROM nodes")
                list_nodes= edit.fetchall()
                s = ''
                n = 0
                for node in list_nodes:
                    n=n+1
                    s += f"{n}: {str(node)}\n"
                send(s)

def words_manager():
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    word_sep_l = str(respondent.object['text']).splitlines()
    word_sep = str(word_sep_l[0]).split(sep=' ', maxsplit=1)
    if len(word_sep) == 2 and len(word_sep_l) == 3:
            try:
                if word_sep[1] == 'create':
                    edit.execute("INSERT OR IGNORE INTO words VALUES(?,?)", (word_sep_l[1], word_sep_l[2]))
                    BD.commit()
                    send("Создано")
                if word_sep[1] == 'update':
                    edit.execute("UPDATE words SET tg_id = ? where peer_id = ?", (word_sep[1], word_sep[2]))
                    BD.commit()
                    send("Обновлено")
                if word_sep[1] == 'delete':
                    edit.execute("DELETE FROM words where key = ? and val = ?",(word_sep[1], word_sep[2]))
                    BD.commit()
                    send("Удалено")
            except Exception as e:
                send(f"Не успешно: {e}")
    if len(word_sep) == 2:
        if word_sep[1] == 'list':
            edit.execute("SELECT * FROM words")
            list_words = edit.fetchall()
            s = ''
            n = 0
            for word in list_words:
                n = n + 1
                s += f"{n}: {str(word)}\n"
            send(s)

################################### вк бот ################################################
def vk_bot_respondent():
    global i, respondent , peerID, who , tag, tag_id
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    edit.execute("""CREATE TABLE IF NOT EXISTS peers( peer_id INT PRIMARY KEY, e_g_mute TEXT,count_period INT); """)
    edit.execute("""CREATE TABLE IF NOT EXISTS nodes( peer_id INT PRIMARY KEY, tg_id INT); """)
    edit.execute("""CREATE TABLE IF NOT EXISTS words( key TEXT PRIMARY KEY, val TEXT); """)
    BD.commit()
    for respondent in longpoll.listen():
        try:
            if respondent.type == VkBotEventType.MESSAGE_NEW:
                i = i + 1
        ######################################### VK Event ########################################
                TEXT = respondent.object['text']
                peerID = respondent.object['peer_id']
                if respondent.object.from_id > 0: who = WHO(TEXT,getUserName(respondent.object.from_id))
                lines = str(TEXT).lower().splitlines()
                TextSplitLowerDict = set('')
                if lines: TextSplitLowerDict = set(lines[0].split())
                Dictwords = []
        ######################################### DB ########################################
                #Стандартные настройки чатов
                data = (peerID,'0',0)
                edit.execute("INSERT OR IGNORE INTO peers VALUES(?,?,?)", data)
                BD.commit()
                #Частота
                edit.execute(f"SELECT * FROM peers WHERE peer_id = {respondent.object['peer_id']}")
                count_period = int(edit.fetchone()[2])
                #Шаблонные ответы
                edit.execute(f"SELECT * FROM words")
                words = edit.fetchall()
                for word in words:
                    Dictwords.append(word[0])
        ################################ Словари для запрос-ответ #################################
                command_service_text = {
                    '/idchat'          : "ID чата : " + str(peerID), #узнать ID чата
                    '/clear_docs_init' : clear_docs(), #очистка доков в группе
                    f"{who[0]}"        : f"{who[1]} ", #Команда на вероятности и выбор
                    '/role_list': (str(list(who_module))).replace(',','\n').replace('[','').replace(']','').replace("'",""),
                }
                command_service_func = {
                    '/кик': manager_kick,
                    '/мем': get_album_photos_mem,
                    '/cabal:kill_all_members=active': KILL_ALL_MEMBERS,
                    '/addUser': invite_user,
                    '*присутствие_злого_бога*': EVIL_GOD_Update,
                    '/частота': set_count_period,
                    '/node': edit_node,
                    '/word': words_manager,
                }
        ############################### Обработка ######################################
            ################## Выбор значения по ключу из command ##################
                if str(TEXT).split(sep=' ')[0] != '/word' and TEXT is not None:
                    dw = dict(words)
                    if TextSplitLowerDict & set(Dictwords):
                        for element in TextSplitLowerDict:
                            key = dw.get(element)
                            if key is not None: send(key)
                    elif set(lines) & set(Dictwords):
                        for element in lines:
                            key = dw.get(element)
                            if key is not None: send(key)

            ################## Выбор значения по ключу из command_service (команды функций с возвратом текста) ##################
                if TEXT in command_service_text:
                    key1 = command_service_text.get(TEXT)
                    if key1 is not None: send(key1)
            ################## Выбор значения по ключу из command_service (команды функций с исполнением) ##################
                if str(TEXT).split(sep=' ')[0] in command_service_func:
                    key2 = command_service_func.get(str(TEXT).split(sep=' ')[0])
                    if key2 is not None: key2()

                if count_period !=0 and TEXT and i % count_period == 0:  send(random.choice(a))
                if TEXT : EVIL_GOD()
            ###########################################################################################
        except Exception as e:
            send(f"{e}")
############################ отправка в чат телеги из вк ##################################

def vk_bot_resend():
    global i, resend, TitleChat
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    for resend in longpoll_full.listen():
        try:
            ################################## Обработчик #########################################
            if resend.type == VkBotEventType.MESSAGE_NEW:
                ########################## Распределение точек отправки ###############################
                edit.execute(f"SELECT tg_id FROM nodes WHERE peer_id = {resend.object['peer_id']}")
                tg_id = edit.fetchone()
                if tg_id is not None: node = tg_id[0]
                else: node = idGroupTelegram
                #######################################################################################
                UserId = resend.object['from_id']
                user = str(getUserName(UserId))
                PeerId = resend.object.peer_id
                TEXT = resend.obj.text
                if PeerId > 2000000000:TitleChat = GET_CHAT_TITLE(PeerId)
                #######################################################################################
                if resend.object['from_id'] > 0:
                    for att in resend.obj.attachments:
                        tb1 =f"\n_____________________________________________________\n"
                        if PeerId > 2000000000:tb1 += f"{user + '  из чата : ' + str(PeerId)}\n{'  [   ' + str(TitleChat) + '   ]'}\n"
                        else: tb1 += f"\nЛичное сообщение от пользователя\n {str(user)} \n"
                ###########################################################################################
                        if att['type'] == 'photo':  # Если прислали фото
                            urls =[size['url'] for size in att['photo']['sizes']]
                            types_ = [size['type'] for size in att['photo']['sizes']]
                            max_size = sorted(types_, key=lambda x: size_values.index(x))[-1]
                            urldict = dict(zip(types_, urls))
                            logging.info(f"{tb1}\n{urldict.get(max_size)}\n_____________________________________________________")
                            bot.send_photo(node, get(urldict.get(max_size)).content, tb1)
                ###########################################################################################
                        elif att['type'] == 'audio_message':
                            logging.info(f"{tb1}\n{att['audio_message']['link_mp3']}")
                            bot.send_audio(node,get(att['audio_message']['link_mp3']).content,tb1)
                ###########################################################################################
                        elif att['type'] == 'sticker':
                            bot.send_photo(node, get(att['sticker']['images'][2]['url']).content, tb1)
                ###########################################################################################
                        elif att['type'] == 'doc':  # Если прислали документ
                            tb1 += (f"{str(att['doc']['url']).replace('no_preview=1', '')}\n_____________________________________________________")
                            SendTG(node,tb1)
                ###########################################################################################
                        elif att['type'] == 'video':
                            tb1 += (f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}\n\n_____________________________________________________")
                            SendTG(node,tb1)
                ###########################################################################################
                        elif att['type'] == 'audio':
                            tb1 += (f"https://vk.com/audio{att['audio']['owner_id']}_{att['audio']['id']}\n")
                            duration = int(att['audio']['duration'])
                            info = (f"_____________________________________________________\n"
                           f"{att['audio']['artist']} - {att['audio']['title']} {att['audio'].get('subtitle', '')}"       
                           f"\nДлительность:   {str(duration // 60)}:{str(duration % 60)}\n_____________________________________________________\n")
                            logging.info(tb1 + info)
                            try: bot.send_audio(node,att['audio']['url'],tb1 + info )
                            except: SendTG(node, tb1 + info)
                ###########################################################################################
                        elif att['type'] == "link":  # Если прислали ссылку(напиример: на историю)
                            tb1 += (f"\n\n{att['link']['url']}\n_____________________________________________________")
                            SendTG(node,tb1)
                ###########################################################################################
                        elif att['type'] == 'wall':  # Если поделились постом
                            ############################## Определение происхождения поста (юзер или группа)#########################
                            if PeerId > 2000000000:
                                textboxhead = textboxFILE = f"\n_____________________________________________________\n"
                                f"{user + '  из чата : ' + str(PeerId)}\n{' [     ' + str(TitleChat) + '     ]' + ' : '} \n поделился постом :\n"
                            else:
                                textboxhead = textboxFILE = f"\n_____________________________________________________\n{user} поделился постом :\n"
                            ######################################## Имя источника ################################################
                            frm = att['wall']['from']
                            ag = frm.get('name',0)
                            if ag == 0:
                                textboxhead += f"\n\n Пользовтель: {att['wall']['from']['first_name']} {att['wall']['from']['last_name']}"
                            else:
                                textboxhead += f"\n\n группа: {att['wall']['from']['name']}"
                            ###########################################################################################
                            textboxhead += str(f"\n\n{att['wall']['text']}\n_____________________________________________________")
                            textboxaudio = ''
                            try:
                                for wall_att in att['wall']['attachments']:
                                    if wall_att['type'] == 'photo':
                                        bot.send_photo(node,get(f"{wall_att['photo']['sizes'][-1]['url']}").content, textboxhead)
                                        textboxFILE += str(f"\n{wall_att['photo']['sizes'][-1]['url']}\n")
                                    if wall_att['type'] == 'video':
                                        textbox = str(f"\nhttps://vk.com/video{str(wall_att['video']['owner_id'])}_{str(wall_att['video']['id'])}\n")
                                        textboxFILE += str(f"\nhttps://vk.com/video{str(wall_att['video']['owner_id'])}_{str(wall_att['video']['id'])}\n")
                                        bot.send_message(node,textboxhead + textbox)
                                    if wall_att['type'] == 'doc':
                                        textbox = str(f"\n{str(wall_att['doc']['url']).replace('no_preview=1', '')}\n")
                                        textboxFILE += str(f"\n{str(wall_att['doc']['url']).replace('no_preview=1', '')}\n")
                                        bot.send_message(node, textboxhead + textbox)
                                    if wall_att['type'] == 'link':
                                        textbox = str(f"\n{str(wall_att['link']['url'])}\n")
                                        textboxFILE += str(f"\n{str(wall_att['link']['url'])}\n")
                                        bot.send_message(node, textboxhead + textbox)
                                    if wall_att['type'] == 'audio':
                                        textboxaudio += (f"\nhttps://vk.com/audio{wall_att['audio']['owner_id']}_{wall_att['audio']['id']}\n"
                                                f"{wall_att['audio']['artist'] + ' - ' + wall_att['audio']['title'] + ' ' + wall_att['audio'].get('subtitle', '')}"
                                                f"\n{'Длительность: ' + str(int(wall_att['audio']['duration']) // 60)}"
                                                f"{':' + str(int(wall_att['audio']['duration']) % 60)}")
                                if textboxaudio != '':
                                    SendTG(node,textboxhead + textboxaudio)
                                    textboxFILE += f"\n_____________________________________________________\n"
                                    logging.info(textboxFILE)
                            except:
                                SendTG(node,textboxhead)
        ###########################################################################################
                    if TEXT != "":
                        texts = f"\n{str(user) +'( https://vk.com/id' + str(UserId) + ' ) ' }"
                        if PeerId > 2000000000:
                            texts += f"{' Из чата (' + str(PeerId) + ')'}\n{'[     ' + str(TitleChat) + '     ]' + ' : '}\n"
                        texts += f"_____________________________________\n\n{TEXT}\n_____________________________________\n\n"
                        SendTG(node,texts)
        ################################# Обработка событий чата ###################################
                    if resend.object.action is not None:
                        if resend.object.action['type'] in tab:
                            key = tab.get(resend.object.action['type'])
                            SendTG(node,f"{ key + str(getUserName(resend.object.action['member_id']))}⚠⚠⚠")
                        elif resend.object.action['type'] == 'chat_title_update':
                            SendTG(node, f"⚠⚠⚠Обновлено название чата {str(resend.object.action['text'])}⚠⚠⚠")
        except Exception as e:
            vk.messages.send(random_id=0, message=f"{e}", peer_id=resend.obj.peer_id)
############################ отправка в чат вк из телеги ##################################
def vkNode():
    @bot.message_handler(content_types=['text','video','photo','document','animation','sticker','audio'])
    def TG_VK(message):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        idchat = message.chat.id
        edit.execute(f"SELECT peer_id FROM nodes WHERE tg_id = {idchat}")
        peer = edit.fetchone()
        node = None
        if peer is not None: node = peer[0]
        ###########################################################################################
        idmessage_start = int(message.message_id)
        msg = message.text
        time.sleep(1)
        ###########################################################################################
        if node is not None:
            if message.text:
                idmessage = int(message.message_id) - 1
                if msg and not message.forward_from and not message.forward_sender_name:
                    last_name = message.from_user.last_name
                    if last_name is None:
                        last_name = ''
                    msgtg = str(message.from_user.first_name) + ' ' + last_name + ' : ' + msg
                    vk.messages.send(random_id=idmessage, message=msgtg, peer_id=node)
                if idmessage < idmessage_start:
                    if message.forward_from:
                        time.sleep(1)
                        last_name_fwd = message.forward_from.last_name
                        if msg is None:
                            msg = ''
                        if last_name_fwd is None:
                            last_name_fwd = ''
                        user = str(message.forward_from.first_name) + ' ' + str(last_name_fwd)
                        vk.messages.send(random_id=idmessage, message=' От  ' + user + "\n " + str(msg),peer_id=node)
                    if message.forward_sender_name:
                        time.sleep(1)
                        vk.messages.send(random_id=idmessage, message=' От  ' + message.forward_sender_name + "\n " + str(msg),peer_id=node)
            ###########################################################################################
            if message.video:
                idvideo = message.video.file_id
                captionvideo = message.caption
                name = idvideo + '.mp4'
                write_file(name,bot.download_file((bot.get_file(idvideo)).file_path))
                u = upload.video(video_file=name,name=idvideo,wallpost=0,is_private=True,group_id=IdGroupVK)
                vidos = "video"+str(u['owner_id']) + '_' + str(u['video_id']) + "?list=" + str(u['access_key'])
                vk.messages.send(random_id=random.randint(0, 999999), message=captionvideo, peer_id=node,attachment=vidos)
                logging.info(f"\n{vidos}\n")
                os.remove(name)
            ###########################################################################################
            if message.photo:
                try: idphoto = message.photo[2].file_id
                except : idphoto = message.photo[0].file_id
                captionphoto = message.caption
                namephoto = idphoto + '.jpg'
                write_file(namephoto,bot.download_file((bot.get_file(idphoto)).file_path))
                u = upload.photo_messages(photos=namephoto,peer_id=node)[0]
                photo = "photo" + str(u['owner_id']) + '_' + str(u['id']) + "_" + str(u['access_key'])
                vk.messages.send(random_id=random.randint(0, 999999), message=captionphoto, peer_id=node, attachment=photo)
                logging.info(f"\n{photo}\n")
                os.remove(namephoto)
            ###########################################################################################
            if message.document:
                try:
                    iddocument = message.document.file_id
                    captiondocument = message.caption
                    if captiondocument is None:
                        captiondocument = ''
                    sep = str(message.document.mime_type).split(sep='/')[1]
                    if sep == 'mp4':
                        namedocument = iddocument + '.' + sep
                        write_file(namedocument,bot.download_file((bot.get_file(iddocument)).file_path))
                        u = upload.video(video_file=namedocument, name=iddocument, wallpost=0, is_private=True,group_id=IdGroupVK,repeat=True)
                        animation = "video" + str(u['owner_id']) + '_' + str(u['video_id']) + "?list=" + str(u['access_key'])
                        logging.info(f"\n{animation}\n")
                        vk.messages.send(random_id=random.randint(0, 999999), message=captiondocument, peer_id=node,attachment=animation)
                    else:
                    ############################### распределение MIME типов ##################################
                        if sep in types:
                            sepget = types.get(sep)
                        else:
                            sepget = 'test'
                    ###########################################################################################
                        namedocument = iddocument + '.' + sepget
                        write_file(namedocument, bot.download_file((bot.get_file(iddocument)).file_path))
                        mtpsget = mtps.guess_extension(message.document.mime_type)
                        if mtpsget is None:
                            mtpsget = (magic.Magic(mime=True)).from_file(namedocument)
                        u = upload.document(doc=namedocument,title=str(random.randint(1,1000000)),group_id=IdGroupVK,to_wall=0)
                        document = "doc"+str(u['doc']['owner_id']) + '_' + str(u['doc']['id']) + '?' + str(u['doc']['url']).split(sep='?')[1].replace('&no_preview=1','')
                        logging.info(f"\n{namedocument}\n{document}\n")
                        vk.messages.send(random_id=random.randint(0, 999999), message= f"{captiondocument}\n{mtpsget}",peer_id=node, attachment=document)
                        ###########################################################################################
                    os.remove(namedocument)
                except Exception as e:
                    vk.messages.send(random_id=random.randint(0, 999999), message= e,peer_id=PEER_CRUSH_EVENT)
                    SendTG(message.chat.id,'\n⚠⚠⚠ Ошибка загрузки ⚠⚠⚠')
            ###########################################################################################
            if message.sticker:
                idsticker = message.sticker.file_id
                if str((bot.get_file(idsticker)).file_path).split(sep='.')[1] != 'tgs':
                    namesticker = idsticker + '.webp'
                    write_file(namesticker,bot.download_file((bot.get_file(idsticker)).file_path))
                    convert_img(namesticker,f"{idsticker}.png","png")
                    os.remove(namesticker)
                    u = upload.graffiti(image =f"{idsticker}.png",group_id=IdGroupVK)
                    sticker = "doc" + str(u['graffiti']['owner_id']) + '_' + str(u['graffiti']['id']) + "_" + str(u['graffiti']['access_key'])
                    logging.info(f"\n{idsticker}.png\n{sticker}\n")
                    vk.messages.send(random_id=random.randint(0, 999999), message='',peer_id=node, attachment=sticker)
                    os.remove(f"{idsticker}.png")
            if message.audio:
                idaudio = message.audio.file_id
                write_file(idaudio + '.mp3',bot.download_file((bot.get_file(idaudio)).file_path))
                u = vk.docs.getMessagesUploadServer(type='audio_message',peer_id=node)
                responses = requests.post(u['upload_url'], files={'file': open(idaudio + '.mp3', 'rb')}).json()
                w = vk.docs.save(file=responses['file'])
                msg_voice = "doc" + str(w['audio_message']['owner_id']) + '_' + str(w['audio_message']['id'])
                vk.messages.send(random_id=random.randint(0, 999999), message='', peer_id=node, attachment=msg_voice)
                os.remove(f"{idaudio}.mp3")
    bot.polling(none_stop=True, interval=0)