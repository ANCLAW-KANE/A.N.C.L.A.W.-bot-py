from loguru import logger
from vkbottle import VKAPIError
from sessions_vk import api_group
from tools import json_config

async def handle_vk_error(error: VKAPIError):
    print('vkkkkkkkkkkkkkkkkkkkkkkk')
    logger.error(error)
    error_message = f"WARNING : {json_config().read_key('sys','users_list_warn')}\nПроизошла ошибка VK: {error}"
    await api_group.messages.send(message=error_message, peer_id=json_config().read_key('sys','PEER_CRUSH_EVENT'), random_id=0)

async def handle_exception_error(error: Exception):
    print('exxxxxxxxxxx')
    logger.error(error)
    error_message = f"WARNING : {json_config().read_key('sys','users_list_warn')}\nПроизошла критическая ошибка: {error}"
    await api_group.messages.send(message=error_message, peer_id=json_config().read_key('sys','PEER_CRUSH_EVENT'), random_id=0)