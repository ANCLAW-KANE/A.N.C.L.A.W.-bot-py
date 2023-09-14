from loguru import logger
from vkbottle.bot import Message , BotLabeler
from keyboards import keyboard_event
from handlers.respond_priv import privileges
from hadlers_rules import MessageNotCommandRule
from database_module.Tables import PeerRepository,create_peer_table



labeler = BotLabeler()

@labeler.message(MessageNotCommandRule(), blocking=False)
async def bot(msg: Message):
        logger.log("STATE","\n_________________________MSG_________________________")
        peerID = msg.peer_id
        ######################################### DB ########################################
                                # Стандартные настройки чатов
        await PeerRepository(peerID).create_settings_peer()
        await create_peer_table(peer=peerID)
        ######################################### Обработка ######################################
        # if FSM(from_id, peerID).check_state() != None: send_to_specific_peer(c, peerID)
        if msg.payload:await keyboard_event(msg).check_Callback()
        await privileges(txt=msg.text, sender=msg.from_id, peer=peerID, obj=msg).EVIL_GOD() #исправить
