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



"""################################### Сервис метод ##################################################
#vk_Service: VkApi = vk_api.VkApi(token=vktokenService)
#vk_Srv = vk_Service.get_api()
################################### Группа ##################################################
#vk_session: VkApi = vk_api.VkApi(token=vktokenGroup)
#vk = vk_session.get_api()
#longpoll = VkBotLongPoll(vk_session, IdGroupVK)

############################## обход капчи ##################################################

#def captcha_handler(captcha):
#    vk.messages.send(random_id=0, message=f"Enter captcha code: {captcha.get_url()}",
#                     peer_id=json_config().cfg_json()['CAPTCHA_EVENT'])
#    for captcha_trigger in longpoll.listen(): return captcha.try_again(captcha_trigger.object.message['text'])

################################## Пользователь #############################################
#vk_session_user: VkApi = vk_api.VkApi(token=full_permission_user_token, captcha_handler=captcha_handler)
#vk_user = vk_session_user.get_api()
#longpoll_user = VkLongPoll(vk_session_user)
################################## Все права ################################################
#vk_session_full: VkApi = vk_api.VkApi(token=full_permission_user_token, captcha_handler=captcha_handler)
#vk_full = vk_session_full.get_api()
#longpoll_full = VkBotLongPoll(vk_session_full, IdGroupVK)
#upload = vk_api.VkUpload(vk_full)
#api_audio = vk_api.audio.VkAudio(vk_session_full)
###########################################################################################"""

file_log = ['ERROR.log', 'Log.log']
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

global_catalog_command = f" \
|||💻user|||\n \
__________________________________\n\
/settings -c \n \
/settings word create(update,delete,list)  \n \
/settings role create(update,delete,list) \n \
/settings quote create(update,delete,list) \n \
/settings count \n \
/settings chat \n \
/кик\n\
/мем\n\
/i -c\n\
/d -c\n\
__________________________________\n\
|||⚙🔧bot-admin|||\n\
* EVIL GOD *  \n \
/settings node create(update,delete,list)(allow-vk,allow-tg)\n \
/settings json-edit <param>  <int, string, bool> args /or/ arr-int arg\n\
/settings json-show \n \
/settings json-params \n \
/settings json-pe create(update,delete)\n \
/cabal:kill_all_members=active\n\
/addUser\n\
/clear_docs_init\n\
/toggle_red\n\
__________________________________\
"
