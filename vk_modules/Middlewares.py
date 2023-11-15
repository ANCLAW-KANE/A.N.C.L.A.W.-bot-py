
import os
from vkbottle import BaseMiddleware 
from vkbottle.bot import Message
from database_module.markov_repo import MarkovRepository
from database_module.peer_repo import PeerRepository
from database_module.Tables import create_peer_table
from vk_modules.hadlers_rules import prefixs
from CONFIG import path_img


class RegistrationPeerMiddleware(BaseMiddleware[Message]):

    async def pre(self):
        try:
            peerID = self.event.peer_id
            ######################################### DB ########################################
            await PeerRepository(peerID).create_settings_peer()  # Стандартные настройки чатов
            await create_peer_table(peer=peerID) # Создание динамических таблиц (для хранения данных для каждого чата)
            if not self.event.text.startswith(prefixs,0,4):
                mRepo = MarkovRepository(self.event.peer_id)
                print("OK")
                await mRepo.add_to_history(message=self.event.text)
            if not os.path.exists(f"{path_img}{peerID}/"):
                os.makedirs(f"{path_img}{peerID}/")
        except Exception as e:
            print(e)
