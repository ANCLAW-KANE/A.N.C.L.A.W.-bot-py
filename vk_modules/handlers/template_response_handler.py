
import random
from vkbottle.bot import Message , BotLabeler
from database_module.words_repo import WordRepository 
from vk_modules.hadlers_rules import MessageNotCommandRule,MsgParamWordsRule
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
