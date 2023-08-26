from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule,OrRule

prefixs = ['/','!','*']

class MessageNotEmpty(OrRule[Message]):
    async def check(self, m:Message)  -> bool:
        print("___MSGNOTEMPTY___")
        return m.text != '' or None
    
class PrefixCommandRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            print("___CMNDSTATUS___")
            return m.text[0] == prefixs[0]

class PrefixRoleRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            print("___ROLESTATUS___")
            return m.text[0] == prefixs[1]

class PrefixPrevilegesRule(ABCRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            print("___PRVGSTATUS___")
            return m.text[0] == prefixs[2]
    
class MessageNotCommandRule(OrRule[Message]):
    async def check(self, m:Message)  -> bool:
        if m.text != '' or None:
            print("___NOTCOMMRULE___")
            return m.text[0] not in prefixs
    

    
