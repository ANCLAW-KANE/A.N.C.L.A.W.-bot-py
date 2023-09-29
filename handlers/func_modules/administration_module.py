
from vkbottle import VKAPIError
from online_tools import GetMembers, kick, get_leave_users
from tools import Patterns,check_dict_key,check_index,parse_time
from sessions import api_group
from CONFIG import IdGroupVK
from enums import Commands
from database_module.peer_repo import PeerRepository

class Administration:
    def __init__(self):
        pass

    async def ban(self,reply):
        try:
            if reply: 
                await  kick(chat=self.obj.chat_id, user=reply.from_id,member=reply.from_id)
            else:
                ids = Patterns.get_mentions(self.string_args)
                if ids['users'] != [] or ids["invert_ids_clubs"] != []:
                    for i in ids['users'] + ids["invert_ids_clubs"]:
                        await kick(chat=self.obj.chat_id, user=i['id'],member=i['id'])  
        except VKAPIError as e: self.send_msg.msg = f"НЕЛЬЗЯ МУДИЛА \n{e}"

    async def ban_deleting(self):
        users = await api_group.messages.get_conversation_members(
            peer_id=self.obj.peer_id, group_id=IdGroupVK,fields=['deactivated'])
        deleting = [user.id for user in users.profiles if user.deactivated]
        for i in deleting: await kick(chat=self.obj.chat_id, user=i,member=i)

    async def leave(self):
        leaves = await get_leave_users(self.peer)
        for i in leaves: await kick(chat=self.obj.chat_id, user=i,member=i)


#######################################/кик ######################################
    async def manager_kick(self):
        self.Members = (await GetMembers(self.peer))
        if self.fromid in self.Members['admins'] or self.fromid in self.EVIL_GODS:
            reply = self.reply if self.reply else False
            comm = {
                Commands.deleted.value: (self.ban_deleting,()),
                Commands.leaves.value : (self.leave,())
            }
            key = check_dict_key(comm, check_index(self.list_args,0))
            if key: await key[0](*key[1])
            else: await self.ban(reply=reply)
        else: self.send_msg.msg = "Ты не админ"

    async def _exec_mute(self,user):
        time = None
        if user in self.Members['members']:
            m = PeerRepository(self.peer)
            time = parse_time(self.string_args)
            msg = await m.set_mute(user, time['calc_time'])
        else: msg = "Вы не можете дать мут этому участнику"
        return msg, time


    async def manager_mute(self):
        self.Members = (await GetMembers(self.peer))
        if self.fromid in self.Members['admins'] or self.fromid in self.EVIL_GODS: 
            reply = self.reply if self.reply else False
            msg = None
            if reply and self.args_len >= 1: 
                msg = await self._exec_mute(self.reply.from_id)
            elif Patterns.pattern_bool(self.string_args, 
                    [Patterns.club_pattern, Patterns.user_pattern],'or') and self.args_len >= 1:
                msg = await self._exec_mute(self.id)
            if msg:
                self.send_msg.msg = f"Время мута для пользователя - {self.name} - {msg[1]['calc_time']}"\
                    if msg[0] is None else msg[0]       
        else: self.send_msg.msg = "Ты не админ"