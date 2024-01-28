
from loguru import logger
from tg_modules.tg_tools import get_data_markov, send_photo
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.filters.logic import and_f
from CONFIG import tr_chat
from tg_modules.handlers.filters import ChatIDFilter
from enums import ColorsRGB



router = Router(name="exc")


@router.message(and_f(Command("t"),ChatIDFilter(tr_chat)))
async def gen_tr(msg: Message):
    g = await get_data_markov(msg.chat.id)
    img = await g.gen_mem('trbnk')
    if img:  await send_photo(msg.chat.id,img,'gtr')
    else : await msg.answer('Ошибка генерации')


@router.message(and_f(Command("th"),ChatIDFilter(tr_chat)))
async def gen_tr(msg: Message):
    g = await get_data_markov(msg.chat.id)
    img = await g.generate_big_demotivator(file_static='hack_static',color=ColorsRGB.Colors.light_blue_1.value,new_height=1000)
    if not img: 
        await msg.answer("Мало данных для генерации ")
        return
    await send_photo(msg.chat.id,img,'gtrHack')

