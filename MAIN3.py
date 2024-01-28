"""from Server import vkNode

vkNode()
"""

import tracemalloc
from aiogram import Dispatcher
from asyncio import run
from loguru import logger
from psutil import Process
from tg_modules.handlers.keyboard import commands
from aiogram.fsm.storage.memory import MemoryStorage
from tg_modules.handlers import rout
from sessions_tg import bot_aiogram
from tg_modules.Middlewares import AddHistoryMiddleware
from database_module.Tables import BaseHash, hashDB, peerDB, BasePeer, create_database,\
    peer, peer_texts_markov,hash,peer_roles,peer_words


tracemalloc.start()
def get_loaded_modules_and_memory_usage():
    process = Process()
    memory_info = process.memory_info()
    return memory_info.rss

async def main():
    await create_database([peer, peer_texts_markov,hash,peer_words,peer_roles])
    async with hashDB.begin() as connect:
        await connect.run_sync(BaseHash.metadata.create_all)
    async with peerDB.begin() as conn:
        await conn.run_sync(BasePeer.metadata.create_all)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*rout)
    dp.message.middleware(AddHistoryMiddleware())
    memory_usage = get_loaded_modules_and_memory_usage()
    logger.debug(f"Потребление памяти: {memory_usage / (1024 * 1024):.2f} MB")
    await bot_aiogram.delete_webhook(drop_pending_updates=True)
    await bot_aiogram.set_my_commands(commands=commands)
    await dp.start_polling(bot_aiogram, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    run(main())
