import random
from loguru import logger
from tg_modules.tg_tools import get_data_markov
from sessions_tg import bot_aiogram
from aiogram import Router
from aiogram.types import Message,BufferedInputFile
from aiogram.filters.command import Command

router = Router()

@router.message(Command("g"))
async def gen_text(msg: Message):
    logger.debug(f"msg: {msg} | chat_id: {msg.chat.id}")
    txt = await (await get_data_markov(msg.chat.id)).generate_text()
    await bot_aiogram.send_message(msg.chat.id, txt)

@router.message(Command("gd"))
async def gen_dem(msg: Message):
    logger.debug(f"msg: {msg}| chat_id: {msg.chat.id}")
    txt = await (await get_data_markov(msg.chat.id)).generate_demotivator()
    if txt: 
        buff = BufferedInputFile(txt,str(random.randint(1,1000000)))
        await bot_aiogram.send_photo(msg.chat.id, buff)
    else : await bot_aiogram.send_message(msg.chat.id, 'Нет изображений в базе данных')

@router.message(Command("gl"))
async def gen_l_text(msg: Message):
    logger.debug(f"msg: {msg}| chat_id: {msg.chat.id}")
    txt = await (await get_data_markov(msg.chat.id)).generate_long_text()
    await bot_aiogram.send_message(msg.chat.id, txt)