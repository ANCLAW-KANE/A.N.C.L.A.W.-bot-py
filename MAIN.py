from multiprocessing import Process
import Server , CONFIG

if __name__ == '__main__':

    thread_vk_bot_respondent = Process(target=Server.vk_bot_respondent, args=())
    thread_vk_bot_respondent.start()
    thread_vk_bot_resend = Process(target=Server.vk_bot_resend,args=())
    thread_vk_bot_resend.start()
    thread_vkNode = Process(target=Server.vkNode,args=())
    thread_vkNode.start()


    thread_vk_bot_respondent.join()
    Server.vk.messages.send(random_id=Server.random.randint(0, 999999), message=f"WARNING : " 
                                                                            f"{CONFIG.users_list_warn}"
                                                                            " Поток-RESPONDENT уничтожен",
                                                                    peer_id=CONFIG.PEER_CRUSH_EVENT)
    thread_vk_bot_resend.join()
    Server.vk.messages.send(random_id=Server.random.randint(0, 999999), message=f"WARNING : "
                                                                            f"{CONFIG.users_list_warn}"
                                                                            " Поток-RESEND уничтожен",
                                                                    peer_id=CONFIG.PEER_CRUSH_EVENT)

    thread_vkNode.join()
    Server.vk.messages.send(random_id=Server.random.randint(0, 999999), message=f"WARNING : "
                                                                            f"{CONFIG.users_list_warn}"
                                                                            " Поток-VkNode уничтожен",
                                                                    peer_id=CONFIG.PEER_CRUSH_EVENT)
    if thread_vk_bot_respondent.is_alive():
        thread_vk_bot_respondent.start()
    if thread_vk_bot_resend.is_alive():
        thread_vk_bot_resend.start()
    if thread_vkNode.is_alive():
        thread_vkNode.start()

