import os
from aiogram import BaseMiddleware
from aiogram.types import Message,CallbackQuery
from typing import Callable,Dict,Any,Awaitable
from loguru import logger
from database_module.Tables import create_peer_table
from database_module.markov_repo import MarkovRepository
from database_module.peer_repo import PeerRepository
from CONFIG import path_img

class AddHistoryMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        logger.info(f"msg: {event.from_user.first_name} {event.from_user.last_name} ::: {event.text} /sticker/ {event.sticker}| chat_id: {event.chat.id}")
        await create_peer_table(peer=event.chat.id)
        await PeerRepository(event.chat.id).create_settings_peer()
        if not os.path.exists(f"{path_img}{event.chat.id}/"):
            os.makedirs(f"{path_img}{event.chat.id}/")
        if event.text and '/' not in event.text: 
            d = MarkovRepository(event.chat.id)
            await d.add_to_history(event.text)
        return await handler(event, data)
    

class CallbackMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        logger.debug(f"msg: {event.from_user.first_name} {event.from_user.last_name} {event.data}| chat_id: {event.message.chat.id}")
        return await handler(event, data)