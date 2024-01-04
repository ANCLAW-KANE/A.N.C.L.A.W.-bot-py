"""from Server import vkNode

vkNode()
"""

import asyncio
from aiogram import Dispatcher
from tg_modules.handlers.keyboard import commands
from aiogram.fsm.storage.memory import MemoryStorage
from tg_modules.handlers import rout
from sessions_tg import bot_aiogram
from tg_modules.Middlewares import AddHistoryMiddleware
from database_module.Tables import BaseHash , hashDB, peerDB, BasePeer
 

async def main():
    async with hashDB.begin() as connect:
        await connect.run_sync(BaseHash.metadata.create_all)
    async with peerDB.begin() as conn:
        await conn.run_sync(BasePeer.metadata.create_all)   
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*rout)
    dp.message.middleware(AddHistoryMiddleware())
    
    await bot_aiogram.delete_webhook(drop_pending_updates=True)
    await bot_aiogram.set_my_commands(commands=commands)
    
    await dp.start_polling(bot_aiogram, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
    