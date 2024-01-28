#import telebot
#from telethon import TelegramClient
from CONFIG import teletoken,api_hash, api_id
from aiogram import Bot

bot_aiogram = Bot(token=teletoken)
#bot = telebot.TeleBot(teletoken)
#client = TelegramClient("", api_id, api_hash)