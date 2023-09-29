from database_module.Tables import DynamicsTables, wordsDB,DBexec,Executor_with_access,strings
from sqlalchemy import select, insert, delete, update
from tools import Formatter,check_index

class WordRepository:

    def __init__(self,peer,fromid=None):
        self.peer = peer
        self.fromid = fromid
        

    async def get_words(self):
        tw = await DynamicsTables(self.peer).tableWords() 
        return await DBexec(wordsDB,select(tw.c.key,tw.c.val)).dbselect() 
    
    async def list_words(self):
        tw = await DynamicsTables(self.peer).tableWords()
        l = await DBexec(wordsDB,select(tw)).dbselect()
        if l: return Formatter.separator_list(l,'-')
        else: return "Нет данных"
    
    async def add_word(self,words,msg,access):
        tw = await DynamicsTables(self.peer).tableWords()
        if words and len(words) == 3: return await Executor_with_access(wordsDB, insert(tw).values(
            key=words[1],val=words[2]).prefix_with('OR IGNORE'),self.fromid,msg,access).exec()
        else: return "Операция не выполнена, проверьте аргументы."

    async def del_word(self,ids,msg,access):
        tw = await DynamicsTables(self.peer).tableWords()
        ids = check_index(ids,1)
        if ids: return await Executor_with_access(wordsDB,delete(tw).where(tw.c.id.in_(Formatter.str_to_int_iter(ids))),self.fromid,msg,access).exec()
        else: return self.strings['delete_ids']
        
    async def clear_data(self,msg,access):
        tw = await DynamicsTables(self.peer).tableWords()
        return await Executor_with_access(wordsDB,delete(tw),self.fromid,msg,access).exec()
    
    async def update_word(self,lines,word,msg,access):
        tw = await DynamicsTables(self.peer).tableWords()
        w = check_index(word,2)
        if w:
            if lines and len(lines) == 2: return await Executor_with_access(wordsDB,update(tw).where(
                tw.c.id == w).values(val=lines[1]).prefix_with('OR IGNORE'),self.fromid,msg,access).exec()
            else: return "Операция не выполнена, проверьте аргументы."
        else: strings['update_words']
###############################################################################