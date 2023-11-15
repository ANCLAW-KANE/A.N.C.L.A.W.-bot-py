import glob
import os
import tracemalloc
from datetime import datetime
from loguru import logger
from database_module.peer_repo import PeerRepository
from vk_modules.handlers import lb
from sessions_vk import vb,api_group
from tools import json_config
from vk_modules.online_tools import getUserName
from vk_modules.Middlewares import RegistrationPeerMiddleware
from database_module.Tables import peerDB,BasePeer
from database_module.marry_repo import MarryRepository
from vk_modules.exceptions import handle_vk_error,handle_exception_error
from pathlib import Path
################################################################################################

# try:
# except ImportError as e:
#    subprocess.check_call([sys.executable, "-m", "pip", "install", e.name])

###################################### init, log ######################################
Path('./temps').mkdir(exist_ok=True)
logger.level("STATE", no=22, color="<yellow>")
logger.level("CHECK", no=27, color="<magenta>")
logger.add(f"./logs/error_{datetime.now().strftime('%d-%m-%Y, %H %M %S')}.log", 
           level="ERROR", format="{time} - {level} - {message}")
logger.add("./logs/log.log", level="INFO", format="{time} - {level} - {message}")
tracemalloc.start()

#######################################################################################

async def start_create():
    logger.log("STATE","\n_________________________STR_________________________")
    json_config().create()
    async with peerDB.begin() as connect:
        await connect.run_sync(BasePeer.metadata.create_all)

#######################################################################################
@vb.loop_wrapper.interval(hours=5) # (seconds=10) 
async def marry_fix():
    logger.log("STATE","\n_________________________LW-marryfix__________________________")
    await MarryRepository(None,None).marry_delete_fix()

@vb.loop_wrapper.interval(days=2)#(seconds=10)
async def clear_logs():
    logger.log("STATE","\n_________________________LW-logs_________________________")
    files = glob.glob(os.path.join("./logs", "*"))
    sorted_files = sorted(files, key=os.path.getctime)
    delete_files = sorted_files[2:] # кроме первых 2 файла
    for file in delete_files:
        if file.endswith(".log"):
            try: os.remove(file)
            except OSError:pass

@vb.loop_wrapper.interval(seconds=25)
async def check_unmute():
    logger.log("STATE","\n_________________________LW-checkUnmute_________________________")
    peerRepo = PeerRepository(None)
    ids = await peerRepo.check_unmute()
    if not ids: return
    await peerRepo.unmute(ids['delete_ids'])
    for i in ids['peers']:
        names = [await getUserName(obj=user,peer=i,return_mentions=True) for user in ids["peers"].get(i)]
        await api_group.messages.send(peer_id=i,message=f'C {", ".join(names)} был снят мут',random_id=0)

#######################################################################################
vb.error_handler.register_error_handler(handle_vk_error,handle_exception_error)
vb.loop_wrapper.on_startup.append(start_create())
vb.labeler.message_view.register_middleware(RegistrationPeerMiddleware)
for label in lb: vb.labeler.load(label)

vb.run_forever()
