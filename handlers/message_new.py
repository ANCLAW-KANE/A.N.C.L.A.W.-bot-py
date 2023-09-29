from loguru import logger
from vkbottle.bot import Message , BotLabeler
from vkbottle.dispatch.rules.base import PeerRule, FromUserRule
from handlers.kb_handlers.keyboard_handler import keyboard_event
from handlers.respond_priv import privileges
from hadlers_rules import MessageNotCommandRule,MuteRule
from sessions import api_group
from database_module.markov_repo import MarkovRepository
from markov.generators import Generator

labeler = BotLabeler()


@labeler.message(MuteRule(), blocking=True)
async def mute(msg: Message):
    logger.log("STATE","\n_________________________Check_mute_________________________")
    await api_group.messages.delete(peer_id=msg.peer_id,delete_for_all=True, cmids=msg.conversation_message_id)
        

@labeler.message(MessageNotCommandRule(), blocking=False)
async def bot(msg: Message):
        logger.log("STATE","\n_________________________MSG_________________________")
        # if FSM(from_id, peerID).check_state() != None: send_to_specific_peer(c, peerID)
        if msg.payload: await keyboard_event(msg).check_Callback()
        await privileges(txt=msg.text, fromid=msg.from_id, peer=msg.peer_id, obj=msg).EVIL_GOD() #исправить


@labeler.message(MessageNotCommandRule(),FromUserRule(),PeerRule(), blocking=False)
async def markov_data(message: Message) -> None:
    logger.log("STATE","\n_________________________MARKOV_________________________")
    mRepo = MarkovRepository(message.peer_id)
    #if random.random() * 100 > cfg.response_chance: #шансы сделать
    #    return
    history = await mRepo.get_history()
    print(history)
    response = await Generator(msg = history).generate_text()
    #await asyncio.sleep(cfg.response_delay)
    await message.answer(response)
        

"""from cachetools import TTLCache


cache = TTLCache(maxsize=100, ttl=60)

def get_data_from_database(key):


def get_data(key):
    
    if key in cache:
        return cache[key]
    else:
        data = get_data_from_database(key)
        cache[key] = data
        return data

def update_data(key):
    data = get_data_from_database(key)
    cache[key] = data

# Пример использования
data1 = get_data("key1")  # Если данных нет в кеше, они будут получены из базы данных
print(data1)

# Допустим, данные в базе данных были обновлены
update_data("key1")

# При следующем запросе данные будут получены из кеша, так как они были обновлены
data2 = get_data("key1")
print(data2)"""