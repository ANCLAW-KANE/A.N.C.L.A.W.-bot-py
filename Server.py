import vk_api , random, telebot,logging, json,os, magic, re, math , time
from PIL import Image
import mimetypes as mtps
from requests import get
from vk_api import VkApi
from respondent import new_message_rand
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from CONFIG import idGroupTelegram , IdGroupVK , teletoken , vktokenGroup , Nodes ,\
    count_period , command, vktokenUser, types ,CAPTCHA_EVENT,OWNER_ALBUM_PHOTO,PEER_CRUSH_EVENT

################### Логирование ###########################
file_log = logging.FileHandler('Log.log', 'a', 'utf-8')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)
################ Служебные переменные #####################
i = 0

################### Авторизация ###########################
bot = telebot.TeleBot(teletoken)

vk_session: VkApi = vk_api.VkApi(token=vktokenGroup)#Группа
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, IdGroupVK)

def captcha_handler(captcha):#обход капчи
    for captcha_trigger in longpoll.listen():
        if captcha_trigger.object.peer_id == CAPTCHA_EVENT:
            vk.messages.send(random_id=random.randint(0, 999999), message=f"Enter captcha code: {captcha.get_url()}", peer_id=CAPTCHA_EVENT)
            return captcha.try_again( captcha_trigger.object.text)

vk_session_user : VkApi = vk_api.VkApi(token=vktokenUser,captcha_handler=captcha_handler)#Пользователь
vk_user = vk_session_user.get_api()

vk_session_kate : VkApi = vk_api.VkApi(token='60df71375fbe40b161c1d8d5ca4d91928cc3833e6bda8610c74ef8cb22173f909550b6afc0eedd5ff162b',captcha_handler=captcha_handler)
vk_kate = vk_session_kate.get_api()

upload = vk_api.VkUpload(vk_user)
################################## Блок функций #######################################

def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, member_id=member_id)

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
    for mbs in members['items']:
        member = mbs['member_id']
        admin = mbs.get('is_admin', False)
        if member > 0:
            membList.append(member)
        if member > 0 and admin != True:
            membListNotAdmin.append(member)
    return [membList,membListNotAdmin]

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

#def GET_CHAT_LIST():
#    get_items_chat = vk.messages.getConversationsById(peer_ids=respondent.object.peer_id)
#    CHAT_LIST = []
#    for chats in get_items_chat['items']:
#        chat_local_id = chats['peer']['local_id']
#        if chat_local_id > 0:
#                CHAT_LIST.append(chat_local_id)
#    return CHAT_LIST

def GET_CHAT_TITLE(object):
    get_items_chat = vk.messages.getConversationsById(peer_ids=object)
    for chats in get_items_chat['items']:
        chat_title = chats['chat_settings']['title']
        return chat_title

def reverse_Nodes():
    reverseNodes = []
    for idchat in Nodes.keys():
        reverseNodes.append((Nodes[idchat], idchat))
        getreversenode = dict(reverseNodes)
    return getreversenode

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

def get_album_photo():
    try:
        parse_album = str(random.choice(get_list_album())).split(sep='_')
        if parse_album[1] == '0': parse_album = str(random.choice(get_list_album())).split(sep='_')
        if int(parse_album[1]) > 50: offset_max = math.floor(int(parse_album[1]) / 50)
        else: offset_max = 0
        alb_ph = vk_user.photos.get(owner_id=OWNER_ALBUM_PHOTO, album_id=parse_album[0], count=50 , offset=random.randint(0,offset_max) * 50)
        photoList = []
        for photo in alb_ph['items']:
            idphoto = str(photo['id'])
            photoList.append(idphoto)
        if photoList is not None: return send_attachments(f"photo{str(OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}",'')
    except: return send_attachments('photo388145277_456240127','блядь я мем пробухал')

def WHO(object,get_sender):
    s = str(object).lower().split(maxsplit=1)
    if len(s) == 2:
        tag = re.compile('@(\w+)').search(s[1])
        if s[0] == "!кто" and s[1] is not None:
            ss = s[0] + ' ' + s[1]
            srs = "❓ ➡➡➡  " + RandomMember() + '  ⬅⬅⬅  :  ' + s[1]
        elif s[0] == "!вероятность" and s[1] is not None:
            ss = s[0] + ' ' + s[1]
            srs = "📊 Вероятность для  (" + s[1] + ') : ' + str(random.randint(0,100)) +'%'
        elif s[0] == "!забив" and tag:
            ss = s[0] + ' ' + s[1]
            srs = "📣🐖   Забив : \n\n"+ "🇺🇦" + get_sender + "🇺🇦        🆚        ✡" + s[1] + '✡\n\n🏆   Победил: ' + random.choice([get_sender , tag.group(0)]) + "   🏆"
        elif s[0] == "!факт" and s[1] is not None:
            ss = s[0] + ' ' + s[1]
            srs = "❗ Факт (" + s[1] + ") " + random.choice(['Ложь ⛔', 'Правда ✅'])
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

def KILL_ALL_MEMBERS(object):
    list_members = GetMembers()[1]
    for member in list_members:
        kick(chat_id= object - 2000000000, member_id=member)


################################### вк бот ################################################
def vk_bot_respondent():
    global i, respondent , peerID
    for respondent in longpoll.listen():
        ######################################### VK Event ########################################
        TEXT = respondent.object['text']
        peerID = respondent.object['peer_id']
        who = WHO(TEXT,getUserName(respondent.object.from_id))
        ############################### Словари из сообщений ######################################
        TextSplitLowerDict = set(str(TEXT).lower().split())
        TextDictSplitLines = set(str(TEXT).lower().splitlines())
        ################################ Словарь для запрос-ответ #################################
        command_service = {
            '/idchat'          : "ID чата : " + str(peerID), #узнать ID чата
            '/clear_docs_init' : clear_docs(), #очистка доков в группе
            f"{who[0]}"        : f"{who[1]} ", #Команда на вероятности и выбор
        }
        #command_attachments = {
        #    '/мем' : get_album_photo(),
        #    '/cabal:kill_all_members=active': KILL_ALL_MEMBERS(peerID),
        #}
        ############################### Обработка ######################################
        if respondent.type == VkBotEventType.MESSAGE_NEW:
            i = i + 1
            ################## Выбор значения по ключу из command ##################
            if TextSplitLowerDict & set(command):
                for element in TextSplitLowerDict:
                    key = command.get(element)
                    if key is not None: send(key)
            ################## Выбор значения по ключу из command_service ##################
            elif TextDictSplitLines & set(command_service):
                for element1 in TextDictSplitLines:
                    key1 = command_service.get(element1)
                    if key1 is not None: send(key1)
            ################## Выбор значения по ключу из command_attachments ##################
            elif TEXT == '/мем' : get_album_photo()
            elif TEXT == '/cabal:kill_all_members=active': KILL_ALL_MEMBERS(peerID)
            elif TEXT and i % count_period == 0 :
                send(new_message_rand())
            ###########################################################################################
            elif respondent.object.text in ['кик']:
                try: kick(chat_id=peerID - 2000000000, member_id=respondent.object.reply_message['from_id'])
                except: send("НЕЛЬЗЯ МУДИЛА")
        else: None
############################ отправка в чат телеги из вк ##################################

def vk_bot_resend():
    global i, resend
    for resend in longpoll.listen():
        UserId1 = resend.object['from_id']
        user1 = str(getUserName(resend.object.from_id))
        PeerId = resend.object.peer_id
        TitleChat = GET_CHAT_TITLE(PeerId)
        ########################## Распределение точек отправки ###############################
        if PeerId in Nodes: node = Nodes.get(PeerId)
        else: node = idGroupTelegram
        ############################### Служебные функции #####################################
        if resend.obj.text == 'ping_anclaw':
            vk.messages.send(random_id=random.randint(0, 999999), message="Поток 2 активен", peer_id=resend.obj.peer_id)
        ################################## Обработчик #########################################
        if UserId1 > 0:
            for att in resend.obj.attachments:
                tb1 =(f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}\n" 
                        f"{'  [   ' + TitleChat + '   ]'}\n")

                if att['type'] == 'photo':  # Если прислали фото
                    tb1 += (f"{att['photo']['sizes'][-1]['url']}\n"
                        f"_____________________________________________________")
                    SendTG(node,tb1)
                ###########################################################################################
                elif att['type'] == 'doc':  # Если прислали документ
                    tb1 += (f"{str(att['doc']['url']).replace('no_preview=1', '')}\n"
                        f"_____________________________________________________")
                    SendTG(node,tb1)
                ###########################################################################################
                elif att['type'] == 'video':
                    tb1 += (f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}\n"
                        f"\n_____________________________________________________")
                    SendTG(node,tb1)
                ###########################################################################################
                elif att['type'] == "link":  # Если прислали ссылку(напиример: на историю)
                    tb1 += (f"\n\n{att['link']['url']}"
                        f"\n_____________________________________________________")
                    SendTG(node,tb1)
            ###########################################################################################
                elif att['type'] == 'wall':  # Если поделились постом
                    textbox = textboxFILE = str(f"\n_____________________________________________________\n"
                                  f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}"
                                  f"\n{' [     ' + TitleChat + '     ]' + ' : '} \n поделился постом :\n"
                                  f"\n\n группа: {att['wall']['from']['name']}"
                                  f"\n\n{att['wall']['text']}")
                    textbox += str(f"\n_____________________________________________________")
                    try:
                        for wall_att in att['wall']['attachments']:
                                if wall_att['type'] == 'photo':
                                    bot.send_photo(node,get(f"{wall_att['photo']['sizes'][-1]['url']}").content, textbox)
                                    textboxFILE += str(f"\n{wall_att['photo']['sizes'][-1]['url']}\n")
                                if wall_att['type'] == 'video':
                                    textbox += str(f"\nhttps://vk.com/video{str(wall_att['video']['owner_id'])}_{str(wall_att['video']['id'])}\n")
                                    textboxFILE += str(f"\nhttps://vk.com/video{str(wall_att['video']['owner_id'])}_{str(wall_att['video']['id'])}\n")
                                    bot.send_message(node, textbox)
                                if wall_att['type'] == 'doc':
                                    textbox += str(f"\n{str(wall_att['doc']['url']).replace('no_preview=1', '')}\n")
                                    textboxFILE += str(f"\n{str(wall_att['doc']['url']).replace('no_preview=1', '')}\n")
                                    bot.send_message(node, textbox)
                                if wall_att['type'] == 'link':
                                    textbox += str(f"\n{str(wall_att['link']['url'])}\n")
                                    textboxFILE += str(f"\n{str(wall_att['link']['url'])}\n")
                                    bot.send_message(node, textbox)
                        textboxFILE += str(f"\n_____________________________________________________\n")
                        logging.info(textboxFILE)
                    except:
                            bot.send_message(node,textbox)
                            textboxFILE += str(f"\n_____________________________________________________\n")
                            logging.info(textboxFILE)
        ###########################################################################################
            if resend.object.fwd_messages:
                #try:
                    fwdlist = []
                    ug = []
                    tg = []
                    FwdTextBox = (f"_____________________________________\n"
                                  f"{user1} из чата {resend.object.peer_id  }  \n"
                                  f"\n{' [     ' + TitleChat + '     ]' + ' : '} \n переслал :\n"
                                  f"_____________________________________\n")
                    for fwd in resend.object.fwd_messages:
                        fg = fwd.get('fwd_messages')
                        fwdlist.append(fg)
                        for user in resend.object.fwd_messages:
                            ug = user['from_id']
                        for text in resend.object.fwd_messages:
                            tg = text['text']
                    print(fwdlist)
                    print(f"{ug},' ',{tg}")
                    #fl = [' | ' + str(userg) + ' : ' + str(text) + "\n"]
                    #bot.send_message(node, f"   {fl}\n")
                #except:
                    #bot.send_message(node,(f"Ошибка передачи\n{resend.obj.fwd_messages}"))

        ###########################################################################################
            if  resend.obj.text != "":
                texts = (f"\n{user1 +'( https://vk.com/id' + str(UserId1) + ' ) ' }"
                        f"{' Из чата (' + str(resend.obj.peer_id) + ')'}" 
                        f"\n{'[     ' + TitleChat + '     ]' + ' : '}\n"
                        f"_____________________________________\n"
                        f"\n{resend.object['text']}\n" 
                        f"_____________________________________\n\n")
                SendTG(node,texts)
            elif resend.obj.text == "":
                None

############################ отправка в чат вк из телеги ##################################
def vkNode():
    @bot.message_handler(content_types=['text','video','photo','document','animation','sticker'])
    def TG_VK(message):
        idchat = message.chat.id
        idmessage_start = int(message.message_id)
        msg = message.text
        if idchat in reverse_Nodes():
            node = reverse_Nodes().get(idchat)
            ###########################################################################################
            if message.text:
                idmessage = int(message.message_id) - 1
                if msg and not message.forward_from and not message.forward_sender_name:
                    last_name = message.from_user.last_name
                    if last_name is None: last_name = ''
                    msgtg = str(message.from_user.first_name) + ' ' + last_name + ' : ' + msg
                    vk.messages.send(random_id=idmessage, message=msgtg, peer_id=node)
                if idmessage < idmessage_start:
                    if message.forward_from:
                        time.sleep(1)
                        last_name_fwd = message.forward_from.last_name
                        if msg is None: msg = ''
                        if last_name_fwd is None: last_name_fwd = ''
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
                idphoto = message.photo[2].file_id
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
                    if captiondocument is None: captiondocument = ''
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
                        if sep in types: sepget = types.get(sep)
                        else: sepget = 'test'
                    ###########################################################################################
                        namedocument = iddocument + '.' + sepget
                        write_file(namedocument, bot.download_file((bot.get_file(iddocument)).file_path))
                        mtpsget = mtps.guess_extension(message.document.mime_type)
                        if mtpsget is None: mtpsget = (magic.Magic(mime=True)).from_file(namedocument)
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
                if str((bot.get_file(idsticker)).file_path).split(sep='.')[1] == 'tgs': tgs = '.tgs'
                else: tgs = '.webp'
                namesticker = idsticker + tgs
                write_file(namesticker,bot.download_file((bot.get_file(idsticker)).file_path))
                if tgs == '.webp': convert_img(namesticker,f"{idsticker}.png","png")
                if tgs != '.tgs':
                    os.remove(namesticker)
                    u = upload.document(doc=f"{idsticker}.png", title=str(random.randint(1, 1000000)), group_id=IdGroupVK,to_wall=0)
                    sticker = "doc" + str(u['doc']['owner_id']) + '_' + str(u['doc']['id']) + '?' + str(u['doc']['url']).split(sep='?')[1].replace('&no_preview=1', '')
                    logging.info(f"\n{idsticker}.png\n{sticker}\n")
                    vk.messages.send(random_id=random.randint(0, 999999), message='',peer_id=node, attachment=sticker)
                    os.remove(f"{idsticker}.png")
                else: os.remove(namesticker)
    bot.polling(none_stop=True, interval=0)
