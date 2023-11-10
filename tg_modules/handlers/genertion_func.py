
from loguru import logger
from tg_modules.tg_tools import get_data_markov,send_photo
from sessions_tg import bot_aiogram
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandObject
from markov.generator_settings_manager import GenerateSettings
from aiogram.filters.logic import and_f
from tg_modules.handlers.filters import ChatTypeFilter,group_chat

router = Router()

@router.message(and_f(Command("g"),ChatTypeFilter(group_chat)))
async def gen_text(msg: Message):
    g = await get_data_markov(msg.chat.id)
    txt = await g.generate_text()
    await bot_aiogram.send_message(msg.chat.id, txt)

@router.message(and_f(Command("gd"),ChatTypeFilter(group_chat)))
async def gen_dem(msg: Message):
    g = await get_data_markov(msg.chat.id)
    img = await g.generate_demotivator()
    if img:  await send_photo(msg.chat.id,img,'gd')
    else : await msg.answer('Нет изображений в базе данных')

@router.message(and_f(Command("gl"),ChatTypeFilter(group_chat)))
async def gen_l_text(msg: Message):
    g = await get_data_markov(msg.chat.id)
    txt = await g.generate_long_text()
    if not txt: txt = "Мало данных для генерации"
    await msg.answer(txt)

@router.message(and_f(Command("gdl"),ChatTypeFilter(group_chat)))
async def gen_long_dem(msg: Message):
    g = await get_data_markov(msg.chat.id)
    img = await g.generate_big_demotivator(square=True)
    if not img: 
        await msg.answer("Мало данных для генерации ")
        return
    await send_photo(msg.chat.id,img,'gdl')

@router.message(and_f(Command("gset"),ChatTypeFilter(group_chat)))
async def settings_manager(msg: Message,command: CommandObject):
    arguments = command.args.split() if command.args else [None]
    setting = arguments[0]
    args = arguments[1:] if len(arguments) >= 1 else None
    gen = GenerateSettings(msg.chat.id)
    g_set = {
        't': (gen.set_gen,(args,)),
        'd': (gen.set_dem,(args,)),
        'dl': (gen.set_gdl,(args,)),
        'stck': (gen.set_stck,(args,)),
        'show': (gen.show,()),
        None: (gen.help,())
    }
    key = g_set.get(setting)
    if key is not None:
        text = await key[0](*key[1])
        await bot_aiogram.send_message(msg.chat.id,text)
