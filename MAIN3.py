"""from Server import vkNode

vkNode()
"""

import asyncio
import os
from aiogram import F
from aiogram import Bot,Router,Dispatcher
from aiogram.types import Message,BufferedInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.command import Command
from CONFIG import teletoken,path_img
from database_module.markov_repo import MarkovRepository
from database_module.Tables import create_peer_table
from markov.generators import Generator
from loguru import logger


bot = Bot(token=teletoken)
router = Router()


async def gen(msg,gen_type='g'):
    mRepo = MarkovRepository(msg.chat.id)
    response = Generator(msg = await mRepo.get_history(), obj = msg)
    if gen_type == 'g':return await response.generate_text()
    if gen_type == 'gl':return await response.generate_long_text()
    if gen_type == 'gd':return await response.generate_demotivator()

async def get_max_photo_id(photos):
    ids = [idfile.file_id for idfile in photos]
    sizes = [size.file_size for size in photos]
    max_size = sorted(sizes)[-1]
    urldict = dict(zip(sizes, ids))
    return urldict.get(max_size)

async def get_photos(photos,peer):
        if not os.path.exists(f"{path_img}{peer}/"):
            os.makedirs(f"{path_img}{peer}/")
        idfile = await get_max_photo_id(photos)
        file = await bot.get_file(file_id=idfile)
        await bot.download_file(file.file_path,f"{path_img}{peer}/{idfile}")
    
async def main():   
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


@router.message(F.photo)
async def echo(msg: Message):
    await get_photos(photos=msg.photo[0:],peer=msg.chat.id)
    #await bot.send_message(msg.chat.id, str(p))

@router.message(Command("g"))
async def echo(msg: Message):
    txt = await gen(msg)
    await bot.send_message(msg.chat.id, txt)

@router.message(Command("gd"))
async def echo(msg: Message):
    txt = await gen(msg,gen_type='gd')
    if txt: 
        buff = BufferedInputFile(txt,'1')
        await bot.send_photo(msg.chat.id, buff)
    else : await bot.send_message(msg.chat.id, 'Нет изображений в базе данных')

@router.message(Command("gl"))
async def echo(msg: Message):
    txt = await gen(msg,gen_type='gl')
    await bot.send_message(msg.chat.id, txt)
    

@router.message(F.text)
async def echo(msg: Message):
    logger.info(f"msg: {msg.text}| chat_id: {msg.chat.id}")
    await create_peer_table(peer=msg.chat.id)
    mRepo = MarkovRepository(msg.chat.id)
    await mRepo.add_to_history(message=msg.text)
    txt = await gen(msg)
    await bot.send_message(msg.chat.id, txt)

if __name__ == "__main__":
    asyncio.run(main())