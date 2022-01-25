from threading import Thread
import Server
from tools import json_gen
thread_vk_bot_resend = Thread(target=Server.vk_bot_resend,args=())
thread_vk_bot_resend.start()
thread_vk_bot_resend.join()
Server.vk.messages.send(random_id=Server.random.randint(0, 999999),
                        message=f"WARNING : " 
                        f"{json_gen().return_config_file_json()['users_list_warn']}"
                        " Поток-RESEND уничтожен",
                        peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])