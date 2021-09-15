from threading import Thread
import Server , CONFIG
thread_vkNode = Thread(target=Server.vkNode,args=())
thread_vkNode.start()
thread_vkNode.join()
Server.vk.messages.send(random_id=Server.random.randint(0, 999999), message=f"WARNING : "
                                                                            f"{CONFIG.users_list_warn}"
                                                                            " Поток-VkNode уничтожен",
                                                                    peer_id=CONFIG.PEER_CRUSH_EVENT) 
