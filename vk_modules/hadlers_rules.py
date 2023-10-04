from loguru import logger
from sqlalchemy import select
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule,OrRule
from database_module.Tables import Peers,peerDB,DBexec
from database_module.peer_repo import PeerRepository

prefixs = ['/','!','$']

class MessageNotEmpty(OrRule[Message]):
    async def check(self, m:Message)  -> bool:
        logger.log("STATE","\n___MSGNOTEMPTY___")
        return m.text != ''
    
class PrefixCommandRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            logger.log("STATE","\n___CMNDSTATUS___")
            return m.text[0] == prefixs[0]

class PrefixRoleRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            logger.log("STATE","\n___ROLESTATUS___")
            return m.text[0] == prefixs[1]

class PrefixPrevilegesRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            logger.log("STATE","\n___PRVGSTATUS___")
            return m.text[0] == prefixs[2]
    
class MessageNotCommandRule(OrRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            logger.log("STATE","\n___NOTCOMMRULE___")
            return m.text[0] not in prefixs

class MsgParamWordsRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            logger.log("STATE","\n___WORDRULE___")
            w = await DBexec(peerDB,select(Peers.words)).dbselect("one")
            return w == 1
        
class MsgParamQuoteRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            logger.log("STATE","\n___QUOTERULE___")
            q = await DBexec(peerDB,select(Peers.quotes)).dbselect("one")
            return q == 1
    
class MuteRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        logger.log("STATE","\n___MUTERULE___")
        repo = PeerRepository(m.peer_id)
        return await repo.check_id_mute(m.from_id)
    
