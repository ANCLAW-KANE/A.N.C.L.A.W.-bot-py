import tracemalloc
from datetime import datetime
from loguru import logger
from handlers import lb
from sessions import vb
from tools import json_config, data_msg
from database_module.Tables import peerDB,BasePeer,MarryRepository
from exceptions import handle_vk_error
from pathlib import Path
################################################################################################

# try:
# except ImportError as e:
#    subprocess.check_call([sys.executable, "-m", "pip", "install", e.name])

###################################### init, log ######################################
Path('./temps').mkdir(exist_ok=True)
logger.level("STATE", no=22, color="<yellow>")
logger.level("CHECK", no=27, color="<magenta>")
logger.add(f"./logs/error_{datetime.now().strftime('%d-%m-%Y, %H %M %S')}.log", level="ERROR", format="{time} - {level} - {message}")
logger.add("./logs/log.log", level="INFO", format="{time} - {level} - {message}")
tracemalloc.start()
data_msg()#избавиться
for label in lb: vb.labeler.load(label)
#######################################################################################

async def start_create():
    logger.log("STATE","\n_________________________STR_________________________")
    json_config().create()
    async with peerDB.begin() as connect:
        await connect.run_sync(BasePeer.metadata.create_all)

#######################################################################################
@vb.loop_wrapper.interval(hours=3) # (seconds=10) ПРОВЕРИТЬ
async def marry_fix():
    logger.log("STATE","\n_________________________LW1_________________________")
    await MarryRepository(None,None).marry_delete_fix()

#######################################################################################
vb.error_handler.register_error_handler(handle_vk_error)
vb.loop_wrapper.on_startup.append(start_create())

vb.run_forever()
