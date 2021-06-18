import vk_api , random, telebot,logging, json,os, magic, lottie
from PIL import Image
import mimetypes as mtps
from requests import get
from vk_api import VkApi
from respondent import new_message_rand , a1
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from CONFIG import idGroupTelegram , IdGroupVK , teletoken , vktokenGroup , Nodes , count_period , command, vktokenUser, \
    types ,pwmess ,CAPTCHA_EVENT

################### Логирование ###########################
file_log = logging.FileHandler('Log.log', 'a', 'utf-8')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)
################ Служебные переменные #####################
i = 0
key = ''
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

upload = vk_api.VkUpload(vk_user)
################################## Блок функций #######################################

def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, member_id=member_id)

def send(msg):
    vk.messages.send(random_id=random.randint(0, 999999), message=msg, peer_id=respondent.object.peer_id)

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
    for mbs in members['items']:
        member = mbs['member_id']
        if member > 0:
            membList.append(member)
    return membList

def RandomMember():
    userID = random.choice((GetMembers()))
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
    for i in d['items']:
        doc = str(i['id'])
        docs.append(doc)
    for doc_ in docs:
        vk_user.docs.delete(owner_id='-'+ str(IdGroupVK),doc_id=doc_)
    send('Удаление завершено')

################################### вк бот ################################################
def vk_bot_respondent():
    global i, respondent , peerID
    for respondent in longpoll.listen():
        ######################################### VK Event ########################################
        TEXT = respondent.object['text']
        peerID = respondent.object['peer_id']
        ############################### Словари из сообщений ######################################
        TextSplitLowerDict = set(str(TEXT).lower().split())
        TextDictSplitLines = set(str(TEXT).lower().splitlines())
        ################################ Команда рандома на *кто...* ##############################
        s = str(TEXT).lower().split(maxsplit=1)
        if len(s) == 2:
            if s[0] == "кто" and s[1] is not None:
                ss = s[0] + ' ' + s[1]
                srs = RandomMember() + ' , ' + s[1]
            else:
                ss = None
                srs = None
        else:
            ss = None
            srs = None
        ################################ Словарь для запрос-ответ #################################
        command_service = {
            '/idchat'       : "ID чата : " + str(peerID), #узнать ID чата
            f"{ss}"  : f"{srs} ", #Команда рандома на *кто...*
        }
        ############################### Обработка ######################################
        if respondent.type == VkBotEventType.MESSAGE_NEW:
            i = i + 1
            ################## Power Electronics Мем ##################
            if a1 & TextSplitLowerDict:
                send(pwmess)
            ################## Выбор значения по ключу из command ##################
            elif TextSplitLowerDict & set(command):
                    for element in TextSplitLowerDict:
                        key = command.get(element)
                        if element in TextSplitLowerDict:
                           if key is not None: send(key)
            ################## Выбор значения по ключу из command_service ##################
            elif TextDictSplitLines & set(command_service):
                    for element1 in TextDictSplitLines:
                        key1 = command_service.get(element1)
                        if element1 in TextDictSplitLines:
                            if key1 is not None: send(key1)

            elif TEXT and i % count_period == 0 :
                send(new_message_rand())
            ###########################################################################################
            elif respondent.object.text in ['кик']:
                try:
                    kick(chat_id=peerID - 2000000000, member_id=respondent.object.reply_message['from_id'])
                except:
                    send("НЕЛЬЗЯ МУДИЛА")

            elif TEXT == '/CABAL:clear_docs=init':
                 clear_docs()
        else:
            None
############################ отправка в чат телеги из вк ##################################

def vk_bot_resend():
    global i, resend
    for resend in longpoll.listen():
        UserId1 = resend.object['from_id']
        user1 = str(getUserName(resend.object.from_id))
        PeerId = resend.object.peer_id
        TitleChat = GET_CHAT_TITLE(PeerId)
        ########################## Распределение точек отправки ###############################
        if PeerId in Nodes:
            node = Nodes.get(PeerId)
        else:
            node = idGroupTelegram
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

                    FwdTextBox = (f"_____________________________________\n"
                                  f"{user1} из чата {resend.object.peer_id  }  \n"
                                  f"\n{' [     ' + TitleChat + '     ]' + ' : '} \n переслал :\n"
                                  f"_____________________________________\n")
                    fwdjson = str(resend.object.fwd_messages)

                    tt1 = json.JSONDecoder().decode(fwdjson)
                    print(tt1)

                    #fl = [' | ' + str(userg) + ' : ' + str(text) + "\n"]
                    #bot.send_message(node, f"   {fl}\n")
                #except:
                    #bot.send_message(node,
                              #(f"Ошибка передачи \n"
                               #f"{resend.obj.fwd_messages}"))

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
        if idchat in reverse_Nodes():
            node = reverse_Nodes().get(idchat)
            ###########################################################################################
            if message.text:
                msgtg = message.text
                vk.messages.send(random_id=random.randint(0, 999999), message=msgtg, peer_id=node)
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
                        u = upload.video(video_file=namedocument, name=iddocument, wallpost=0, is_private=True,group_id=IdGroupVK)
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
                except:
                    SendTG(message.chat.id,'\n⚠⚠⚠ Ошибка загрузки ⚠⚠⚠')
            ###########################################################################################
            if message.sticker:
                idsticker = message.sticker.file_id
                if str((bot.get_file(idsticker)).file_path).split(sep='.')[1] == 'tgs': tgs = '.tgs'
                else: tgs = '.webp'
                namesticker = idsticker + tgs
                write_file(namesticker,bot.download_file((bot.get_file(idsticker)).file_path))
                if tgs == '.webp':
                    ipng = Image.open(namesticker).convert()
                    ipng.save(f"{idsticker}.png", "png")
                #if str(namesticker).split(sep='.')[1] == 'tgs':
                #    fileconv = os.popen(f'lottie_convert.py {namesticker} {idsticker}.gif')
                #    write_file(idsticker+'.gif',fileconv)
                if tgs != '.tgs':
                    os.remove(namesticker)
                    u = upload.document(doc=f"{idsticker}.png", title=str(random.randint(1, 1000000)), group_id=IdGroupVK,to_wall=0)
                    sticker = "doc" + str(u['doc']['owner_id']) + '_' + str(u['doc']['id']) + '?' + str(u['doc']['url']).split(sep='?')[1].replace('&no_preview=1', '')
                    logging.info(f"\n{idsticker}.png\n{sticker}\n")
                    vk.messages.send(random_id=random.randint(0, 999999), message='',peer_id=node, attachment=sticker)
                    os.remove(f"{idsticker}.png")
                else:
                    os.remove(namesticker)
    bot.polling(none_stop=True, interval=0)
