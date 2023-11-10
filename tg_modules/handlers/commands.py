
import random
from loguru import logger
from sessions_tg import bot_aiogram
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,BufferedInputFile,ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.filters.logic import and_f
from tg_modules.handlers.filters import ChatTypeFilter,private,group_chat
from tools import download_image
from tg_modules.api_vk_helper import get_images_from_vk,get_audio
from tg_modules.states import Audio
from tg_modules.handlers.keyboard import ReplyKeyboards,InlineKeyboards,DataKeyboards,PageManager
from CONFIG import tr_chat

router = Router()

@router.message(Command("mem"))
async def mem(msg: Message):
    try:
        url = await get_images_from_vk()
        image = await download_image(url=url)
        if image:
            buff = BufferedInputFile(image,str(random.randint(1,1000000)))
            await bot_aiogram.send_photo(msg.chat.id, buff)
    except: msg.answer("Ошибка, повторите запрос")

@router.message(and_f(Command("menu"),ChatTypeFilter(group_chat)))
async def menu(msg: Message):
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Списки комманд', reply_markup=InlineKeyboards.gen_chat_kb())

@router.message(and_f(Command("menu"),ChatTypeFilter(private)))
async def menu(msg: Message):
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Списки комманд', reply_markup=InlineKeyboards.gen_private_kb())

@router.message(and_f(Command("openkb"),ChatTypeFilter(group_chat)))
async def open_kb(msg: Message):
    kb = ReplyKeyboards.gen_kb_menu_chat_tr() if msg.chat.id == tr_chat else ReplyKeyboards.gen_kb_menu_chat()
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура включена', reply_markup=kb)

@router.message(and_f(Command("openkb"),ChatTypeFilter(private)))
async def open_kb(msg: Message):
    kb = ReplyKeyboards.gen_kb_menu_private()
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура включена', reply_markup=kb)

@router.message(Command("closekb"))
async def close_kb(msg: Message):
    await bot_aiogram.send_message(chat_id=msg.chat.id, text='Клавиатура выключена', reply_markup=ReplyKeyboardRemove())

@router.message(and_f(Command("music"),ChatTypeFilter(private)))
async def find_music(msg: Message,state: FSMContext):
    await state.set_state(Audio.name)
    await msg.answer("Введите исполнителя или имя трека")


@router.message(and_f(Audio.name,ChatTypeFilter(private)))
async def find_music(msg: Message,state : FSMContext):
    query = msg.text
    if not query:
        await  msg.answer(text="Пустой запрос, введите исполнителя или имя трека")
        return
    msg_id = await msg.answer(text="Ожидайте, выполняется поиск ...")
    hash_id = f"{msg_id.chat.id}_{msg_id.from_user.id}_{msg_id.message_id}"
    data = await get_audio(query,hash_id)
    if not data: 
        msg.answer("Ничего не найдено, проверьте имя")
        return
    kb_data = DataKeyboards().music_kb(data)
    await msg_id.edit_text(text=f"Аудио по запросу {query}", 
                            reply_markup=PageManager(
                               kb=kb_data['kb'],
                               len_data= kb_data['len_data'],
                               div=kb_data['div'], 
                               page=kb_data['page'],
                               command='music'
                            ).page_kb()
                        )
    await state.clear()