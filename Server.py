import vk_api , random, telebot
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from  vk_api import VkApi
from respondent import new_message_rand

################### Логирование ###########################
import logging
file_log = logging.FileHandler('Log.log', 'a', 'utf-8')
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

################ Служебные переменные #####################
i = 0
hell = False
users_list_warn = " @keyn_prorok  @thehardestmistakes @redsettings "

################# API-ключи ###############################
#vktokenGroup="f44cdb58f26da7b43b489931c952026e7027cf9a499fb0edc66758edda65cd938b54bcaec2eaa8e4cb5a1"
teletoken="1778615967:AAFayqQFet_DB6c600_dipj8dgJrH_qhu9Q"
vktokenuser= "7e4cb74c772fb51d51cf9a30b4e4503a0c914c053665d2cabf2289ee8184be2c5fe0ee6ef83ea16a083b9"

################## id групп ###############################
IdGroupVK=204593208
#202960000
idGroupTelegram=-569647443


################### Авторизация ###########################
vk_session: VkApi = vk_api.VkApi(token=vktokenuser)
longpoll = VkBotLongPoll(vk_session, IdGroupVK)
vk = vk_session.get_api()
bot = telebot.TeleBot(teletoken)

###########################################################################################

def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, member_id=member_id)

def send(msg):
    vk.messages.send(random_id=random.randint(0, 999999), message=msg, peer_id=event.object['peer_id'])




###########################################################################################

def vk_bot_respondent():
    global hell , event,i
    for event in longpoll.listen():

        NEW = event.type == VkBotEventType.MESSAGE_NEW
        TEXT = event.object['text']
        peerID = event.object['peer_id']

    # извлечение имени и фамилии
        #if event.object['from_id']:
            #userId = event.object['from_id']
            #if 0 < userId < 2000000000:
                #username = vk.users.get(user_id=userId)
                #first_name = username[0]['first_name']
                #last_name = username[0]['last_name']
                #user = str(first_name + " " + last_name)

        if NEW:
            i = i + 1
            if TEXT == 'хуй':
                send('поцелуй')

            elif TEXT == 'начать':
                send('кончать')

            elif TEXT == 'вкл еблана':
                hell=True
                send('стал ебланом')

            elif TEXT == 'выкл еблана':
                hell=False
                send('все не еблан')

            elif TEXT == 'помощь':
                send('себе помоги инвалид обоссаный')

            elif TEXT and i % 6 == 0 and hell==True:
                send(new_message_rand())

            elif TEXT == 'CABAL:INIT_KILL==TRUE and SYSTEM.WORK == FALSE':
                vk.messages.send(random_id=random.randint(0, 999999), message="ВЫКЛЮЧАЮСЬ", peer_id=2000000001, attachments=[])
                quit()

            elif TEXT == 'IDCHAT':
                send("ID чата : " + str(peerID - 2000000000))
                nameChat = vk.messages.getConversations(title = event.object.title)
                print(nameChat)

            ###########################################################################################
            elif event.object.text in ['кик']:
                try:
                    kick(chat_id=peerID - 2000000000, member_id=event.object.reply_message['from_id'])
                except:
                    send("НЕЛЬЗЯ МУДИЛА")
        else:
            None

###########################################################################################

def vk_bot_resend():

    global i, event1
    for event1 in longpoll.listen():
        if event1.obj.text == 'ping_anclaw':
            vk.messages.send(random_id=random.randint(0, 999999), message="Поток 2 активен", peer_id=event1.obj.peer_id)

        if event1.object['from_id']:
            userId1 = event1.object['from_id']
            if 0 < userId1 < 2000000000:
                username = vk.users.get(user_id=userId1)
                first_name1 = username[0]['first_name']
                last_name1 = username[0]['last_name']
                user1 = str(first_name1 + " " + last_name1)
            else:
                None

        ###########################################################################################
        if userId1 > 0:
            for att in event1.obj.attachments:
                if att['type'] == 'photo':  # Если прислали фото
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(event1.obj.peer_id)}\n"
                        f"{att['photo']['sizes'][-1]['url']}\n"
                        f"_____________________________________________________") )
                    logging.info(f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(event1.obj.peer_id)}\n"
                        f"{att['photo']['sizes'][-1]['url']}\n"
                        f"_____________________________________________________\n\n")

                ###########################################################################################

                elif att['type'] == 'doc':  # Если прислали документ
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(event1.obj.peer_id)}\n"
                        f"{str(att['doc']['url']).replace('no_preview=1', '')}\n"
                        f"_____________________________________________________") )
                    logging.info(f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(event1.obj.peer_id)}\n"
                        f"{str(att['doc']['url']).replace('no_preview=1', '')}\n"
                        f"_____________________________________________________\n\n")

                ###########################################################################################

                elif att['type'] == 'video':
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(event1.obj.peer_id)}\n"
                        f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}\n"
                        f"\n_____________________________________________________"))
                    logging.info(f"\n_____________________________________________________\n"
                      f"{user1 + '  из чата : ' + str(event1.obj.peer_id)}\n"
                      f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}\n"
                      f"_____________________________________________________\n\n")

            ###########################################################################################

                elif att['type'] == 'wall':  # Если поделились постом


                    try:

                        if att['wall']['attachments'][0]['type'] == 'photo': # Если в посте фото
                            bot.send_message(idGroupTelegram,
                                (f"\n_____________________________________________________\n"
                                f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился постом"
                                f"\n\n группа: {att['wall']['from']['name']}"
                                f"\n\n{att['wall']['text']}"
                                f"\n{att['wall']['attachments'][0]['photo']['sizes'][-1]['url']}"
                                f"\n_____________________________________________________") )
                            logging.info(f"\n_____________________________________________________\n"
                                f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился постом"
                                f"\n\n группа: {att['wall']['from']['name']}"
                                f"\n\n{att['wall']['text']}"
                                f"\n{att['wall']['attachments'][0]['photo']['sizes'][-1]['url']}"
                                f"\n_____________________________________________________\n\n")


                        elif att['wall']['attachments'][0]['type'] == "video":  # если в посте видео
                            bot.send_message(idGroupTelegram,
                                (f"\n_____________________________________________________\n"
                                f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился видео"
                                f"\n\n группа: {att['wall']['from']['name']}"
                                f"\n\n{att['wall']['text']}\n\n"
                                f"https://vk.com/video{att['wall']['attachments'][0]['video']['owner_id']}_{att['wall']['attachments'][0]['video']['id']}"
                                f"\n_____________________________________________________") )
                            logging.info(f"\n_____________________________________________________\n"
                                f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился видео"
                                f"\n\n группа: {att['wall']['from']['name']}"
                                f"\n\n{att['wall']['text']}\n\n"
                                f"https://vk.com/video{att['wall']['attachments'][0]['video']['owner_id']}_{att['wall']['attachments'][0]['video']['id']}"
                                f"\n_____________________________________________________\n\n")


                        elif att['wall']['attachments'][0]['type'] == 'doc':  # Если прислали документ
                            bot.send_message(idGroupTelegram,
                                             (f"\n_____________________________________________________\n"
                                              f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился постом\n"
                                              f"\n\n группа: {att['wall']['from']['name']}"
                                              f"\n\n{att['wall']['text']}\n\n"
                                              f"{str(att['wall']['attachments'][0]['doc']['url']).replace('no_preview=1', '')}\n"
                                              f"_____________________________________________________"))
                            logging.info(f"\n_____________________________________________________\n"
                                         f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился постом\n"
                                         f"\n\n группа: {att['wall']['from']['name']}"
                                         f"\n\n{att['wall']['text']}\n\n"
                                         f"{str(att['wall']['attachments'][0]['doc']['url']).replace('no_preview=1', '')}\n"
                                         f"_____________________________________________________\n\n")
                    except:
                        bot.send_message(idGroupTelegram,
                                  (f"\n_____________________________________________________\n"
                                   f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился текстовым постом"
                                   f"\n\n группа: {att['wall']['from']['name']}"
                                   f"\n\n{att['wall']['text']}\n\n"
                                   f"\n_____________________________________________________"))
                        logging.info(f"\n_____________________________________________________\n"
                              f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился текстовым постом"
                              f"\n\n группа: {att['wall']['from']['name']}"
                              f"\n\n{att['wall']['text']}\n\n"
                              f"\n_____________________________________________________\n\n")


            ###########################################################################################

                elif att['type'] == "link":  # Если прислали ссылку(напиример: на историю)
                    bot.send_message(idGroupTelegram,
                        (f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился ссылкой"
                        f"\n\n{att['link']['url']}"
                        f"\n_____________________________________________________"))
                    logging.info((f"\n_____________________________________________________\n"
                        f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился ссылкой"
                        f"\n\n{att['link']['url']}"
                        f"\n_____________________________________________________"))

        ###########################################################################################

            if event1.object.fwd_messages:
                try:
                    print(event1.object.fwd_messages)
                    for fwd in event1.object.fwd_messages:

                        getname = fwd['from_id']
                        if 0 < getname < 2000000000:
                            username1 = vk.users.get(user_id=getname)
                            user2 = str(username1[0]['first_name'] + " " + username1[0]['last_name'])
                            bot.send_message(idGroupTelegram,
                             (   f" {user1} переслал : \n"
                                 f"_____________________________________\n"
                                 f"   {user2 + ' : ' + fwd['text']}\n"
                                 f"_____________________________________"))
                except:
                    bot.send_message(idGroupTelegram,
                              (f"Ошибка передачи \n"
                               f"{event1.obj.fwd_messages}"))

        ###########################################################################################

            if event1.obj.text != 'CABAL:INIT_KILL==TRUE and SYSTEM.WORK == FALSE' and event1.obj.text != "":
                UserId1 = event1.obj['from_id']
                bot.send_message(idGroupTelegram,
                             str(f"{user1 +'( https://vk.com/id' + str(UserId1) + ' ) ' }"
                                 f"\n{' Из чата (' + str(event1.obj.peer_id) + ') : '}\n"
                                 f"_____________________________________\n"
                                 f"\n{event1.object['text']}\n" 
                                 f"_____________________________________") )
                

                if UserId1 > 0:
		   
                    logging.info("|" + 
                             "|  ЧАТ : " + str(event1.obj.peer_id - 2000000000) +
                             "  https://vk.com/id" + str(UserId1) +
                             "  Пользователь: " + str(user1) +
                             "\n_______________________________________________________________________________________\n" +
                             " \n                                   " + str(event1.obj.text) + "\n" +
                             "_______________________________________________________________________________________\n\n\n\n")
                else:
                    None

            elif event1.obj.text == "":
                None




