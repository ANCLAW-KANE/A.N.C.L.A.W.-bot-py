import json
import random
import traceback
import aiosqlite
from loguru import logger

from vkbottle.bot import Message , BotLabeler

from keyboards import keyboard_event
from online_tools import send
from handlers.respond_priv import privileges
from sessions import api_group
from tools import json_config, data_msg
from hadlers_rules import MessageNotCommandRule

labeler = BotLabeler()

@labeler.message(MessageNotCommandRule(), blocking=False)
async def bot(msg: Message):
    logger.log("STATE","\n_________________________MSG_________________________")
    #print(msg)
    BD = await aiosqlite.connect('peers.db')
    edit = await BD.cursor()
    BDWORDS = await aiosqlite.connect('peers_words.db')
    edit_word = await BDWORDS.cursor()
    BDROLES = await aiosqlite.connect('peers_roles.db')
    edit_roles = await BDROLES.cursor()
    BDQUOTES = await aiosqlite.connect('peers_quotes.db')
    edit_quotes = await BDQUOTES.cursor()
    try:
        Dictwords = []
        w = []
        TextSplitLowerDict = set('')
        TEXT = msg.text
        peerID = msg.peer_id
        lines = str(TEXT).lower().splitlines()
        if lines: TextSplitLowerDict = set(lines[0].split())
        ######################################### DB ########################################

            ################################## CREATE ##################################
        # Стандартные настройки чатов                     index:    0     1  2  3  4  5  6
        await edit.execute(f"INSERT OR IGNORE INTO peers VALUES({peerID}, 0, 0, 0, 0, 1, 1)")
        await edit_word.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT, key TEXT PRIMARY KEY, val TEXT);")
        # ролевые команды
        await edit_roles.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT, command TEXT UNIQUE,"
            f"emoji_1 TEXT, txt TEXT, emoji_2 TEXT, CONSTRAINT  new_pk  PRIMARY KEY (id, command));")
        # Рандомные высказывания бота
        await edit_quotes.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT PRIMARY KEY, quote TEXT);")
        await BD.commit()
        await BDWORDS.commit()
        await BDROLES.commit()
        await BDQUOTES.commit()

            ################################## SELECT ##################################
        ### Частота рандомных ответов
        await edit.execute(f"SELECT * FROM peers WHERE peer_id = {peerID}")
        count_period = int((await edit.fetchone())[2])
        ### Шаблонные ответы
        await edit_word.execute(f"SELECT key,val FROM '{peerID}' ")
        words = await edit_word.fetchall()
        #print(words, type(words))
        for word in words: Dictwords.append(word[0])  
        ### Рандомные высказывания бота
        await edit_quotes.execute(f"SELECT quote FROM '{peerID}'")
        quotes = await edit_quotes.fetchall()
        ######################################### Обработка ######################################
        if TEXT != '':
            # if FSM(from_id, peerID).check_state() != None: send_to_specific_peer(c, peerID)
            if msg.payload: await keyboard_event(json.loads(msg.payload), msg).check_event_msg()
            await privileges(txt=TEXT, sender=msg.from_id, peer=peerID, obj=msg).EVIL_GOD()
            if MessageNotCommandRule:#исправить
                print(1111111111111111111111111111111111111111111111111)
                dw = dict(words)
                #print(dw)
                ####################################################################
                if set(lines) & set(Dictwords):
                    for element in lines:
                        e = dw.get(element)
                        if e is not None:
                            w.append(e)
                    print(w)
                    data_msg.msg = random.choice(w)
                elif TextSplitLowerDict & set(Dictwords):
                    for element in TextSplitLowerDict:
                        e = dw.get(element)
                        if e is not None:
                            w.append(e)
                    print(w)
                    data_msg.msg = random.choice(w)
                elif random.randint(0, 100) < count_period and quotes:
                    data_msg.msg = random.choice(quotes)[0]
            print(data_msg.msg)
            #####################################################################################
            await send(msg)

    ###########################################################################################
    except Exception as ex:
        #logger(
        #    f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
        await api_group.messages.send(message=f"WARNING : {json_config().cfg_json()['users_list_warn']}\n\n"
                                              f"{ex} \n {msg.peer_id} \n {traceback.format_exc()}",
                                      peer_id=json_config().cfg_json()['PEER_CRUSH_EVENT'], random_id=0)