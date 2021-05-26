import vk_api , random, telebot,logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkApi
from respondent import new_message_rand , a1
from requests import get
from CONFIG import idGroupTelegram , IdGroupVK , teletoken , vktokenGroup

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
vk_session: VkApi = vk_api.VkApi(token=vktokenGroup)
longpoll = VkBotLongPoll(vk_session, IdGroupVK)
vk = vk_session.get_api()
bot = telebot.TeleBot(teletoken)

################################## Блок функций #######################################

def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, member_id=member_id)

def send(msg):
    vk.messages.send(random_id=random.randint(0, 999999), message=msg, peer_id=respondent.object.peer_id)

def getUserName(): #извлечение имени и фамилии

        userId = respondent.object.from_id
        if 0 < userId < 2000000000:
           username = vk.users.get(user_id=userId)
           first_name = username[0]['first_name']
           last_name = username[0]['last_name']
           user = str(first_name + " " + last_name)
           return user
        else:
            None

def GetMembers():
    members = vk.messages.getConversationMembers(peer_id=respondent.object.peer_id,group_id=IdGroupVK)
    membList = []
    for mbs in members['items']:
        member = mbs['member_id']
        if member > 0:
            membList.append(member)
    return membList

def RandomMember():
        randMember = '@id' + str(random.choice((GetMembers())))
        return randMember

###########################################################################################

def vk_bot_respondent():
    global hell, i, respondent , peerID, ss, srs
    for respondent in longpoll.listen():

        ######################################### VK Event ########################################
        NEW = respondent.type == VkBotEventType.MESSAGE_NEW
        TEXT = respondent.object['text']
        peerID = respondent.object['peer_id']

        ############################### Словари из сообщений ######################################
        TextSplitLowerDict = set(str(TEXT).lower().split())
        TextDictSplitLines = set(str(TEXT).lower().splitlines())

        ############################### Команда рандома на *кто...* ###############################

        s = str(TEXT).lower().split(maxsplit=1)
        if len(s) == 2:
            if s[0]=="кто" and s[1]is not None:
                ss = s[0] + ' ' + s[1]
                srs = RandomMember()  + ' , ' + s[1]
            else:
                ss = None
                srs = None
        else:
            ss = None
            srs = None

        ################################# Словарь для слово-ответ ################################№
        command = {
            'хуй': 'поцелуй',
            'начать': 'кончать',
            'помощь': 'себе помоги инвалид обоссаный',
        }

        ################################ Словарь для запрос-ответ #################################
        command_service = {
            'IDCHAT': "ID чата : " + str(peerID - 2000000000),
            f"{ss}" : f"{srs} "
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


            elif TEXT and i % 6 == 0 :
                send(new_message_rand())

            ###########################################################################################
            elif respondent.object.text in ['кик']:
                try:
                    kick(chat_id=peerID - 2000000000, member_id=respondent.object.reply_message['from_id'])
                except:
                    send("НЕЛЬЗЯ МУДИЛА")
        else:
            None


###########################################################################################

def vk_bot_resend():

    global i, resend
    for resend in longpoll.listen():
        UserId1 = resend.object['from_id']

        if resend.obj.text == 'ping_anclaw':
            vk.messages.send(random_id=random.randint(0, 999999), message="Поток 2 активен", peer_id=resend.obj.peer_id)

        if 0 < UserId1 < 2000000000:
                username = vk.users.get(user_id=UserId1)
                first_name1 = username[0]['first_name']
                last_name1 = username[0]['last_name']
                user1 = str(first_name1 + " " + last_name1)
        else:
            None

        ###########################################################################################
        if UserId1 > 0:
            for att in resend.obj.attachments:
                if att['type'] == 'photo':  # Если прислали фото
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}\n"
                        f"{att['photo']['sizes'][-1]['url']}\n"
                        f"_____________________________________________________") )
                    logging.info(f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}\n"
                        f"{att['photo']['sizes'][-1]['url']}\n"
                        f"_____________________________________________________\n\n")

                ###########################################################################################

                elif att['type'] == 'doc':  # Если прислали документ
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}\n"
                        f"{str(att['doc']['url']).replace('no_preview=1', '')}\n"
                        f"_____________________________________________________") )
                    logging.info(f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}\n"
                        f"{str(att['doc']['url']).replace('no_preview=1', '')}\n"
                        f"_____________________________________________________\n\n")

                ###########################################################################################

                elif att['type'] == 'video':
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}\n"
                        f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}\n"
                        f"\n_____________________________________________________"))
                    logging.info(f"\n_____________________________________________________\n"
                      f"{user1 + '  из чата : ' + str(resend.obj.peer_id)}\n"
                      f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}\n"
                      f"_____________________________________________________\n\n")

            ###########################################################################################

                elif att['type'] == 'wall':  # Если поделились постом
                    textbox = textboxFILE = str(f"\n_____________________________________________________\n"
                                  f"{user1 + '  из чата : ' + str(resend.obj.peer_id)} поделился постом"
                                  f"\n\n группа: {att['wall']['from']['name']}"
                                  f"\n\n{att['wall']['text']}")
                    textbox += str(f"\n_____________________________________________________")
                    try:
                        for wall_att in att['wall']['attachments']:
                                if wall_att['type'] == 'photo':
                                    bot.send_photo(idGroupTelegram,get(f"{wall_att['photo']['sizes'][-1]['url']}").content, textbox)
                                    textboxFILE += str(f"\n{wall_att['photo']['sizes'][-1]['url']}\n")
                                if wall_att['type'] == 'video':
                                    textbox += str(f"\nhttps://vk.com/video{str(wall_att['video']['owner_id'])}_{str(wall_att['video']['id'])}\n")
                                    textboxFILE += str(f"\nhttps://vk.com/video{str(wall_att['video']['owner_id'])}_{str(wall_att['video']['id'])}\n")
                                    bot.send_message(idGroupTelegram, textbox)

                                if wall_att['type'] == 'doc':
                                    textbox += str(f"\n{str(wall_att['doc']['url']).replace('no_preview=1', '')}\n")
                                    textboxFILE += str(f"\n{str(wall_att['doc']['url']).replace('no_preview=1', '')}\n")
                                    bot.send_message(idGroupTelegram, textbox)
                                if wall_att['type'] == 'link':
                                    textbox += str(f"\n{str(wall_att['link']['url'])}\n")
                                    textboxFILE += str(f"\n{str(wall_att['link']['url'])}\n")
                                    bot.send_message(idGroupTelegram, textbox)
                        textboxFILE += str(f"\n_____________________________________________________\n")
                        logging.info(textboxFILE)
                    except:
                            bot.send_message(idGroupTelegram,textbox)
                            textboxFILE += str(f"\n_____________________________________________________\n")
                            logging.info(textboxFILE)




            ###########################################################################################

                elif att['type'] == "link":  # Если прислали ссылку(напиример: на историю)
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)} поделился ссылкой"
                        f"\n\n{att['link']['url']}"
                        f"\n_____________________________________________________"))
                    logging.info((f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(resend.obj.peer_id)} поделился ссылкой"
                        f"\n\n{att['link']['url']}"
                        f"\n_____________________________________________________"))

        ###########################################################################################

            if resend.object.fwd_messages:
                try:

                    FwdTextBox = (f"_____________________________________\n"
                                  f"{user1} из чата {resend.object.peer_id} переслал : \n"
                                  f"_____________________________________\n")
                    for fwd in resend.object.fwd_messages:
                        getname = fwd['from_id']
                        if 0 < getname < 2000000000:
                            username_ = vk.users.get(user_id=getname)
                            user_ = str(username_[0]['first_name'] + " " + username_[0]['last_name'])
                        else:
                            user_ = "БОТ"
                        FwdTextBox += ' | ' + user_ + ' : ' + fwd['text']  + "\n"
                    FwdTextBox += f"_____________________________________\n"
                    bot.send_message(idGroupTelegram, f"   {FwdTextBox}\n")
                except:
                    bot.send_message(idGroupTelegram,
                              (f"Ошибка передачи \n"
                               f"{resend.obj.fwd_messages}"))

        ###########################################################################################

            if resend.obj.text != 'CABAL:INIT_KILL==TRUE and SYSTEM.WORK == FALSE' and resend.obj.text != "":
                bot.send_message(idGroupTelegram,
                                 str(f"{user1 +'( https://vk.com/id' + str(UserId1) + ' ) ' }"
                                 f"\n{' Из чата (' + str(resend.obj.peer_id) + ') : '}\n"
                                 f"_____________________________________\n"
                                 f"\n{resend.object['text']}\n" 
                                 f"_____________________________________") )

                logging.info("|" + str(i) +
                             "|  ЧАТ : " + str(resend.obj.peer_id - 2000000000) +
                             "  https://vk.com/id" + str(UserId1) +
                             "  Пользователь: " + str(user1) +
                             "\n_______________________________________________________________________________________\n" +
                             " \n                                   " + str(resend.obj.text) + "\n" +
                             "_______________________________________________________________________________________\n\n\n\n")

            elif resend.obj.text == "":
                None




