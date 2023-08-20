import time, sqlite3, traceback

from resend_function import SendTGtoVK
from resend_parser import parse_resend
from telebot.types import InputMediaDocument
from vk_api.bot_longpoll import VkBotEventType
from online_tools import get_online
from tools import json_config, logger
from sessions import vk, bot, longpoll_full, file_log


############################ отправка в чат телеги из вк ##################################
def vk_bot_resend():
    BD = sqlite3.connect('peers.db')
    edit = BD.cursor()
    for resend in longpoll_full.listen():
        try:
            ################################## Обработчик #########################################
            if resend.type == VkBotEventType.MESSAGE_NEW:
                UserId = resend.object.message['from_id']
                PeerId = resend.object.message['peer_id']
                ########################## Распределение точек отправки ###############################
                edit.execute(f"SELECT tg_id , vk_tg_allow FROM nodes WHERE peer_id = {PeerId}")
                tg_id = edit.fetchone()
                edit.execute(f"SELECT resend FROM peers WHERE peer_id = {PeerId}")
                global_allow = edit.fetchone()[0]
                if tg_id is not None:
                    node = tg_id[0]
                    allow = tg_id[1]
                else:
                    node = json_config().cfg_json()['idGroupTelegram']
                    allow = global_allow
                #######################################################################################
                if allow == 1 and UserId > 0: parse_resend(node, resend.object.message, PeerId, UserId).sender()
        except Exception as e:
            logger(f"\n________________________\n{traceback.format_exc()}"
                   f"\n________________________\n\n\n", "ERROR.log")
            vk.messages.send(random_id=0, message=f"WARNING : "
                                                  f"{json_config().cfg_json()['users_list_warn']}"
                                                  f"\n\n{e}", peer_id=resend.object.message['peer_id'])


############################ отправка в чат вк из телеги ##################################
def vkNode():
    # @bot.message_handler(commands=['id'])

    @bot.message_handler(commands=['id'])
    def show_id(message):
        bot.send_message(message.chat.id, message.chat.id)

    @bot.message_handler(commands=['online'])
    def show_online(message):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT peer_id  FROM nodes WHERE tg_id = {message.chat.id}")
        peer = edit.fetchone()
        BD.close()
        node = None
        if peer is not None: node = peer[0]
        if node is not None:
            bot.send_message(message.chat.id, get_online(node))
        else:
            bot.send_message(message.chat.id, "Этот чат не имеет привязки к вк чату")

    @bot.message_handler(commands=['log'])
    def log_down(message):
        media_group = []
        for f in file_log: media_group.append(InputMediaDocument(media=open(f, "rb")))
        bot.send_media_group(message.chat.id, media_group)

    @bot.message_handler(content_types=['text', 'video', 'photo', 'document', 'animation', 'sticker', 'audio'])
    def TG_VK(message):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT peer_id, tg_vk_allow FROM nodes WHERE tg_id = {message.chat.id}")
        peer = edit.fetchone()
        BD.close()
        if peer is not None:
            time.sleep(1)
            if peer[0] is not None and peer[1] == 1: SendTGtoVK(message, peer[0]).upload_vk()

    try:
        bot.polling(none_stop=True, timeout=40, long_polling_timeout=40)
    except Exception as e:
        vk.messages.send(random_id=0, message=f"WARNING: {json_config().cfg_json()['users_list_warn']}"
                                              f"\n\n{e}",
                         peer_id=json_config().cfg_json()['PEER_CRUSH_EVENT'])
        logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
        pass
