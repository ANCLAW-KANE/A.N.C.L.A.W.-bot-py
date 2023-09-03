
import random
from sqlalchemy import select
from vkbottle.bot import Message , BotLabeler
from database_module.Tables import DynamicsTables, Peers, wordsDB ,quotesDB , peerDB, DBexec
from hadlers_rules import MessageNotCommandRule,MsgParamQuoteRule,MsgParamWordsRule
from vkbottle.dispatch.rules import AndRule
from online_tools import send
from tools import data_msg

labeler = BotLabeler()


@labeler.message(AndRule(MessageNotCommandRule(),MsgParamWordsRule()),blocking=False)#   Шаблонные ответы
async def words_handler(m:Message):
    tw = await DynamicsTables(m.peer_id).tableWords()  # объект динамической таблицы '{peerID}'
    words_BD = await DBexec(wordsDB,select(tw.c.key,tw.c.val)).dbselect()  #f"SELECT key,val FROM '{peerID}' "
    if words_BD is not None:
        DictWords = dict([word for word in words_BD])
        DictKeys = list(DictWords.keys())
        TextSplitLowerDict = set('')
        lines = str(m.text).lower().splitlines()
        if lines: TextSplitLowerDict = set(lines[0].split())
        words_msg = lines if set(lines) & set(DictKeys) else TextSplitLowerDict
        w = [DictWords.get(element) for element in words_msg if DictWords.get(element) is not None]
        data_msg.msg = random.choice(w) if w else None
        await send(m)

@labeler.message(AndRule(MessageNotCommandRule(),MsgParamQuoteRule()),blocking=False)
async def quotes_handler(m:Message):
    tq = await DynamicsTables(m.peer_id).tableQuotes()
    #f"SELECT count_period FROM peers WHERE peer_id = {peerID}" # Частота рандомных ответов
    count_period = await DBexec(peerDB,select(Peers.count_period).where(Peers.peer_id == m.peer_id)).dbselect("one")
    quotes = await DBexec(quotesDB,select(tq.c.quote)).dbselect() #f"SELECT quote FROM '{peerID}'"
    if random.randint(0, 100) < count_period and quotes:
        data_msg.msg = random.choice(quotes)[0]
        await send(m)
