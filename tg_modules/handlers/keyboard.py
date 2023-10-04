from aiogram.types import InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def gen_kb() -> InlineKeyboardMarkup :
    kb = InlineKeyboardBuilder()
    kb.button(text="/g",callback_data='g')
    kb.button(text="/gl",callback_data='gl')
    kb.button(text="/gd",callback_data='gd')
    kb.button(text="/mem",callback_data='mem')
    return kb.as_markup()


def gen_kb_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/g"),
                KeyboardButton(text="/gl")
            ],
            [
                KeyboardButton(text="/gd"),
                KeyboardButton(text="/mem")
            ]
        ],
        resize_keyboard=True
    )
    return kb