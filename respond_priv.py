import sqlite3,traceback
from online_tools import RandomMember,getUserName,send_to_specific_peer,Invertor
from tools import json_gen,logger
from sessions import vk
from CONFIG import IdGroupVK
######################################################################################################
class privileges(object):
    def __init__(self, txt, sender, peer, obj):
        self.txt = txt
        self.sender = sender
        self.peer = peer
        self.obj = obj
        self.cnvmgid = self.obj['conversation_message_id']
        self.EVIL_GODS = json_gen().return_config_file_json()['EVIL_GODS']
    ################## привелегия для удаления сообщений не админов(ультимативный мут) #################
    def EVIL_GOD(self):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.peer}")
        E_G = edit.fetchone()
        try:
            if self.sender not in self.EVIL_GODS :
                if E_G[1] == '1': vk.messages.delete(peer_id=self.peer,conversation_message_ids=self.cnvmgid,
                                   group_id=IdGroupVK,delete_for_all=1)
                if E_G[3] == '1':
                    vk.messages.delete(peer_id=self.peer, conversation_message_ids=self.cnvmgid,
                                       group_id=IdGroupVK, delete_for_all=1)
                    send_to_specific_peer(f"{getUserName(self.sender)} *Впечатан в землю*", self.peer)
                if E_G[4] == '1':
                    send_to_specific_peer(f"{RandomMember(self.peer)} насилует {RandomMember(self.peer)}", self.peer)
            BD.close()
        except:
            logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
            BD.close()

    ######################################################################################################
    def check(self):
        if self.sender in self.EVIL_GODS:
            p=[f"SELECT * FROM peers WHERE peer_id = {self.peer}",self.peer,"UPDATE peers SET "," = ? where peer_id = ?"]
            privilege = {
            '*присутствие злого бога*': Invertor(p[0],'Безмолвие','*Уходит*', p[1], f"{p[2]} e_g_mute {p[3]}",1,str,p[1]).key,
            '*ваши головы подняты слишком высоко*': Invertor(p[0],'*Раздавлены*','*Уходит*',p[1],f"{p[2]} e_g_head {p[3]}",3,str,p[1]).key,
            '*адская похоть*': Invertor(p[0],'Исполнено','*Уходит*',p[1],f"{p[2]} e_g_ex {p[3]}",4,str,p[1]).key,
            }
            if self.txt in privilege:
                key = privilege.get(self.txt)
                if key is not None: key()
            elif self.txt == '* EVIL GOD *':
                mess = f'Доступно только админам бота\n______________________________\n'
                for z in list(privilege):
                    mess += f"🔥 {z} 🔥\n\n"
                send_to_specific_peer(f"{mess}", self.peer)


######################################################################################################
