
from vkbottle import BaseMiddleware 
from vkbottle.bot import Message
from database_module.markov_repo import MarkovRepository
from database_module.peer_repo import PeerRepository
from database_module.Tables import create_peer_table


class RegistrationPeerMiddleware(BaseMiddleware[Message]):

    async def pre(self):
        peerID = self.event.peer_id
        ######################################### DB ########################################
        await PeerRepository(peerID).create_settings_peer()  # Стандартные настройки чатов
        await create_peer_table(peer=peerID) # Создание динамических таблиц (для хранения данных для каждого чата)
        mRepo = MarkovRepository(self.event.peer_id)
        await mRepo.add_to_history(message=self.event.text)

