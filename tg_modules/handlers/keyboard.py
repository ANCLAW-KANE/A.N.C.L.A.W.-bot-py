from aiogram.types import InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand
from aiogram.filters.callback_data import CallbackData
from math import ceil


class Pagination(CallbackData,prefix='pag'):
    command: str
    action: str
    page: int
    page_max : int

class UrlAudio(CallbackData,prefix='url_download'):
    url : str

class PageManager:
    """ Args:\n
            kb (InlineKeyboardMarkup): объект клавиатуры с данными для наполнения\n
            len_data (int): количество кнопок\n
            div (int): разделение на страницы с N кнопками\n
            page (int, optional): Текущая страница. Defaults to 0.
    """
    def __init__(self,kb : InlineKeyboardMarkup ,command:str ,len_data: int , div : int ,page : int = 0) -> None:
        self.kb = kb
        self.len_data = len_data
        self.div = div
        self.page = page
        self.command = command

    def page_kb(self):
        build = InlineKeyboardBuilder(markup=self.kb) 
        max_page = ceil(self.len_data / self.div) - 1
        build.row(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination(
                action = 'prev',
                page=self.page,
                page_max=max_page,
                command=self.command
            ).pack()),
            InlineKeyboardButton(text=f"{self.page} из {max_page}",callback_data='None'),
            InlineKeyboardButton(text="➡️", callback_data=Pagination(
                action = 'next',
                page=self.page,
                page_max=max_page,
                command=self.command
            ).pack())
        )
        return build.as_markup()
    

###########################################################################################
commands = [

    BotCommand(command="/g", description="Короткая генерация текста (только для чатов)"),
    BotCommand(command="/gl", description="Длинная генерация текста (только для чатов)"),
    BotCommand(command="/gd", description="Генерация демотиватора (только для чатов)"),
    BotCommand(command="/gdl", description="Генерация большого демотиватора (только для чатов)"),
    BotCommand(command="/mem", description="Случайный мем или картинка"),
    BotCommand(command="/menu", description="Все комманды"),
    BotCommand(command="/closekb", description="Закрыть клавиатуру в этом чате"),
    BotCommand(command="/openkb", description="Открыть клавиатуру в этом чате")
    
]
###########################################################################################
class InlineKeyboards:
    def gen_chat_kb() -> InlineKeyboardMarkup :
        kb = InlineKeyboardBuilder()
        kb.button(text="/g",callback_data='g')
        kb.button(text="/gl",callback_data='gl')
        kb.button(text="/gd",callback_data='gd')
        kb.button(text="/gdl",callback_data='gdl')
        kb.button(text="/mem",callback_data='mem')
        return kb.as_markup()

    def gen_private_kb() -> InlineKeyboardMarkup :
        kb = InlineKeyboardBuilder()
        kb.button(text="/music",callback_data='music')
        kb.button(text="/mem",callback_data='mem')
        return kb.as_markup()
###########################################################################################
class DataKeyboards:
    def __init__(self,page: int = 0) -> None:
        self.page = page

    def music_kb(self , data, div : int = 40):
        kb = InlineKeyboardBuilder()
        start = self.page * div
        end = start + div
        stop = end if end < len(data) - 1 else len(data)
        block = data[start:stop]
        for d in block:
            kb.row(
                InlineKeyboardButton(text=f"{d['artist']} - {d['title']} ({d['duration']})",
                                    callback_data=UrlAudio(
                                         url=d['url'],
                                         name=f"{d['artist']}-{d['title']}"
                                    ).pack()
                )
            )
        return {
            'kb' : kb.export(),
            'div' : div,
            'page' : self.page,
            'len_data': len(data)
        }



###########################################################################################
class ButtonsRepository:
    default_kb = [
            [
                KeyboardButton(text="/g"),
                KeyboardButton(text="/gl")
            ],
            [
                KeyboardButton(text="/gd"),
                KeyboardButton(text="/mem")
            ],
            [
                KeyboardButton(text="/gdl"),
                KeyboardButton(text="/closekb")
            ]
        ]

    private_kb = [
            [
                KeyboardButton(text="/music"),
                KeyboardButton(text="/mem")
            ]
    ]

    moded_kb = [
            [
                KeyboardButton(text="/th"),
                KeyboardButton(text="/t")
            ],
            [
                KeyboardButton(text="/gdl"),
                KeyboardButton(text="/gd"),
                KeyboardButton(text="/mem"),
                
            ],
            [
                KeyboardButton(text="/g"),
                KeyboardButton(text="/gl")
            ]
        ]
###########################################################################################
class ReplyKeyboards:
    def gen_kb_menu_private() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(
            keyboard= ButtonsRepository.private_kb,
            resize_keyboard=True
        )
        return kb


    def gen_kb_menu_chat() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(
            keyboard= ButtonsRepository.default_kb,
            resize_keyboard=True
        )
        return kb
    
    def gen_kb_menu_chat_tr() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(
            keyboard=ButtonsRepository.moded_kb,
            resize_keyboard=True
        )
        return kb

