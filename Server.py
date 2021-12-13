import random, logging,os,mimetypes as mtps, magic , time , requests,sqlite3
from tools import write_file, convert_img, write_file_json,read_file_json,json_gen
from online_tools import getUserName,GetMembers,GET_CHAT_TITLE,SendTG,send_to_specific_peer
from respondent_func import WHO,COMMAND,privileges
from sessions import longpoll, vk,bot,longpoll_full,upload,size_values,tab,platforms
from datetime import datetime
from requests import get
from vk_api.bot_longpoll import  VkBotEventType
from CONFIG import  IdGroupVK ,types ,config_file_json

################### Логирование ###########################
file_log = logging.FileHandler('Log.log', 'a', 'utf-8')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)
i = 0

################################### вк бот ################################################
def vk_bot_respondent():
    global i, respondent , peerID, who
    if not os.path.isfile(config_file_json):
        write_file_json(config_file_json,json_gen().return_json())
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    edit.execute("""CREATE TABLE IF NOT EXISTS peers( peer_id INT PRIMARY KEY, e_g_mute TEXT,count_period INT); """)
    edit.execute("""CREATE TABLE IF NOT EXISTS nodes( peer_id INT PRIMARY KEY, tg_id INT); """)
    edit.execute("""CREATE TABLE IF NOT EXISTS params_info( param TEXT PRIMARY KEY, info TEXT); """)
    for e in read_file_json(config_file_json):
        edit.execute(f"INSERT OR IGNORE INTO params_info VALUES('{e}','')")
    BD.commit()

    BDWORDS = sqlite3.connect('peers_words.db')
    edit_word = BDWORDS.cursor()
    BDWORDS.commit()

    BDROLES = sqlite3.connect('peers_roles.db')
    edit_roles = BDROLES.cursor()
    BDROLES.commit()

    BDQUOTES = sqlite3.connect('peers_quotes.db')
    edit_quotes = BDQUOTES.cursor()
    BDQUOTES.commit()

    for respondent in longpoll.listen():
        try:
            if respondent.type == VkBotEventType.MESSAGE_NEW:
                i = i + 1
        ######################################### VK Event ########################################
                TEXT = respondent.object['text']
                peerID = respondent.object['peer_id']
                from_id = respondent.object['from_id']
                lines = str(TEXT).lower().splitlines()
                TextSplitLowerDict = set('')
                if lines: TextSplitLowerDict = set(lines[0].split())
                Dictwords = []
        ######################################### DB ########################################
                #Стандартные настройки чатов
                data = (peerID,'0',0)
                edit.execute("INSERT OR IGNORE INTO peers VALUES(?,?,?)", data)
                BD.commit()

                #Частота рандомных ответов
                edit.execute(f"SELECT * FROM peers WHERE peer_id = {peerID}")
                count_period = int(edit.fetchone()[2])

                #Шаблонные ответы
                edit_word.execute(f"CREATE TABLE IF NOT EXISTS '{str(peerID)}' ( id INT, key TEXT PRIMARY KEY, val TEXT);")
                BDWORDS.commit()
                edit_word.execute(f"SELECT key,val FROM '{str(peerID)}' ")
                words = edit_word.fetchall()
                for word in words:
                    Dictwords.append(word[0])

                #ролевые команды
                edit_roles.execute(f"CREATE TABLE IF NOT EXISTS '{str(peerID)}' ( id INT PRIMARY KEY, command TEXT ,emoji_1 TEXT, txt TEXT, emoji_2 TEXT);")

                #Рандомные высказывания бота
                edit_quotes.execute(f"CREATE TABLE IF NOT EXISTS '{str(peerID)}' ( id INT PRIMARY KEY, quote TEXT);")
                BDQUOTES.commit()
                edit_quotes.execute(f"SELECT quote FROM '{str(peerID)}'")
                quotes = edit_quotes.fetchall()
        ################################ Словари для запрос-ответ #################################
                prefix = {
                    '*': privileges(TEXT,from_id,peerID,respondent.object).check(),
                    '!': WHO(TEXT,from_id,peerID).WHO_GET(),
                    '/': COMMAND(TEXT,from_id,peerID,respondent.object).check()
                }
        ############################### Обработка ######################################
                if TEXT is not '':
                    privileges(TEXT,from_id,peerID,respondent.object).EVIL_GOD()
                    if str(TEXT)[0] != '/' or '*' or '!':
                        dw = dict(words)
                        if set(lines) & set(Dictwords):
                            for element in lines:
                                key = dw.get(element)
                                if key is not None: send_to_specific_peer(key,peerID)
                        elif TextSplitLowerDict & set(Dictwords):
                            for element in TextSplitLowerDict:
                                key = dw.get(element)
                                if key is not None: send_to_specific_peer(key,peerID)
                    if TEXT[0] in prefix:
                        key1 = prefix.get(TEXT[0])
                        if key1 is not None: key1()

                if count_period !=0 and TEXT and \
                    i % count_period == 0 and quotes != []:  send_to_specific_peer(random.choice(quotes),peerID)
            ###########################################################################################
        except Exception as e:
            send_to_specific_peer(f"{e}",peerID)
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
                else: node = json_gen().return_config_file_json()['idGroupTelegram']
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
                            tb1 += f"{str(att['doc']['url']).replace('no_preview=1', '')}\n_____________________________________________________"
                            SendTG(node,tb1)
                ###########################################################################################
                        elif att['type'] == 'video':
                            tb1 += f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}\n\n_____________________________________________________"
                            SendTG(node,tb1)
                ###########################################################################################
                        elif att['type'] == 'audio':
                            tb1 += f"https://vk.com/audio{att['audio']['owner_id']}_{att['audio']['id']}\n"
                            duration = int(att['audio']['duration'])
                            info = (f"_____________________________________________________\n"
                           f"{att['audio']['artist']} - {att['audio']['title']} {att['audio'].get('subtitle', '')}"       
                           f"\nДлительность:   {str(duration // 60)}:{str(duration % 60)}\n_____________________________________________________\n")
                            logging.info(tb1 + info)
                            try: bot.send_audio(node,att['audio']['url'],tb1 + info )
                            except: SendTG(node, tb1 + info)
                ###########################################################################################
                        elif att['type'] == "link":  # Если прислали ссылку(напиример: на историю)
                            tb1 += f"\n\n{att['link']['url']}\n_____________________________________________________"
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
 try:
    @bot.message_handler(commands=['id'])
    def show_id(message):
        bot.send_message(message.chat.id, message.chat.id)

    @bot.message_handler(commands=['online'])
    def show_online(message):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT peer_id FROM nodes WHERE tg_id = {message.chat.id}")
        peer = edit.fetchone()
        node = None
        fields = ''
        if peer is not None: node = peer[0]
        if node is not None:
            info = vk.users.get(user_ids=GetMembers(node)[0],fields=['first_name','last_name','online','last_seen'])
            for field in info:
                online = '✅ONLINE' if field['online'] == 1 else '❌OFFLINE'
                get_seen = field.get('last_seen', None)
                if get_seen is not None :
                    get_seen = f" C {datetime.fromtimestamp(get_seen['time'])} через " \
                               f"{platforms.get(get_seen['platform'])}" if online == '❌OFFLINE' else f"{platforms.get(get_seen['platform'])}"
                else: get_seen = ''
                fields += f"{field['first_name']} {field['last_name']} - {online} {get_seen}\n\n"
            bot.send_message(message.chat.id,fields)
        else: bot.send_message(message.chat.id,"Этот чат не имеет привязки к вк чату")

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
                    vk.messages.send(random_id=random.randint(0, 999999), message= e,
                                     peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])
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
                #else:
                #    in_= f"pylottie/{idsticker+'.tgs'}"
                #    out = idsticker
                #    write_file(in_, bot.download_file((bot.get_file(idsticker)).file_path))
                #    file = TGS_TO_GIF([in_],[out])
                #    print(file)

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
 except Exception as e:
     vk.messages.send(random_id=0, message=f"{e}", peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])