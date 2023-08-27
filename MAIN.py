import os
import tracemalloc
import aiosqlite
from loguru import logger
from enums import Colors
from handlers import lb
from CONFIG import config_file_json
from online_tools import getUserName
from sessions import file_log, vb
from tools import write_file_json, read_file_json, json_config, data_msg

################################################################################################

# try:
# except ImportError as e:
#    subprocess.check_call([sys.executable, "-m", "pip", "install", e.name])

###################################### init, log ######################################
aiosqlite.core.LOG.disabled = True

logger.level("STATE", no=33, color="<yellow>")
tracemalloc.start()
data_msg()
for label in lb: vb.labeler.load(label)
#######################################################################################

async def start_create():
    logger.log("STATE","\n_________________________STR_________________________")
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
        f"man2name TEXT,allow INT,await INT);"
        f"CREATE TABLE IF NOT EXISTS nicknames(peer_id INT PRIMARY KEY, user_id INT, nickname TEXT);")
    for e in read_file_json(config_file_json):
        await edit.execute(f"INSERT OR IGNORE INTO params_info VALUES('{e}','')")
    await BD.commit()


@vb.loop_wrapper.interval(hours=3) #(seconds=10)
async def marry_fix():
    logger.log("STATE","\n_________________________LW1_________________________")
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

vb.run_forever()
