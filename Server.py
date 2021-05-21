import vk_api , random, telebot
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from  vk_api import VkApi
from respondent import new_message_rand
from requests import get
from CONFIG import idGroupTelegram , IdGroupVK , teletoken , vktokenGroup

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
users_list_warn = " @keyn_prorok  "


################### Авторизация ###########################
vk_session: VkApi = vk_api.VkApi(token=vktokenGroup)
longpoll = VkBotLongPoll(vk_session, IdGroupVK)
vk = vk_session.get_api()
bot = telebot.TeleBot(teletoken)

###########################################################################################

def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, member_id=member_id)

def send(msg):
    vk.messages.send(random_id=random.randint(0, 999999), message=msg, peer_id=event.object['peer_id'])

#извлечение имени и фамилии
def getUserName():

        userId = event.object['from_id']
        if 0 < userId < 2000000000:
           username = vk.users.get(user_id=userId)
           first_name = username[0]['first_name']
           last_name = username[0]['last_name']
           user = str(first_name + " " + last_name)
        else:
            None


###########################################################################################

def vk_bot_respondent():
    global hell , event,i
    for event in longpoll.listen():

        NEW = event.type == VkBotEventType.MESSAGE_NEW
        TEXT = event.object['text']
        peerID = event.object['peer_id']



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
                #nameChat = vk.messages.getConversations(title = event.object.title)
                #print(nameChat)

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
        UserId1 = event1.object['from_id']

        if event1.obj.text == 'ping_anclaw':
            vk.messages.send(random_id=random.randint(0, 999999), message="Поток 2 активен", peer_id=event1.obj.peer_id)



        if 0 < UserId1 < 2000000000:
                username = vk.users.get(user_id=UserId1)
                first_name1 = username[0]['first_name']
                last_name1 = username[0]['last_name']
                user1 = str(first_name1 + " " + last_name1)
        else:
            None

        ###########################################################################################
        if UserId1 > 0:
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
                    textbox = textboxFILE = str(f"\n_____________________________________________________\n"
                                  f"{user1 + '  из чата : ' + str(event1.obj.peer_id)} поделился постом"
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
                bot.send_message(idGroupTelegram,
                                 str(f"{user1 +'( https://vk.com/id' + str(UserId1) + ' ) ' }"
                                 f"\n{' Из чата (' + str(event1.obj.peer_id) + ') : '}\n"
                                 f"_____________________________________\n"
                                 f"\n{event1.object['text']}\n" 
                                 f"_____________________________________") )

                logging.info("|" + str(i) +
                             "|  ЧАТ : " + str(event1.obj.peer_id - 2000000000) +
                             "  https://vk.com/id" + str(UserId1) +
                             "  Пользователь: " + str(user1) +
                             "\n_______________________________________________________________________________________\n" +
                             " \n                                   " + str(event1.obj.text) + "\n" +
                             "_______________________________________________________________________________________\n\n\n\n")

            elif event1.obj.text == "":
                None




