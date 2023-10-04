"""from Server import vkNode

vkNode()
"""

import asyncio
from aiogram import Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from tg_modules.handlers import rout
from sessions_tg import bot_aiogram
from tg_modules.Middlewares import AddHistoryMiddleware

commands = [

    BotCommand(command="/g", description="Короткая генерация текста"),
    BotCommand(command="/gl", description="Длинная генерация текста"),
    BotCommand(command="/gd", description="Генерация демотиватора"),
    BotCommand(command="/mem", description="Случайный мем или картинка"),
    BotCommand(command="/menu", description="Все комманды"),
    BotCommand(command="/closekb", description="Закрыть клавиатуру в этом чате"),
    BotCommand(command="/openkb", description="Открыть клавиатуру в этом чате")
    
]

async def main():   
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*rout)
    dp.message.middleware(AddHistoryMiddleware())
    await bot_aiogram.delete_webhook(drop_pending_updates=True)
    await bot_aiogram.set_my_commands(commands=commands)
    await dp.start_polling(bot_aiogram, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())