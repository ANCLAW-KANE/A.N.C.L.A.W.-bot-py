
import random
from aiogram import Router,F
from aiogram.types import Message,BufferedInputFile
from CONFIG import path_img
from loguru import logger
from tg_modules.tg_tools import get_data_markov, get_max_photo_id
from sessions_tg import bot_aiogram
from tools import Writer

router = Router()

@router.message(F.photo)
async def get_photo(msg: Message):
    logger.success(f"msg: {msg.photo[0].file_id}| chat_id: {msg.chat.id}")
    idfile = await get_max_photo_id(msg.photo[0:])
    file = await bot_aiogram.get_file(file_id=idfile)
    await bot_aiogram.download_file(file.file_path,f"{path_img}{msg.chat.id}/{idfile}")

@router.message(F.text)
async def text_msg(msg: Message):
    logger.info(f"msg: {msg.text}| chat_id: {msg.chat.id}")
    if random.randint(0, 100) < 20:
        txt = await(await get_data_markov(msg.chat.id)).generate_demotivator()
        if txt: 
            buff = BufferedInputFile(txt,str(random.randint(1,1000000)))
            await bot_aiogram.send_photo(msg.chat.id, buff)
    elif random.randint(0, 100) < 30:
        stck = Writer.read_file_json('stickers_tg.json')
        if stck : await bot_aiogram.send_sticker(msg.chat.id,random.choice(stck['sticker']))
    else:
        txt = await(await get_data_markov(msg.chat.id)).generate_text()
        await bot_aiogram.send_message(msg.chat.id, txt)