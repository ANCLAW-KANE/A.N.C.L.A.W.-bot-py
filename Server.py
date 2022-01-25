import random, os,  time, sqlite3 , traceback,requests
from telebot.types import InputMediaDocument
from tools import  write_file_json, read_file_json, json_gen,logger
from online_tools import send_to_specific_peer,get_online
from resend_function import SendTGtoVK
from resend_parser import parse_resend
from respond_func import COMMAND
from respond_priv import privileges
from respond_who import WHO
from sessions import longpoll, vk, bot, longpoll_full,file_log,teletoken
from vk_api.bot_longpoll import VkBotEventType
from CONFIG import config_file_json
from keyboards import keyboard_event
################################### вк бот ################################################
def vk_bot_respondent():
    if not os.path.isfile(config_file_json):
        write_file_json(config_file_json, json_gen().return_json())
    for z in file_log:
        if not os.path.isfile(z):
            f = open(z, 'w+')
            f.write("")
            f.close()

    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    edit.execute(f"""CREATE TABLE IF NOT EXISTS peers( peer_id INT PRIMARY KEY,e_g_mute TEXT,count_period INT,
                     e_g_head TEXT,e_g_ex TEXT,resend INT, poligam_marry INT);""")
    edit.execute("""CREATE TABLE IF NOT EXISTS nodes( peer_id INT PRIMARY KEY, tg_id INT, vk_tg_allow INT, 
                    tg_vk_allow INT); """)
    edit.execute("""CREATE TABLE IF NOT EXISTS params_info( param TEXT PRIMARY KEY, info TEXT); """)
    edit.execute("""CREATE TABLE IF NOT EXISTS marry(id INT PRIMARY KEY ,peer_id INT , man1 INT,man2 INT,
        man1name TEXT,man2name TEXT,allow INT,await INT); """)
    for e in read_file_json(config_file_json): edit.execute(f"INSERT OR IGNORE INTO params_info VALUES('{e}','')")
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
            if respondent.type == VkBotEventType.MESSAGE_EVENT:
                OBJ = respondent.object
                payload = OBJ.get('payload', False)
                if payload:
                    payload = str(payload).replace("'",'"')
                    keyboard_event(payload, OBJ).check()
            if respondent.type == VkBotEventType.MESSAGE_NEW:
                r = random.randint(0,100)
                Dictwords = []
                TextSplitLowerDict = set('')
                ######################################### VK Event ########################################
                #print(respondent.object)
                MESSAGE = respondent.object.message
                TEXT = MESSAGE['text']
                peerID = MESSAGE['peer_id']
                from_id = MESSAGE['from_id']
                payload = MESSAGE.get('payload', False)
                lines = str(TEXT).lower().splitlines()
                if lines: TextSplitLowerDict = set(lines[0].split())
                ######################################### DB ########################################
                # Стандартные настройки чатов
                ####index: 0     1   2   3   4  5 6
                data = (peerID, '0', 0 ,'0','0',1,1)
                edit.execute("INSERT OR IGNORE INTO peers VALUES(?,?,?,?,?,?,?)", data)
                BD.commit()
                ################# Частота рандомных ответов
                edit.execute(f"SELECT * FROM peers WHERE peer_id = {peerID}")
                count_period = int(edit.fetchone()[2])

                ################# Шаблонные ответы
                edit_word.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT, key TEXT PRIMARY KEY, val TEXT);")
                BDWORDS.commit()
                edit_word.execute(f"SELECT key,val FROM '{peerID}' ")
                words = edit_word.fetchall()
                for word in words: Dictwords.append(word[0])
                ################# ролевые команды
                edit_roles.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT, command TEXT UNIQUE,"
                            f"emoji_1 TEXT, txt TEXT, emoji_2 TEXT, CONSTRAINT  new_pk  PRIMARY KEY (id, command));")
                ################# Рандомные высказывания бота
                edit_quotes.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT PRIMARY KEY, quote TEXT);")
                BDQUOTES.commit()
                edit_quotes.execute(f"SELECT quote FROM '{peerID}'")
                quotes = edit_quotes.fetchall()
    ######################################## Блок классов команд ######################################################
                prefix = {
                    '/': COMMAND(TEXT, from_id, peerID, MESSAGE).check,
                    '!': WHO( from_id, peerID,TEXT,MESSAGE).WHO_GET,
                    '*': privileges(TEXT, from_id, peerID, MESSAGE).check
                }
        ######################################### Обработка ######################################
                if TEXT is not '':
                    privileges(TEXT, from_id, peerID, MESSAGE).EVIL_GOD()
                    if payload: keyboard_event(payload,MESSAGE).check()
                    if str(TEXT)[0] not in prefix:
                        dw = dict(words)
                        ####################################################################
                        if set(lines) & set(Dictwords):
                            for element in lines:
                                key = dw.get(element)
                                if key is not None: send_to_specific_peer(key, peerID)
                        ####################################################################
                        elif TextSplitLowerDict & set(Dictwords):
                            for element in TextSplitLowerDict:
                                key = dw.get(element)
                                if key is not None: send_to_specific_peer(key, peerID)
                    #####################################################################################
                    if TEXT[0] in prefix:
                        key = prefix.get(TEXT[0])
                        if key is not None: key()
                if r < count_period and quotes:  send_to_specific_peer(random.choice(quotes), peerID)
            ###########################################################################################
        except Exception as e:
            logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n","ERROR.log")
            send_to_specific_peer(f"WARNING : {json_gen().return_config_file_json()['users_list_warn']}\n\n"
                                  f"{e}", respondent.object.message['peer_id'])

############################ отправка в чат телеги из вк ##################################
def vk_bot_resend():
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    for resend in  longpoll_full.listen():
        try:
            ################################## Обработчик #########################################
            if resend.type == VkBotEventType.MESSAGE_NEW:
                UserId = resend.object.message['from_id']
                PeerId = resend.object.message['peer_id']
                ########################## Распределение точек отправки ###############################
                edit.execute(f"SELECT tg_id , vk_tg_allow FROM nodes WHERE peer_id = {PeerId}")
                tg_id = edit.fetchone()
                edit.execute(f"SELECT resend FROM peers WHERE peer_id = {PeerId}")
                global_allow = edit.fetchone()[0]
                if tg_id is not None:
                    node = tg_id[0]
                    allow = tg_id[1]
                else:
                    node = json_gen().return_config_file_json()['idGroupTelegram']
                    allow = global_allow
                #######################################################################################
                if allow == 1 and UserId > 0: parse_resend(node,resend.object.message,PeerId,UserId).sender()
        except Exception as e:
            logger(f"\n________________________\n{traceback.format_exc()}"
                   f"\n________________________\n\n\n", "ERROR.log")
            vk.messages.send(random_id=0, message=f"WARNING : "
                        f"{json_gen().return_config_file_json()['users_list_warn']}"
                        f"\n\n{e}", peer_id=resend.object.message['peer_id'])

############################ отправка в чат вк из телеги ##################################
def vkNode():
    @bot.message_handler(commands=['id'])
    def show_id(message):
        bot.send_message(message.chat.id, message.chat.id)

    @bot.message_handler(commands=['online'])
    def show_online(message):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT peer_id  FROM nodes WHERE tg_id = {message.chat.id}")
        peer = edit.fetchone()
        BD.close()
        node = None
        if peer is not None: node = peer[0]
        if node is not None: bot.send_message(message.chat.id, get_online(node))
        else: bot.send_message(message.chat.id, "Этот чат не имеет привязки к вк чату")

    @bot.message_handler(commands=['log'])
    def log_down(message):
        media_group = []
        for f in file_log: media_group.append(InputMediaDocument(media=open(f,"rb")))
        bot.send_media_group(message.chat.id,media_group)

    @bot.message_handler(content_types=['text', 'video', 'photo', 'document', 'animation', 'sticker', 'audio'])
    def TG_VK(message):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT peer_id, tg_vk_allow FROM nodes WHERE tg_id = {message.chat.id}")
        peer = edit.fetchone()
        BD.close()
        if peer is not None:
            time.sleep(1)
            if peer[0] is not None and peer[1] == 1: SendTGtoVK(message,peer[0]).upload_vk()

    try: bot.polling(none_stop=True,timeout=40,long_polling_timeout=40)
    except Exception as e:
        vk.messages.send(random_id=0,message=f"WARNING: {json_gen().return_config_file_json()['users_list_warn']}"
                                    f"\n\n{e}",peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])
        logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
        pass
