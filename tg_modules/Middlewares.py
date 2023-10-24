import os
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable,Dict,Any,Awaitable
from database_module.Tables import create_peer_table
from database_module.markov_repo import MarkovRepository
from database_module.peer_repo import PeerRepository
from CONFIG import path_img
from tg_modules.handlers.keyboard  import commands

class AddHistoryMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        await create_peer_table(peer=event.chat.id)
        await PeerRepository(event.chat.id).create_settings_peer()
        if not os.path.exists(f"{path_img}{event.chat.id}/"):
            os.makedirs(f"{path_img}{event.chat.id}/")
        if event.text and '/' not in event.text: 
            d = MarkovRepository(event.chat.id)
            await d.add_to_history(event.text)
        return await handler(event, data)
    
