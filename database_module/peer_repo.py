from database_module.Tables import DBmanager, peerDB, DBexec , Nicknames,Peers,Mutes
from sqlalchemy import delete, select, insert, update
from datetime import datetime

class PeerRepository:
    def __init__(self,peer,fromid=None):
        self.peer = peer
        self.fromid = fromid

    async def create_settings_peer(self):
        await DBexec(peerDB,insert(Peers).values(
                peer_id=self.peer, 
                e_g_mute = 0, 
                e_g_head = 0,
                e_g_ex = 0, 
                resend = 1, 
                poligam_marry = 1, 
                words = 1,
                g_txt = 0,
                g_dem = 0,
                g_ldem = 0,
                g_sticker = 0
            ).prefix_with('OR IGNORE')).dbedit()
        
    async def check_nick(self):
        return await DBexec(peerDB,select(Nicknames.nickname).where(
            Nicknames.peer_id == self.peer,Nicknames.user_id == self.fromid)).dbselect("line")

    async def set_nickname(self,nick):
        print(await self.check_nick())
        if await self.check_nick():
            print("UPD")
            await DBexec(peerDB,update(Nicknames).where(
                Nicknames.peer_id == self.peer,Nicknames.user_id == self.fromid).values(nickname=nick)).dbedit()
        else: 
            print("INS")
            await DBexec(peerDB,insert(Nicknames).values(peer_id = self.peer, user_id = self.fromid, 
                    nickname = nick).prefix_with('OR IGNORE')).dbedit()
            
    #async def get_count(self):
    #    return await DBexec(peerDB,select(Peers.&&&&&).where(Peers.peer_id == self.peer)).dbselect("one")
    
    async def toggle_marry(self):
        return await DBmanager(peerDB, Peers, Peers.poligam_marry, Peers.peer_id == self.peer, ['Полигамный брак разрешен',
                                                                            'Полигамный брак запрещен']).key("poligam_marry")
    
    async def toggle_word(self):
        return await DBmanager(peerDB, Peers, Peers.words, Peers.peer_id == self.peer, ['Шаблоны (слова) включены',
                                                                            'Шаблоны (цитаты) выключены']).key("words")

    async def get_params_peer(self):
        fetch = await DBexec(peerDB,select(Peers).where(Peers.peer_id == self.peer)).dbselect()
        params = fetch[0][0] if fetch else None
        if params: return{
            "peer_id": params.peer_id,
            "e_g_mute": params.e_g_mute,
            "e_g_head": params.e_g_head,
            "e_g_ex": params.e_g_ex,
            "resend": params.resend,
            "poligam_marry": params.poligam_marry,
            "words": params.words,
            "g_txt": params.g_txt,
            "g_dem": params.g_dem,
            "g_ldem": params.g_ldem,
            "g_stck": params.g_sticker
        }
        else:return None

    async def g_txt(self,count):
        await DBexec(peerDB,update(Peers).where(Peers.peer_id == self.peer).values(g_txt=count)).dbedit()

    async def g_dem(self,count):
        await DBexec(peerDB,update(Peers).where(Peers.peer_id == self.peer).values(g_dem=count)).dbedit()

    async def g_ldem(self,count):
        await DBexec(peerDB,update(Peers).where(Peers.peer_id == self.peer).values(g_ldem=count)).dbedit()

    async def g_stck(self,count):
        await DBexec(peerDB,update(Peers).where(Peers.peer_id == self.peer).values(g_sticker=count)).dbedit()

    async def check_id_mute(self,user):
        date_mute = await DBexec(peerDB,select(Mutes.data_end).where(
            Mutes.peer_id == self.peer, Mutes.user_id == user)).dbselect("one")
        if date_mute: return datetime.now().replace(second=0,microsecond=0) < date_mute
        else: return False 

    async def check_unmute(self):
        ids = await DBexec(peerDB,select(Mutes).where(
            Mutes.data_end < datetime.now().replace(second=0,microsecond=0))).dbselect()
        if ids:
            peers = [(peer[0].peer_id,peer[0].user_id) for peer in ids]
            result = {chat_id: [] for chat_id, _ in peers}
            [result[chat_id].append(user_id) for chat_id, user_id in peers]
            return {
            'delete_ids' : [id[0].id for id in ids],
            'peers' : result
            }

    async def unmute(self,ids):
        await DBexec(peerDB,delete(Mutes).where(Mutes.id.in_(ids))).dbedit()

    async def set_mute(self,user,mute):
        if await self.check_id_mute(user) == False:
            await DBexec(peerDB,insert(Mutes).values(peer_id=self.peer, user_id = user, data_end=mute)).dbedit()
        else: return "Такой пользователь уже заблокирован"

    