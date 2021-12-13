import vk_api, telebot
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api import VkApi , audio
from CONFIG import teletoken , vktokenGroup , vktokenUser,full_permission_user_token,IdGroupVK
from tools import json_gen
################### Авторизация ###########################
bot = telebot.TeleBot(teletoken)

vk_session: VkApi = vk_api.VkApi(token=vktokenGroup)#Группа
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, IdGroupVK)

def captcha_handler(captcha):#обход капчи
    print(f"Enter captcha code: {captcha.get_url()}")
    vk.messages.send(random_id=0, message=f"Enter captcha code: {captcha.get_url()}",
                     peer_id=json_gen().return_config_file_json()['CAPTCHA_EVENT'])
    for captcha_trigger in longpoll.listen():
        return captcha.try_again( captcha_trigger.object.text)

vk_session_user : VkApi = vk_api.VkApi(token=vktokenUser,captcha_handler=captcha_handler)#Пользователь
vk_user = vk_session_user.get_api()

vk_session_full : VkApi = vk_api.VkApi(token=full_permission_user_token,captcha_handler=captcha_handler)#VKME
vk_full = vk_session_full.get_api()

longpoll_full = VkBotLongPoll(vk_session_full, IdGroupVK)
upload = vk_api.VkUpload(vk_full)
api_audio = vk_api.audio.VkAudio(vk_session_full)

tag = ''

size_values = list("smxopqryzw")

tab = {
    'chat_kick_user': '⚠⚠⚠ УДАЛЕН ',
    'chat_invite_user': '⚠⚠⚠ ДОБАВЛЕН ',
    'chat_invite_user_by_link': '⚠⚠⚠ ПРИГЛАШЕН ПО ССЫЛКЕ ',
}

platforms = {
    1 : 'мобильная версия сайта',
    2 : 'iPhone',
    3 : 'iPad',
    4 : 'Android',
    5 : 'Windows Phone',
    6 : 'Windows 10',
    7 : 'полная версия сайта'
}