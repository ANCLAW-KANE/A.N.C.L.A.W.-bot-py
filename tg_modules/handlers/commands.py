
import random
from loguru import logger
from sessions_tg import bot_aiogram
from aiogram import Router
from aiogram.types import Message,BufferedInputFile,ReplyKeyboardRemove
from aiogram.filters.command import Command
from tools import download_image
from tg_modules.api_vk_helper import get_images_from_vk
from tg_modules.handlers.keyboard import gen_kb,gen_kb_menu

router = Router()

@router.message(Command("mem"))
async def gen_text(msg: Message):
    logger.debug(f"msg: {msg} | chat_id: {msg.chat.id}")
    url = await get_images_from_vk()
    image = await download_image(url=url)
    if image:
        buff = BufferedInputFile(image,str(random.randint(1,1000000)))
        await bot_aiogram.send_photo(msg.chat.id, buff)

@router.message(Command("menu"))
async def menu(msg: Message):
    logger.debug(f"msg: {msg} | chat_id: {msg.chat.id}")
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Списки комманд', reply_markup=gen_kb())

@router.message(Command("openkb"))
async def menu(msg: Message):
    logger.debug(f"msg: {msg} | chat_id: {msg.chat.id}")
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура включена', reply_markup=gen_kb_menu())

@router.message(Command("closekb"))
async def menu(msg: Message):
    logger.debug(f"msg: {msg} | chat_id: {msg.chat.id}")
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура выключена', reply_markup=ReplyKeyboardRemove())


    