from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message,CallbackQuery

private = 'private'
group_chat = ['supergroup','group']

class ChatTypeFilter(BaseFilter):  
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, msg) -> bool:
        if isinstance(msg,Message):
            data = msg
        if isinstance(msg,CallbackQuery):
            data = msg.message
        if isinstance(self.chat_type, str):
            return data.chat.type == self.chat_type
        else:
            return data.chat.type in self.chat_type
    

        

class ChatIDFilter(BaseFilter):  
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    async def __call__(self, message: Message) -> bool: 
            return message.chat.id == self.chat_id