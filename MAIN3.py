"""from Server import vkNode

vkNode()
"""

import asyncio, os, random
from aiogram import Bot,Router,Dispatcher,F
from aiogram.types import Message,BufferedInputFile,ErrorEvent
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.command import Command
from CONFIG import teletoken,path_img
from database_module.markov_repo import MarkovRepository
from database_module.Tables import create_peer_table
from loguru import logger
from tg_modules.tools import get_max_photo_id, get_data

bot = Bot(token=teletoken)
router = Router()

async def main():   
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

@router.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Critical error caused by {event.exception}")
    pass


@router.message(F.photo)
async def echo(msg: Message):
    logger.success(f"msg: {msg.photo[0].file_id}| chat_id: {msg.chat.id}")
    if not os.path.exists(f"{path_img}{msg.chat.id}/"):
        os.makedirs(f"{path_img}{msg.chat.id}/")
    idfile = await get_max_photo_id(msg.photo[0:])
    file = await bot.get_file(file_id=idfile)
    await bot.download_file(file.file_path,f"{path_img}{msg.chat.id}/{idfile}")

@router.message(Command("g"))
async def echo(msg: Message):
    logger.debug(f"msg: {msg}| chat_id: {msg.chat.id}")
    response = await get_data(msg.chat.id)
    txt = await response.generate_text()
    await bot.send_message(msg.chat.id, txt)

@router.message(Command("gd"))
async def echo(msg: Message):
    logger.debug(f"msg: {msg}| chat_id: {msg.chat.id}")
    response = await get_data(msg.chat.id)
    txt = await response.generate_demotivator()
    if txt: 
        buff = BufferedInputFile(txt,str(random.randint(1,1000000)))
        await bot.send_photo(msg.chat.id, buff)
    else : await bot.send_message(msg.chat.id, 'Нет изображений в базе данных')

@router.message(Command("gl"))
async def echo(msg: Message):
    logger.debug(f"msg: {msg}| chat_id: {msg.chat.id}")
    response = await get_data(msg.chat.id)
    txt = await response.generate_long_text()
    await bot.send_message(msg.chat.id, txt)
    

@router.message(F.text)
async def echo(msg: Message):
    logger.info(f"msg: {msg.text}| chat_id: {msg.chat.id}")
    await create_peer_table(peer=msg.chat.id)
    mRepo = MarkovRepository(msg.chat.id)
    await mRepo.add_to_history(message=msg.text)
    response = await get_data(msg.chat.id)
    txt = await response.generate_text()
    await bot.send_message(msg.chat.id, txt)

if __name__ == "__main__":
    asyncio.run(main())