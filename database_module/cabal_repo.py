
from sqlalchemy import delete, select, update
from database_module.Tables import DBexec, DBmanager, Nodes, Peers,peerDB
from tools import Formatter, Patterns
from sqlalchemy.dialects.postgresql import insert

class CabalRepository:

    def __init__(self,peer,fromid=None):
        self.peer = peer
        self.fromid = fromid

    async def toggle_resend(self):
        return await DBmanager(peerDB, Peers, Peers.resend, Peers.peer_id == self.peer, 
                               ['Глобальная отправка сообщений включена',
                                'Глобальная отправка сообщений отключена']).key("resend")
    
    async def nodes(self):
        fetch = (await DBexec(peerDB,select(Nodes)).dbselect())
        if fetch:
            msg = f'|____ вк чат ____|____телеграм чат____||| Разрешения адресации\n' \
                       f'|=============|==================|||=========|==========\n'
            for o in range(len(fetch)):
                vk_tg_allow = Formatter.emojy_format(fetch[o][0].vk_tg_allow)
                tg_vk_allow = Formatter.emojy_format(fetch[o][0].tg_vk_allow)
                msg += f"| VK: {fetch[o][0].peer_id} | TG: {fetch[o][0].tg_id} ||| VK>TG: " \
                            f"{vk_tg_allow}| TG>VK:{tg_vk_allow}\n"
            return msg
        else: return "Ничего нет"
        
    async def create_node(self,values,msg):
        if values and len(values) == 4 and Patterns.pattern_bool(values[2],[Patterns.chat_id_pattern])\
        and Patterns.pattern_bool(values[3],[Patterns.id_telegram_chat_pattern]):
            await DBexec(peerDB,insert(Nodes)
                            .values(peer_id=values[2], tg_id=values[3],
                                tg_vk_allow=1 ,vk_tg_allow=1)
                            .on_conflict_do_nothing()
                        ).dbedit()
            return msg
        else: return "Операция не выполнена, проверьте аргументы."

    async def delete_node(self,values,msg):
        if values and len(values) == 3 and Patterns.pattern_bool(values[2],[Patterns.chat_id_pattern]):
            await DBexec(peerDB,delete(Nodes).where(Nodes.peer_id == values[2])).dbedit()
            return msg
        else: return "Операция не выполнена, проверьте аргументы."

    async def update_node(self,values,msg):
        if values and len(values) == 4 and Patterns.pattern_bool(values[2],[Patterns.chat_id_pattern])\
        and Patterns.pattern_bool(values[3],[Patterns.id_telegram_chat_pattern]):
            await DBexec(peerDB,update(Nodes).where(Nodes.peer_id == values[2]).values(
                tg_id=values[3]).prefix_with('OR IGNORE')).dbedit()
            return msg
        else: return "Операция не выполнена, проверьте аргументы."

    async def toggle_vk_tg(self):
        print(self.peer)
        return await DBmanager(peerDB, Nodes, Nodes.vk_tg_allow, Nodes.peer_id == self.peer, 
                               [f'Отправка сообщений для {self.peer} в телеграмм включена',
                                f'Отправка сообщений для {self.peer} в телеграмм отключена']).key("vk_tg_allow")
    
    async def toggle_tg_vk(self):
        return await DBmanager(peerDB, Nodes, Nodes.tg_vk_allow, Nodes.peer_id == self.peer, 
                               [f'Отправка сообщений из телеграмм в {self.peer} включена',
                                f'Отправка сообщений из телеграмм в {self.peer} отключена']).key("tg_vk_allow")

    async def priveleges_get(self):
        p = await DBexec(peerDB,select(Peers.e_g_ex,Peers.e_g_head,Peers.e_g_mute).where(
            Peers.peer_id == self.peer)).dbselect(DBexec.FETCH_LINE)
        
        return {
            "e_g_ex": p[0],
            "e_g_head": p[1],
            "e_g_mute": p[2]
        }
    
    async def set_priveleges_mute(self):
        return await DBmanager(peerDB, Peers, Peers.e_g_mute, Peers.peer_id == self.peer, 
                               ['Безмолвие','*Безмолвие Уходит*']).key("e_g_mute")

    async def set_priveleges_head(self):
        return await DBmanager(peerDB, Peers, Peers.e_g_head, Peers.peer_id == self.peer, 
                               ['*Раздавлены*','Гравитация отключена']).key("e_g_head")
    
    async def set_priveleges_ex(self):
        return await DBmanager(peerDB, Peers, Peers.e_g_ex, Peers.peer_id == self.peer, 
                               ['Исполнено Похоть','*Похоть развеяна*']).key("e_g_ex")