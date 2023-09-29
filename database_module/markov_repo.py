from typing import List
from sqlalchemy import insert , select, delete
from database_module.Tables import DBexec,markovDB, DynamicsTables
from itertools import chain

class MarkovRepository:
    def __init__(self,peer):
        self.peer = peer

    async def get_history(self) -> List[str]:
        mt = await DynamicsTables(self.peer).tableMarkov()
        print(mt.name)
        txt = await DBexec(markovDB,select(mt.c.txt)).dbselect()
        return list(chain.from_iterable(txt))

    async def add_to_history(self,message: str) -> None:
        try:
            if message == "": return
            mt = await DynamicsTables(self.peer).tableMarkov()
            await DBexec(markovDB,insert(mt).values(txt=message)).dbedit()
        except:
            pass

    async def clean_history(self) -> None:
        mt = await DynamicsTables(self.peer).tableMarkov()
        await DBexec(markovDB,delete(mt)).dbedit()