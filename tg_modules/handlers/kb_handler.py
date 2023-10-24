import random
import time
from loguru import logger
from tg_modules.api_vk_helper import get_images_from_vk,get_content
from tg_modules.handlers.filters import ChatTypeFilter,group_chat,private
from tg_modules.tg_tools import get_data_markov,send_photo,page_toggle
from tg_modules.handlers.keyboard import Pagination, music_kb, page_kb,UrlAudio
from aiogram import Router,F
from aiogram.types import CallbackQuery , BufferedInputFile,InputMediaAudio
from aiogram.filters.logic import and_f
from tools import download_image,Writer,Patterns
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from database_module.operations_repo import get_url
from sessions_tg import bot_aiogram
router = Router()

@router.callback_query(and_f(F.data == "g",ChatTypeFilter(group_chat)))
async def gen(callback: CallbackQuery):
    logger.debug(f"msg: {callback.from_user.first_name} {callback.from_user.last_name} | chat_id: {callback.message.chat.id}")
    g = await get_data_markov(callback.message.chat.id)
    txt = await g.generate_text()
    await callback.message.answer(txt)

@router.callback_query(and_f(F.data == "gd",ChatTypeFilter(group_chat)))
async def gen_dem_(callback: CallbackQuery):
    logger.debug(f"msg: {callback.from_user.first_name} {callback.from_user.last_name} | chat_id: {callback.message.chat.id}")
    g = await get_data_markov(callback.message.chat.id)
    img = await g.generate_demotivator()
    if img: await send_photo(callback.message.chat.id,img,'gd')
    else : await callback.message.answer('Нет изображений в базе данных')

@router.callback_query(and_f(F.data == "gl",ChatTypeFilter(group_chat)))
async def gen_l_text_(callback: CallbackQuery):
    logger.debug(f"msg: {callback.from_user.first_name} | chat_id: {callback.message.chat.id}")
    g = await get_data_markov(callback.message.chat.id)
    txt = await g.generate_long_text()
    await callback.message.answer(txt)

@router.callback_query(F.data == "mem")
async def mem_send(callback: CallbackQuery):
    logger.debug(f"msg: {callback.from_user.first_name} {callback.from_user.last_name} | chat_id: {callback.message.chat.id}")
    url = await get_images_from_vk()
    image = await download_image(url=url)
    if image:
        buff = BufferedInputFile(image,str(random.randint(1,1000000)))
        await callback.message.answer_photo(buff)

@router.callback_query(and_f(F.data == "gdl",ChatTypeFilter(group_chat)))
async def gen_long_dem_(callback: CallbackQuery):
    logger.debug(f"msg: {callback.from_user.first_name} {callback.from_user.last_name} | chat_id: {callback.message.chat.id}")
    g = await get_data_markov(callback.message.chat.id)
    img = await g.generate_big_demotivator()
    if img: await send_photo(callback.message.chat.id,img,'gdl')
    else : await callback.message.answer('Нет изображений в базе данных')

@router.callback_query(and_f(F.data == "music",ChatTypeFilter(private)))
async def music(callback: CallbackQuery):
    logger.debug(f"msg: {callback.from_user.first_name} {callback.from_user.last_name} | chat_id: {callback.message.chat.id}")
    await callback.message.answer('приватный чат')


@router.callback_query(and_f(Pagination.filter(F.action.in_(['prev','next'])),ChatTypeFilter(private)))
async def page_(callback: CallbackQuery,callback_data : Pagination):
    start_time = time.time()
    print(callback_data)
    print(callback.data)
    numPage = page_toggle(callback_data)
    data = Writer.read_file_json(
        f"temps/{callback.message.chat.id}_{callback.message.from_user.id}_{callback.message.message_id}.json")
    if data:
         kb_data = music_kb(data=data,page=numPage)
    else:
        callback.answer('Что то пошло не так ,поробуйте выполнить поиск снова')
    logger.warning(f" :page audio vk: {time.time() - start_time}")
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text=f"{callback.message.text}", reply_markup=page_kb(
                                                                            kb_data['kb'],
                                                                            kb_data['len_data'],
                                                                            kb_data['div'],
                                                                            kb_data['page'])
                                                                        )
    callback.answer()


@router.callback_query(and_f(UrlAudio.filter(F.url.regexp(pattern=Patterns.md5)),ChatTypeFilter(private)))
async def down_audio(callback: CallbackQuery,callback_data:UrlAudio):
    s = time.time()
    url = await get_url(callback_data.url)
    info = await bot_aiogram.send_message(callback.message.chat.id,'Скачивается... ')
    audio = await get_content(url=url)
    logger.warning(f" :dwn audio vk: {time.time() - s}")

    s = time.time()
    buff = BufferedInputFile(audio,str(random.randint(1,1000000)))
    await bot_aiogram.send_audio(callback.message.chat.id,buff)
    info.delete()
    logger.warning(f" :upl audio vk: {time.time() - s}")