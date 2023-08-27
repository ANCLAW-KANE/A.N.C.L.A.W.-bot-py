from loguru import logger
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule,OrRule

prefixs = ['/','!','*']

class MessageNotEmpty(OrRule[Message]):
    async def check(self, m:Message)  -> bool:
        logger.log("STATE","\n___MSGNOTEMPTY___")
        return m.text != '' or None
    
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
    

    
