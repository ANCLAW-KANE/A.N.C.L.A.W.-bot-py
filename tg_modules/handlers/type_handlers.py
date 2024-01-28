
import random
from aiogram import Router,F
from aiogram.types import Message
from CONFIG import path_img,tr_chat
from loguru import logger
from tg_modules.handlers.filters import ChatTypeFilter,group_chat
from tg_modules.tg_tools import get_data_markov, get_max_photo_id,send_photo
from sessions_tg import bot_aiogram
from tools import Writer
from database_module.peer_repo import PeerRepository
from aiogram.filters.logic import and_f


router = Router()




async def process_ldem(generator,msg):
    txt = await generator.generate_big_demotivator(square=True)
    if txt: await send_photo(msg.chat.id, txt, 'gdl')


async def process_dem(generator,msg):
    txt = await generator.generate_demotivator()
    if txt: await send_photo(msg.chat.id, txt, 'gd')


async def process_stck(msg):
    stck = Writer.read_file_json('stickers_tg.json')
    if stck : 
        stickers = stck['sticker']
        if  msg.chat.id == tr_chat: stickers += stck['trbl']
        await bot_aiogram.send_sticker(msg.chat.id,random.choice(stickers))


async def process_txt(generator,msg):
    txt = await generator.generate_text()
    await bot_aiogram.send_message(msg.chat.id, txt)



@router.message(and_f(F.photo,ChatTypeFilter(group_chat)))
async def get_photo(msg: Message):
    logger.success(f"msg: {msg.photo[0].file_id}| chat_id: {msg.chat.id}")
    idfile = await get_max_photo_id(msg.photo[0:])
    file = await bot_aiogram.get_file(file_id=idfile)
    await bot_aiogram.download_file(file.file_path,f"{path_img}{msg.chat.id}/{idfile}")


@router.message(and_f(F.text,ChatTypeFilter(group_chat)))
@router.message(and_f(F.sticker,ChatTypeFilter(group_chat)))
@router.edited_message(and_f(F.text,ChatTypeFilter(group_chat)))
async def text_msg(msg: Message):
    peer_repo = await PeerRepository(msg.chat.id).get_params_peer()
    r = random.randint(0, 100)
    generator = await get_data_markov(msg.chat.id)
    chances = sorted([peer_repo['g_ldem'],peer_repo['g_dem'],peer_repo['g_stck'],peer_repo['g_txt']])
    nums = list(filter(lambda x: x >= r, chances))
    closest_number = min(nums) if nums else None
    data = {
        peer_repo['g_ldem']:(process_ldem,(generator,msg)),
        peer_repo['g_dem']:(process_dem,(generator,msg)),
        peer_repo['g_stck']:(process_stck,(msg,)),
        peer_repo['g_txt']:(process_txt,(generator,msg))
    }
    if closest_number in data:
        key = data.get(closest_number)
        await key[0](*key[1])

