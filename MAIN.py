import tracemalloc
from pathlib import Path
from loguru import logger
from handlers import lb
from online_tools import getUserName
from sessions import file_log, vb
from tools import json_config, data_msg
from database_module.Tables import peerDB,BasePeer,Marry,DBexec
from sqlalchemy import select,update,delete,or_,case
from itertools import chain
from exceptions import handle_vk_error
################################################################################################

# try:
# except ImportError as e:
#    subprocess.check_call([sys.executable, "-m", "pip", "install", e.name])

###################################### init, log ######################################
logger.level("STATE", no=22, color="<yellow>")
logger.level("CHECK", no=27, color="<magenta>")
logger.add("error.log", level="ERROR", format="{time} - {level} - {message}")
logger.add("log.log", level="INFO", format="{time} - {level} - {message}")
tracemalloc.start()
data_msg()
for label in lb: vb.labeler.load(label)
#######################################################################################

async def start_create():
    logger.log("STATE","\n_________________________STR_________________________")
    json_config().create()
    Path(*file_log).touch()
    async with peerDB.begin() as connect:
        await connect.run_sync(BasePeer.metadata.create_all)

#######################################################################################
@vb.loop_wrapper.interval(hours=3) # (seconds=10) ПРОВЕРИТЬ
async def marry_fix():
    logger.log("STATE","\n_________________________LW1_________________________")
    ids = await DBexec(peerDB,select(Marry.man1, Marry.man2)).dbselect()
    print(ids)
    users = list(set(chain.from_iterable(ids)))
    for z in users:
        user = await getUserName(z)
        await DBexec(peerDB,update(Marry).where(or_(Marry.man1 == z, Marry.man2 == z)).values(
                man1name=case((Marry.man1 == z, user), else_=Marry.man1name),
                man2name=case((Marry.man2 == z, user), else_=Marry.man2name))).dbedit()
    await DBexec(peerDB,delete(Marry).where(or_(Marry.man1name == 'None',Marry.man1name == 'DELETED ',
                                Marry.man2name == 'None',Marry.man2name == 'DELETED ')))

#######################################################################################
vb.error_handler.register_error_handler(handle_vk_error)
vb.loop_wrapper.on_startup.append(start_create())

vb.run_forever()
