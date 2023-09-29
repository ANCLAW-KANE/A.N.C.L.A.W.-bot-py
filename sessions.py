import telebot
from vkbottle import API
from vkbottle.bot import Bot
from telethon import TelegramClient
from CONFIG import teletoken, vktokenGroup, full_permission_user_token,api_hash, api_id

###################################### Авторизация ##############################################
##################################### Телеграм ##################################################
bot = telebot.TeleBot(teletoken)
client = TelegramClient("", api_id, api_hash)
##################################### VKBOTTLE ##################################################
vb = Bot(token=vktokenGroup)
api_group = API(token=vktokenGroup)
api_user = API(token=full_permission_user_token)


size_values = list("smxopqryzw")
max_user_id = 2000000000
              

platforms = {
    1: 'мобильная версия сайта',
    2: 'iPhone',
    3: 'iPad',
    4: 'Android',
    5: 'Windows Phone',
    6: 'Windows 10',
    7: 'полная версия сайта'
}
