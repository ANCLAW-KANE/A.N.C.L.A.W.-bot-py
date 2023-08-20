import json
import os
import random
import traceback
import tracemalloc
import loguru
import aiosqlite

from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

from CONFIG import config_file_json
from keyboards import keyboard_event
from online_tools import getUserName
from respond_func import COMMAND
from respond_priv import privileges
from respond_who import WHO
from sessions import file_log, vb, api_group
from tools import write_file_json, read_file_json, json_config, logger, data_msg

################################################################################################

# try:
# except ImportError as e:
#    subprocess.check_call([sys.executable, "-m", "pip", "install", e.name])
######################################### log #########################################
aiosqlite.core.LOG.disabled = True
tracemalloc.start()


#######################################################################################

async def start_create():
    if not os.path.isfile(config_file_json):
        write_file_json(config_file_json, json_config().return_json())
    for z in file_log:
        if not os.path.isfile(z):
            f = open(z, 'w+')
            f.write("")
            f.close()
    BD = await aiosqlite.connect('peers.db')
    await (await aiosqlite.connect('peers_words.db')).commit()
    await (await aiosqlite.connect('peers_roles.db')).commit()
    await (await aiosqlite.connect('peers_quotes.db')).commit()
    edit = await BD.cursor()
    await edit.executescript(
        f"CREATE TABLE IF NOT EXISTS peers( peer_id INT PRIMARY KEY,e_g_mute TEXT,count_period INT,"
        f"e_g_head TEXT,e_g_ex TEXT,resend INT,poligam_marry INT);"
        f"CREATE TABLE IF NOT EXISTS nodes(peer_id INT PRIMARY KEY,tg_id INT,vk_tg_allow INT, tg_vk_allow INT);"
        f"CREATE TABLE IF NOT EXISTS params_info(param TEXT PRIMARY KEY, info TEXT);"
        f"CREATE TABLE IF NOT EXISTS marry(id INT PRIMARY KEY ,peer_id INT , man1 INT,man2 INT,man1name TEXT,"
        f"man2name TEXT,allow INT,await INT);")
    for e in read_file_json(config_file_json):
        await edit.execute(f"INSERT OR IGNORE INTO params_info VALUES('{e}','')")
    await BD.commit()


@vb.loop_wrapper.interval(hours=3)
async def marry_fix():
    BD = await aiosqlite.connect('peers.db')
    edit = await BD.cursor()
    ids = await(await edit.execute(f"SELECT man1 ,man2 from marry")).fetchall()
    users = []
    for i in ids:
        for a in range(0, 1):
            if i[a] not in users:
                users.append(i[a])
    for z in users:
        user = await getUserName(z)
        await edit.executescript(
            f'UPDATE marry SET man1name = "{user}" where man1 = {z};'
            f'UPDATE marry SET man2name = "{user}" where man2 = {z}')
        await BD.commit()
    await edit.execute(f"DELETE FROM marry where man1name = 'None' or man2name = 'None'")
    await BD.close()


vb.loop_wrapper.on_startup.append(start_create())


@vb.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def bot_event(ev: MessageEvent):
    # print('EVENT ::: ', ev)
    data_msg()
    await keyboard_event(ev.payload, ev).check_Callback()
    if data_msg.msg is not None:
        await ev.send_message(f"{data_msg.msg}")


@vb.on.message()
async def bot(msg: Message):
    BD = await aiosqlite.connect('peers.db')
    edit = await BD.cursor()
    BDWORDS = await aiosqlite.connect('peers_words.db')
    edit_word = await BDWORDS.cursor()
    BDROLES = await aiosqlite.connect('peers_roles.db')
    edit_roles = await BDROLES.cursor()
    BDQUOTES = await aiosqlite.connect('peers_quotes.db')
    edit_quotes = await BDQUOTES.cursor()
    try:
        r = random.randint(0, 100)
        data_msg()
        Dictwords = []
        w = []
        TextSplitLowerDict = set('')
        ######################################### VK Event ########################################
        TEXT = msg.text
        peerID = msg.peer_id
        from_id = msg.from_id
        lines = str(TEXT).lower().splitlines()
        if lines:
            TextSplitLowerDict = set(lines[0].split())
        ######################################### DB ########################################
        # Стандартные настройки чатов                     index:    0     1  2  3  4  5  6
        await edit.execute(f"INSERT OR IGNORE INTO peers VALUES({peerID}, 0, 0, 0, 0, 1, 1)")
        await BD.commit()
        # Частота рандомных ответов
        await edit.execute(f"SELECT * FROM peers WHERE peer_id = {peerID}")
        count_period = int((await edit.fetchone())[2])
        # Шаблонные ответы
        await edit_word.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT, key TEXT PRIMARY KEY, val TEXT);")
        await BDWORDS.commit()
        await edit_word.execute(f"SELECT key,val FROM '{peerID}' ")
        words = await edit_word.fetchall()
        print(words, type(words))
        for word in words:
            Dictwords.append(word[0])
        # ролевые команды
        await edit_roles.execute(
            f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT, command TEXT UNIQUE,"
            f"emoji_1 TEXT, txt TEXT, emoji_2 TEXT, CONSTRAINT  new_pk  PRIMARY KEY (id, command));")
        # Рандомные высказывания бота
        await edit_quotes.execute(f"CREATE TABLE IF NOT EXISTS '{peerID}' ( id INT PRIMARY KEY, quote TEXT);")
        await BDQUOTES.commit()
        await edit_quotes.execute(f"SELECT quote FROM '{peerID}'")
        quotes = await edit_quotes.fetchall()
        ######################################## Блок классов команд #############################
        prefix = {
            '/': COMMAND(TEXT=TEXT, _FROM=from_id, PEER=peerID, OBJ=msg).check,
            '!': WHO(fromid=from_id, peer=peerID, msg=TEXT, obj=msg).WHO_GET,
            '*': privileges(txt=TEXT, sender=from_id, peer=peerID, obj=msg).check
        }
        ######################################### Обработка ######################################
        if TEXT != '':
            await msg.answer(message="хуемем")
            # if FSM(from_id, peerID).check_state() != None: send_to_specific_peer(c, peerID)
            await privileges(txt=TEXT, sender=from_id, peer=peerID, obj=msg).EVIL_GOD()
            if msg.payload:
                await keyboard_event(json.loads(msg.payload), msg).check_event_msg()
            if TEXT[0] not in prefix:
                dw = dict(words)
                print(dw)
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
                elif r < count_period and quotes:
                    data_msg.msg = random.choice(quotes)[0]
            print(data_msg.msg)
            #####################################################################################
            if TEXT[0] in prefix:
                key = prefix.get(TEXT[0])
                if key is not None:
                    await key()
            if data_msg.msg or data_msg.attachment:
                await msg.answer(message=data_msg.msg,
                                 attachment=data_msg.attachment,
                                 keyboard=data_msg.keyboard)
                data_msg()

    ###########################################################################################
    except Exception as ex:
        logger(
            f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
        await api_group.messages.send(message=f"WARNING : {json_config().cfg_json()['users_list_warn']}\n\n"
                                              f"{ex} \n {msg.peer_id} \n {traceback.format_exc()}",
                                      peer_id=json_config().cfg_json()['PEER_CRUSH_EVENT'], random_id=0)


vb.run_forever()
