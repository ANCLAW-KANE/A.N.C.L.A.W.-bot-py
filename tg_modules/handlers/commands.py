
import random
from loguru import logger
from sessions_tg import bot_aiogram
from aiogram import Router
from aiogram.types import Message,BufferedInputFile,ReplyKeyboardRemove
from aiogram.filters.command import Command,CommandObject
from aiogram.filters.logic import and_f
from tg_modules.handlers.filters import ChatTypeFilter,private,group_chat
from tools import download_image
from tg_modules.api_vk_helper import get_images_from_vk,get_audio
from tg_modules.handlers.keyboard import gen_chat_kb,gen_kb_menu_chat,gen_kb_menu_chat_tr,\
    gen_private_kb,gen_kb_menu_private, music_kb,page_kb
from CONFIG import tr_chat

router = Router()

@router.message(Command("mem"))
async def mem(msg: Message):
    logger.debug(f"msg: {msg.from_user.first_name} {msg.from_user.last_name} ::: {msg.text}| chat_id: {msg.chat.id}")
    try:
        url = await get_images_from_vk()
        image = await download_image(url=url)
        if image:
            buff = BufferedInputFile(image,str(random.randint(1,1000000)))
            await bot_aiogram.send_photo(msg.chat.id, buff)
    except: msg.answer("Ошибка, повторите запрос")

@router.message(and_f(Command("menu"),ChatTypeFilter(group_chat)))
async def menu(msg: Message):
    logger.debug(f"msg: {msg.from_user.first_name} {msg.from_user.last_name} ::: {msg.text}| chat_id: {msg.chat.id}")
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Списки комманд', reply_markup=gen_chat_kb())

@router.message(and_f(Command("menu"),ChatTypeFilter(private)))
async def menu(msg: Message):
    logger.debug(f"msg: {msg.from_user.first_name} {msg.from_user.last_name} ::: {msg.text}| chat_id: {msg.chat.id}")
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Списки комманд', reply_markup=gen_private_kb())

@router.message(and_f(Command("openkb"),ChatTypeFilter(group_chat)))
async def open_kb(msg: Message):
    logger.debug(f"msg: {msg.from_user.first_name} {msg.from_user.last_name} ::: {msg.text}| chat_id: {msg.chat.id}")
    kb = gen_kb_menu_chat_tr() if msg.chat.id == tr_chat else gen_kb_menu_chat()
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура включена', reply_markup=kb)

@router.message(and_f(Command("openkb"),ChatTypeFilter(private)))
async def open_kb(msg: Message):
    logger.debug(f"msg: {msg.from_user.first_name} {msg.from_user.last_name} ::: {msg.text}| chat_id: {msg.chat.id}")
    kb = gen_kb_menu_private()
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура включена', reply_markup=kb)

@router.message(Command("closekb"))
async def close_kb(msg: Message):
    logger.debug(f"msg: {msg.from_user.first_name} {msg.from_user.last_name} ::: {msg.text}| chat_id: {msg.chat.id}")
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура выключена', reply_markup=ReplyKeyboardRemove())

@router.message(and_f(Command("music"),ChatTypeFilter(private)))
async def find_music(msg: Message,command: CommandObject):
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='приватный чат')
    query = command.args if command.args else None
    if not query:
        await  bot_aiogram.send_message(chat_id=msg.chat.id, text="Пустой запрос, введите исполнителя или имя трека")
        return
    msg_id = await  bot_aiogram.send_message(chat_id=msg.chat.id, text="Ожидайте, выполняется поиск ...")
    hash_id = f"{msg_id.chat.id}_{msg_id.from_user.id}_{msg_id.message_id}"
    data = await get_audio(query,hash_id)
    kb_data = music_kb(data)
    await msg_id.edit_text(text=f"Аудио по запросу {query}", 
                           reply_markup=page_kb(kb_data['kb'], kb_data['len_data'],
                                                kb_data['div'], kb_data['page'] )
                        )

    