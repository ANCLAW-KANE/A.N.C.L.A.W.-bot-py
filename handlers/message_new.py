import json
from loguru import logger
from vkbottle.bot import Message , BotLabeler
from sqlalchemy import insert
from keyboards import keyboard_event
from online_tools import send
from handlers.respond_priv import privileges
from tools import data_msg
from hadlers_rules import MessageNotCommandRule
from database_module.Tables import Peers,create_peer_table,peerDB,DBexec
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session


labeler = BotLabeler()

@labeler.message(MessageNotCommandRule(), blocking=False)
async def bot(msg: Message):
    logger.log("STATE","\n_________________________MSG_________________________")
    peerID = msg.peer_id
    ######################################### DB ########################################
                                # Стандартные настройки чатов
    await DBexec(peerDB,insert(Peers).values(peer_id=peerID, count_period=0, e_g_mute = 0, e_g_head = 0,
            e_g_ex = 0, resend = 1, poligam_marry = 1, quotes = 1 , words = 1).prefix_with('OR IGNORE')).dbedit()
    await create_peer_table(peer=peerID)
    ######################################### Обработка ######################################
    # if FSM(from_id, peerID).check_state() != None: send_to_specific_peer(c, peerID)
    if msg.payload: await keyboard_event(json.loads(msg.payload), msg).check_event_msg()#исправить
    await privileges(txt=msg.text, sender=msg.from_id, peer=peerID, obj=msg).EVIL_GOD() #исправить
    print(data_msg.msg)
    await send(msg)
