from threading import Thread
import Server , CONFIG
thread_vkNode = Thread(target=Server.vkNode,args=())
thread_vkNode.start()
thread_vkNode.join()
Server.vk.messages.send(random_id=Server.random.randint(0, 999999), message=f"WARNING : " 
