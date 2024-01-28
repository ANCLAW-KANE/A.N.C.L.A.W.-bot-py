import random
from time import time

from loguru import logger
from database_module.markov_repo import MarkovRepository
from markov.generators import Generator
from sessions_tg import bot_aiogram
from aiogram.types import BufferedInputFile


async def get_max_photo_id(photos):
    ids = [idfile.file_id for idfile in photos]
    sizes = [size.file_size for size in photos]
    max_size = sorted(sizes)[-1]
    urldict = dict(zip(sizes, ids))
    return urldict.get(max_size)


async def get_data_markov(chat):
    mRepo = MarkovRepository(chat)
    return Generator(msg = await mRepo.get_history(),obj=chat)


async def send_photo(chat,img,mode,obj = bot_aiogram):
    start_time = time()
    buff = BufferedInputFile(img,str(random.randint(1,1000000)))
    await obj.send_photo(chat, buff)
    end_time = time()
    logger.warning(f"{mode} :upl: {end_time - start_time}")


def page_toggle(obj):
    page = int(obj.page)
    numPage = page - 1 if page > 0 else 0
    if obj.action == 'next':
        numPage = page + 1 if page < obj.page_max else obj.page_max
    return numPage