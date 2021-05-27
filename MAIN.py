from threading import Thread
import Server , CONFIG



thread_vk_bot_respondent = Thread(target=Server.vk_bot_respondent, args=())

thread_vk_bot_respondent.start()

thread_vk_bot_respondent.join()
Server.vk.messages.send(random_id=Server.random.randint(0, 999999), message=f"WARNING : " 
                                                                            f"{CONFIG.users_list_warn}"
                                                                            " Поток-RESPONDENT уничтожен",
                                                                    peer_id=CONFIG.PEER_CRUSH_EVENT)