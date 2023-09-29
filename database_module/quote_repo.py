from database_module.Tables import DynamicsTables, quotesDB,DBexec,Executor_with_access,strings
from sqlalchemy import select, insert, delete, update
from tools import Formatter,check_index

class QuoteRepository:

    def __init__(self,peer,fromid=None):
        self.peer = peer
        self.fromid = fromid

    async def get_quotes(self):
        tq = await DynamicsTables(self.peer).tableQuotes()
        return await DBexec(quotesDB,select(tq.c.quote)).dbselect()
    
    async def list_quotes(self):
        tq = await DynamicsTables(self.peer).tableQuotes()
        l = await DBexec(quotesDB,select(tq.c.id,tq.c.quote)).dbselect()
        if l: return Formatter.separator_list(l,'-')
        else: return "Нет данных"

    async def add_quote(self,quote,msg,access):
        tq = await DynamicsTables(self.peer).tableQuotes()
        quote = check_index(quote,1)
        if quote: return await Executor_with_access(quotesDB, 
            insert(tq).values(quote=quote).prefix_with('OR IGNORE'),self.fromid,msg,access).exec()
        else: return "Операция не выполнена, проверьте аргументы."

    async def del_quote(self,ids,msg,access):
        tq = await DynamicsTables(self.peer).tableQuotes()
        ids = check_index(ids,1)
        if ids: return await Executor_with_access(quotesDB,
            delete(tq).where(tq.c.id.in_(Formatter.str_to_int_iter(ids))),self.fromid,msg,access).exec()
        else: return self.strings['delete_ids']
        
    async def clear_data(self,msg,access):
        tq = await DynamicsTables(self.peer).tableQuotes()
        return await Executor_with_access(quotesDB,delete(tq),self.fromid,msg,access).exec()
    
    async def update_quote(self,id,quote,msg,access):
        tq = await DynamicsTables(self.peer).tableQuotes()
        id = check_index(id,2)
        quote = check_index(quote,1)
        if id:
            if quote:
                return await Executor_with_access(quotesDB,update(tq).values(quote=quote).where(tq.c.id==id),
                                                    self.fromid,msg,access).exec()
            else: return "Операция не выполнена, проверьте аргументы."
        else: return strings['update_words']