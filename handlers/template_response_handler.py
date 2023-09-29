
import random
from vkbottle.bot import Message , BotLabeler
from database_module.words_repo import WordRepository 
from database_module.quote_repo import QuoteRepository
from database_module.peer_repo import PeerRepository
from hadlers_rules import MessageNotCommandRule,MsgParamQuoteRule,MsgParamWordsRule
from vkbottle.dispatch.rules import AndRule

from tools import data_msg


labeler = BotLabeler()


@labeler.message(AndRule(MessageNotCommandRule(),MsgParamWordsRule()),blocking=False)#   Шаблонные ответы
async def words_handler(m:Message):
    words_BD = await WordRepository(m.peer_id).get_words()
    if words_BD is not None:
        DictWords = dict([word for word in words_BD])
        DictKeys = list(DictWords.keys())
        TextSplitLowerDict = set('')
        lines = str(m.text).lower().splitlines()
        if lines: TextSplitLowerDict = set(lines[0].split())
        words_msg = lines if set(lines) & set(DictKeys) else TextSplitLowerDict
        w = [DictWords.get(element) for element in words_msg if DictWords.get(element) is not None]
        data = data_msg()
        data.msg = random.choice(w) if w else None
        await data.send(m)

@labeler.message(AndRule(MessageNotCommandRule(),MsgParamQuoteRule()),blocking=False)
async def quotes_handler(m:Message):
    count_period = await PeerRepository(m.peer_id).get_count()
    quotes = await QuoteRepository(m.peer_id).get_quotes()
    if random.randint(0, 100) < count_period and quotes:
        data = data_msg()
        data.msg = random.choice(quotes)[0]
        await data.send(m)
