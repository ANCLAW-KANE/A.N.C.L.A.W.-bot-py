import random, os,  time, sqlite3
from tools import  write_file_json, read_file_json, json_gen
from online_tools import send_to_specific_peer,SendTGtoVK,get_online
from resend_parser import parse_resend
from respondent_func import WHO, COMMAND, privileges
from sessions import longpoll, vk, bot, longpoll_full
from vk_api.bot_longpoll import VkBotEventType
from CONFIG import config_file_json

################################### вк бот ################################################
def vk_bot_respondent():
    i = 0
    global respondent, who
    if not os.path.isfile(config_file_json):
        write_file_json(config_file_json, json_gen().return_json())
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    edit.execute(f"""CREATE TABLE IF NOT EXISTS peers( peer_id INT PRIMARY KEY,e_g_mute TEXT,count_period INT,
                    e_g_head TEXT,e_g_ex TEXT,resend INT);""")
    edit.execute("""CREATE TABLE IF NOT EXISTS nodes( peer_id INT PRIMARY KEY, tg_id INT, vk_tg_allow INT, tg_vk_allow INT); """)
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
                MESSAGE = respondent.object.message
                TEXT = MESSAGE['text']
                peerID = MESSAGE['peer_id']
                from_id = MESSAGE['from_id']
                lines = str(TEXT).lower().splitlines()
                TextSplitLowerDict = set('')
                if lines: TextSplitLowerDict = set(lines[0].split())
                Dictwords = []
                ######################################### DB ########################################
                # Стандартные настройки чатов
                data = (peerID, '0', 0 ,'0','0',1)
                ####index: 0     1   2   3   4  5
                edit.execute("INSERT OR IGNORE INTO peers VALUES(?,?,?,?,?,?)", data)
                BD.commit()

                # Частота рандомных ответов
                edit.execute(f"SELECT * FROM peers WHERE peer_id = {peerID}")
                count_period = int(edit.fetchone()[2])

                # Шаблонные ответы
                edit_word.execute(
                    f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT, key TEXT PRIMARY KEY, val TEXT);")
                BDWORDS.commit()
                edit_word.execute(f"SELECT key,val FROM '{peerID}' ")
                words = edit_word.fetchall()
                for word in words:
                    Dictwords.append(word[0])

                # ролевые команды
                edit_roles.execute(
                    f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT PRIMARY KEY, command TEXT ,emoji_1 TEXT, txt TEXT, emoji_2 TEXT);")

                # Рандомные высказывания бота
                edit_quotes.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT PRIMARY KEY, quote TEXT);")
                BDQUOTES.commit()
                edit_quotes.execute(f"SELECT quote FROM '{peerID}'")
                quotes = edit_quotes.fetchall()
                ################################ Словари для запрос-ответ #################################
                prefix = {
                    '*': privileges(TEXT, from_id, peerID, MESSAGE).check(),
                    '!': WHO(TEXT, from_id, peerID).WHO_GET(),
                    '/': COMMAND(TEXT, from_id, peerID, MESSAGE).check()
                }
                ############################### Обработка ######################################
                if TEXT is not '':
                    privileges(TEXT, from_id, peerID, MESSAGE).EVIL_GOD()
                    if str(TEXT)[0] != '/' or '*' or '!':
                        dw = dict(words)
                        if set(lines) & set(Dictwords):
                            for element in lines:
                                key = dw.get(element)
                                if key is not None: send_to_specific_peer(key, peerID)
                        elif TextSplitLowerDict & set(Dictwords):
                            for element in TextSplitLowerDict:
                                key = dw.get(element)
                                if key is not None: send_to_specific_peer(key, peerID)
                    if TEXT[0] in prefix:
                        key1 = prefix.get(TEXT[0])
                        if key1 is not None: key1()

                if count_period != 0 and TEXT and \
                        i % count_period == 0 and quotes != []:  send_to_specific_peer(random.choice(quotes), peerID)
            ###########################################################################################
        except Exception as e:
            send_to_specific_peer(f"{e}", respondent.object.message['peer_id'])

############################ отправка в чат телеги из вк ##################################
def vk_bot_resend():
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    for resend in longpoll_full.listen():
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
            vk.messages.send(random_id=0, message=f"{e}", peer_id=resend.object.message['peer_id'])

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
            node = None
            if peer is not None: node = peer[0]
            if node is not None: bot.send_message(message.chat.id, get_online(node))
            else: bot.send_message(message.chat.id, "Этот чат не имеет привязки к вк чату")

        @bot.message_handler(content_types=['text', 'video', 'photo', 'document', 'animation', 'sticker', 'audio'])
        def TG_VK(message):
            #print(message)
            BD = sqlite3.connect('peers.db')
            edit = BD.cursor()
            edit.execute(f"SELECT peer_id, tg_vk_allow FROM nodes WHERE tg_id = {message.chat.id}")
            peer = edit.fetchone()
            if peer is not None:
                time.sleep(1)
                if peer[0] is not None and peer[1] == 1: SendTGtoVK(message,peer[0]).upload_vk()
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            vk.messages.send(random_id=0, message=f"{e}", peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])
            pass