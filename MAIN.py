from threading import Thread
import Server



thread_vk_bot_respondent = Thread(target=Server.vk_bot_respondent, args=())

thread_vk_bot_respondent.start()