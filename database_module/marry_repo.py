from database_module.Tables import peerDB, DBexec , Marry, Peers
from sqlalchemy import select, and_, or_, delete, update
from itertools import chain
from sqlalchemy.dialects.postgresql import insert

class MarryRepository:

    def __init__(self,peer,fromid):
        self.peer = peer
        self.fromid = fromid
    ######################################## Select ######################################

    async def get_married_from_ids(self):
        ids = await DBexec(peerDB, select(Marry.man1,Marry.man2).filter(
            and_(Marry.peer_id == self.peer,
                    or_(Marry.man1 == self.fromid,Marry.man2 == self.fromid)))).dbselect()
        return list(chain.from_iterable(ids)).count(self.fromid)

    async def awaited_marry(self):
        return await DBexec(peerDB, select(Marry.man1name, Marry.man2name).where(
            and_(Marry.allow == 0, Marry.await_state == 1,Marry.peer_id == self.peer))).dbselect()
    
    async def marry_all_allow(self):
        return await DBexec(peerDB, select(Marry.man1name, Marry.man2name).where(
            Marry.allow == 1, Marry.peer_id == self.peer)).dbselect()

    
    async def marry_allow(self):
        return await DBexec(peerDB, select(Marry.man1name, Marry.man2name).where(
                          and_(or_(Marry.man1 == self.fromid, Marry.man2 == self.fromid),
                          Marry.allow == 1, Marry.peer_id == self.peer))).dbselect()
    
    async def peer_params_marry(self,selfid):
        params = await DBexec(peerDB,select(Marry.allow,Marry.await_state).where(
            and_(Marry.peer_id == self.peer,or_(
                    and_(Marry.man1 == self.fromid, Marry.man2 == selfid),
                    and_(Marry.man1 == selfid, Marry.man2 == self.fromid))))).dbselect(DBexec.FETCH_LINE)
        print(f"PA {params}")
        if params: return {"await":params[1],"allow": params[0]}
        else: return params

    async def get_polygam_marry(self):
        return await DBexec(peerDB,select(Peers.poligam_marry).where(Peers.peer_id == self.peer)).dbselect(DBexec.FETCH_ONE)

    async def params_marry_control(self,kb):
        fetch = await DBexec(peerDB,select(Marry).where(
            Marry.peer_id == self.peer,Marry.man1 == kb, Marry.man2 == self.fromid)).dbselect()
        params = fetch[0][0] if fetch else None
        if params: return{
            "peer_id": params.peer_id,
            "man1": params.man1,
            "man2": params.man2,
            "man1name": params.man1name,
            "man2name": params.man2name,
            "allow": params.allow,
            "await_state": params.await_state,
        }
        else:return None

    ######################################## Editor #######################################
    async def marry_accept(self,kb):
        await DBexec(peerDB, update(Marry).where(Marry.peer_id == self.peer, Marry.man1 == kb,
                                Marry.man2 == self.fromid).values(allow=1,await_state=0)).dbedit()

    async def marry_deny(self,kb):
        await DBexec(peerDB, delete(Marry).where(Marry.peer_id == self.peer,
                                         Marry.man1 == kb,Marry.man2 == self.fromid)).dbedit()

    async def clear_all_marry_fromid(self):
        await DBexec(peerDB, delete(Marry).where(
            and_(Marry.peer_id == self.peer, 
            or_(Marry.man1 == self.fromid,Marry.man2 == self.fromid)))).dbedit()

    async def create_new_marry(self,selfid,m1,m2):
        await DBexec(peerDB,insert(Marry)
                    .values(peer_id = self.peer,man1 = self.fromid,
                        man2 = selfid, man1name = m1, man2name = m2,
                        allow = 0, await_state = 1)
                    .on_conflict_do_nothing()
                ).dbedit()

    async def unmarry_fromid(self,selfid):
        await DBexec(peerDB, delete(Marry).where(and_(Marry.peer_id == self.peer, or_(
            and_(Marry.man1 == self.fromid, Marry.man2 == selfid),
            and_(Marry.man1 == selfid, Marry.man2 == self.fromid))))).dbedit()
        
    async def marry_delete_fix(self):
        await DBexec(peerDB,delete(Marry).where(or_(Marry.man1name == 'None',Marry.man1name == 'DELETED ',
                                Marry.man2name == 'None',Marry.man2name == 'DELETED '))).dbedit()
        
###############################################################################