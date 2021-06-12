import vk_api , random, telebot,logging, json,os
from requests import get
from vk_api import VkApi
from respondent import new_message_rand , a1
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from CONFIG import idGroupTelegram , IdGroupVK , teletoken , vktokenGroup , Nodes , count_period , command, vktokenUser

################### Логирование ###########################
file_log = logging.FileHandler('Log.log', 'a', 'utf-8')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out),
                    format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)
################ Служебные переменные #####################
i = 0
hell = False
################### Авторизация ###########################
#Группа
vk_session: VkApi = vk_api.VkApi(token=vktokenGroup)
vk = vk_session.get_api()
#Пользователь
vk_session_user : VkApi = vk_api.VkApi(token=vktokenUser)
vk_user = vk_session_user.get_api()

longpoll = VkBotLongPoll(vk_session, IdGroupVK)
bot = telebot.TeleBot(teletoken)

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

###########################################################################################
def vk_bot_respondent():
    global hell, i, respondent , peerID
    for respondent in longpoll.listen():
        ######################################### VK Event ########################################
        NEW = respondent.type == VkBotEventType.MESSAGE_NEW
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
            '/idchat'       : "ID чата : " + str(peerID - 2000000000), #узнать ID чата
            f"{ss}"  : f"{srs} " #Команда рандома на *кто...*
        }
        ############################### Обработка ######################################
        if NEW:
            i = i + 1
            ################## Power Electronics Мем ##################
            if a1 & TextSplitLowerDict:
                pwmess = (f"🚯🚯🚯СПИСОК ФАНАТОВ 🚫🚫🚫Сглыпа)🚫🚫🚫 и ХЕЙТЕРОВ 💞💞💞Электроникса💞💞💞/💫❤Пауэр-электроникса❤💫: \n" 
                    f"1. https://vk.com/jido_schweine (МРАЗЬ)  \n" 
                    f"2. https://vk.com/ultima_resolucion (ПРЕДАТЕЛЬ) Электроникса, ЕРЕТИК\n" 
                    f"3. https://vk.com/estenatu (СГЛЫПСКАЯ ПОДСТИЛКА), бывшая Хранительница Электроникса, теперь в прислуге у 🚫🚫🚫Сглыпа)🚫🚫🚫\n" 
                    f"4. https://vk.com/keyn_prorok (ЛИЦЕМЕР), БАЛАБОЛ, ПРЕДАТЕЛЬ ЭЛЕКТРОНИКСА 'ДЭТ ИНДАСТРИАЛ' поклонник - ЕРЕТИК.\n" )
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
        else:
            None
        print(respondent)
###########################################################################################
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
################################### пишем в чат вк прмо из телеги #####################
def vkNode():
    @bot.message_handler(content_types=['text','video','photo'])
    def TG_VK(message):
        print(f"{message}\n")
        idchat = message.chat.id
        if idchat in reverse_Nodes():
            node = reverse_Nodes().get(idchat)
            if message.text:
                msg = message.text
                vk.messages.send(random_id=random.randint(0, 999999), message=msg, peer_id=node)
            if message.video:
                idvideo = message.video.file_id
                filevideo = bot.get_file(idvideo)
                captionvideo = message.caption
                name = idvideo + '.mp4'
                down = bot.download_file(filevideo.file_path)
                # link = f"https://api.telegram.org/file/bot{teletoken}/{filevideo.file_path}"
                with open(name, 'bw')as f:
                    f.write(down)
                u = upload.video(video_file=name,name=idvideo,wallpost=0,is_private=True,group_id=IdGroupVK)
                vidos = "video"+str(u['owner_id']) + '_' + str(u['video_id']) + "?list=" + str(u['access_key'])
                vk.messages.send(random_id=random.randint(0, 999999), message=captionvideo, peer_id=node,attachment=vidos)
                print(f"\n{vidos}\n")
                os.remove(name)
            if message.photo:
                idphoto = message.photo[2].file_id
                filephoto = bot.get_file(idphoto)
                captionphoto = message.caption
                namephoto = idphoto + '.jpg'
                download = bot.download_file(filephoto.file_path)
                with open(namephoto,'bw') as f:
                    f.write(download)
                u = upload.photo_messages(photos=namephoto,peer_id=node)[0]
                photo = "photo" + str(u['owner_id']) + '_' + str(u['id']) + "_" + str(u['access_key'])
                vk.messages.send(random_id=random.randint(0, 999999), message=captionphoto, peer_id=node, attachment=photo)
                print(f"\n{photo}\n")
                os.remove(namephoto)
    bot.polling(none_stop=True, interval=0)
