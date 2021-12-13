from threading import Thread
import Server
from tools import json_gen
thread_vkNode = Thread(target=Server.vkNode,args=())
thread_vkNode.start()
thread_vkNode.join()
Server.vk.messages.send(random_id=Server.random.randint(0, 999999),
                        message=f"WARNING : " 
                        f"{json_gen().return_config_file_json()['users_list_warn']}"
                        " Поток-VkNode уничтожен",
                        peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])