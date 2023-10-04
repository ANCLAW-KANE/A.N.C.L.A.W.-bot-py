import random
from loguru import logger
from tg_modules.api_vk_helper import get_images_from_vk
from tg_modules.tg_tools import get_data_markov
from aiogram import Router,F
from aiogram.types import CallbackQuery , BufferedInputFile

from tools import download_image


router = Router()

@router.callback_query(F.data == "g")
async def gen(callback: CallbackQuery):
    logger.debug(f"msg: {callback} | chat_id: {callback.message.chat.id}")
    txt = await (await get_data_markov(callback.message.chat.id)).generate_text()
    await callback.message.answer(txt)

@router.callback_query(F.data == "gd")
async def gen_dem_(callback: CallbackQuery):
    logger.debug(f"msg: {callback} | chat_id: {callback.message.chat.id}")
    txt = await (await get_data_markov(callback.message.chat.id)).generate_demotivator()
    if txt:
        buff = BufferedInputFile(txt,str(random.randint(1,1000000)))
        await callback.message.answer_photo(photo=buff)
    else : await callback.message.answer('Нет изображений в базе данных')

@router.callback_query(F.data == "gl")
async def gen_l_text_(callback: CallbackQuery):
    logger.debug(f"msg: {callback} | chat_id: {callback.message.chat.id}")
    txt = await (await get_data_markov(callback.message.chat.id)).generate_long_text()
    await callback.message.answer(txt)

@router.callback_query(F.data == "mem")
async def mem_send(callback: CallbackQuery):
    logger.debug(f"msg: {callback} | chat_id: {callback.message.chat.id}")
    url = await get_images_from_vk()
    image = await download_image(url=url)
    if image:
        buff = BufferedInputFile(image,str(random.randint(1,1000000)))
        await callback.message.answer_photo(buff)