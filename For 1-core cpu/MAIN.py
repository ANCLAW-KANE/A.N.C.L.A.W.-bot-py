from threading import Thread
import Server
from tools import json_gen
thread_vk_bot_respondent = Thread(target=Server.vk_bot_respondent, args=())
thread_vk_bot_respondent.start()
thread_vk_bot_respondent.join()
Server.vk.messages.send(random_id=Server.random.randint(0, 999999),
                        message=f"WARNING : " 
                        f"{json_gen().return_config_file_json()['users_list_warn']}"
                        " Поток-RESPONDENT уничтожен",
                        peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])