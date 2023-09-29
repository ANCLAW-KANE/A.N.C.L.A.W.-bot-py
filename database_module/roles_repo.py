from database_module.Tables import DynamicsTables, rolesDB,DBexec,Executor_with_access,strings
from sqlalchemy import select, insert, delete, update
from tools import Formatter,check_index

class RoleRepository:

    def __init__(self,peer,fromid):
        self.peer = peer
        self.fromid = fromid
    
    async def check_roles(self):
        tR = await DynamicsTables(self.peer).tableRoles()
        return await DBexec(rolesDB,select(tR.c.command)).dbselect('one')

    async def get_roles(self,word_comm):
        tR = await DynamicsTables(self.peer).tableRoles()
        return await DBexec(rolesDB,select(tR.c.emoji_1, tR.c.txt, tR.c.emoji_2).where(
                tR.c.command == word_comm)).dbselect("line")
    
    async def create_role(self,args,msg,access):
        tR = await DynamicsTables(self.peer).tableRoles()
        if args and len(args) == 5:
            return await Executor_with_access(rolesDB,insert(tR).values(command=args[1].lower(),emoji_1=args[2],txt=args[3],
                            emoji_2=args[4]).prefix_with('OR IGNORE'),self.fromid,msg,access).exec()
        else: return strings['update_roles']
        
    async def del_role(self,ids,msg,access):
        tR = await DynamicsTables(self.peer).tableRoles()
        ids = check_index(ids,1)
        if ids: return await Executor_with_access(rolesDB,delete(tR).where(
            tR.c.id.in_(Formatter.str_to_int_iter(ids))),self.fromid,msg,access).exec()
        else: return self.strings['delete_ids']
        
    async def clear_data(self,msg,access):
        tR = await DynamicsTables(self.peer).tableRoles()
        return await Executor_with_access(rolesDB,delete(tR),self.fromid,msg,access).exec()
    
    async def update_role(self,args,msg,access):
        tR = await DynamicsTables(self.peer).tableRoles()
        if args and len(args) == 5:
            return await Executor_with_access(rolesDB,update(tR).where(
                tR.c.command == args[1].lower()).values(emoji_1=args[2],txt=args[3],
                            emoji_2=args[4]).prefix_with('OR IGNORE'),self.fromid,msg,access).exec()
        else: return strings['update_roles']

    async def list_roles(self):
        tR = await DynamicsTables(self.peer).tableRoles()
        l = await DBexec(rolesDB,select(tR.c.id,tR.c.command,tR.c.emoji_1,tR.c.txt,tR.c.emoji_2)).dbselect()
        if l: return Formatter.separator_list(l,'-')
        else: return "Нет данных"
###############################################################################

