
from vkbottle import DocMessagesUploader
from CONFIG import ADMIN_JSON_CONFIG
from database_module.peer_repo import PeerRepository
from online_tools import  GetMembers
from tools import Patterns, Writer, data_msg,json_config,Formatter,unpack_keys
from sessions import api_group, vb
from database_module.cabal_repo import CabalRepository


class base_config:
    def __init__(self):
        self.data = json_config()
        self.send_msg = data_msg()
        self.types = {
                'int': int,
                'string': str,
                'bool': bool
                }
        self.crud = {
            'set': self.data.input_key ,
            'extend' : self.data.extend_key_list,
            'delete' : self.data.delete_key_list
        }

    
    ######################################################################################################
    async def edit(self):
        data_keys = json_config().get_key_list()
        if self.args_len == 5 and self.list_args[1] in data_keys and\
            self.list_args[2] in self.types and self.list_args[3] in self.crud:
            parametr = self.list_args[1]
            type_ = self.types.get(self.list_args[2])
            crud = self.crud.get(self.list_args[3])
            data = self.list_args[4]
            try:
                crud(parametr,data,type_)
                self.send_msg.msg = f"Запрос :\n {self.list_args[3]} "\
                f"{self.list_args[2]} {parametr} = {data}  выполнен успешно."
            except:
                self.send_msg.msg = f"Запрос :\n {self.list_args[3]} "\
                f"{self.list_args[2]} {parametr} = {data}  не выполнен, проверьте аргументы."
        else:
            self.send_msg.msg = f"Данные не корректны. Шаблон : /cabal json-edit <Param> <type> <operation> <value>"

    ######################################################################################################
    async def show(self):
        msg = ''
        for e in self.data.db['sys']: msg += f"{e} : {self.data.db['sys'].get(e)}\n"
        self.send_msg.msg = msg

    ######################################################################################################



class Cabal(base_config):

    def __init__(self) -> None:
        self.EVIL_GODS = json_config().read_key('sys','EVIL_GODS')
        base_config.__init__(self)
        
    async def show_cabal_settings(self):
        if self.args_len == 2 and Patterns.pattern_bool(self.list_args[1],[Patterns.chat_id_pattern]):
            opt = await PeerRepository(self.list_args[1]).get_params_peer()
        else: opt = await PeerRepository(self.peer).get_params_peer()
        for key in opt: opt[key] = Formatter.emojy_format(opt[key])
        self.send_msg.msg = f"🆔 : {opt['peer_id']} \n " \
                       f"☢ ️Ультимативный режим(на админки не действует): {opt['e_g_mute']}\n" \
                       f"☢️ Ультимативный режим(ролевой): {opt['e_g_head']}\n" \
                       f"🍆 Режим рандомного изнасилования: {opt['e_g_ex']}\n" \
                       f"📡 R.E.D.-модуль: {opt['resend']}\n" \
                       

    #################################### переключатель для resend ###################################
    async def global_resend_toggle(self):
        if self.args_len == 2 and Patterns.pattern_bool(self.list_args[1], [Patterns.chat_id_pattern]):
                self.send_msg.msg = await CabalRepository(self.list_args[1]).toggle_resend()
        elif self.args_len == 1:
            self.send_msg.msg = await CabalRepository(self.peer).toggle_resend()

    

    #################################### менеджер соединений ###################################
    async def edit_node(self):
        if self.fromid in self.EVIL_GODS and self.args_len >= 2:
            cRepo = CabalRepository(self.peer)
            len_word_list = (self.args_len,self.list_args[1])
            peer_arg = self.list_args[2] if self.args_len >= 3 else None
            cRepoPermID = CabalRepository(peer_arg)
            nodes = {
                (4,   'create'): (cRepo.create_node,(self.list_args, "Создано")),
                (3,   'delete'): (cRepo.delete_node,(self.list_args, "Удалено")),
                (4,   'update'): (cRepo.update_node,(self.list_args, "Обновлено")),
                (2,     'list'): (cRepo.nodes,()),
                (2, 'allow-vk'): (cRepo.toggle_vk_tg,()),
                (2, 'allow-tg'): (cRepo.toggle_tg_vk,()),
                (3, 'allow-vk'): (cRepoPermID.toggle_vk_tg,()),
                (3, 'allow-tg'): (cRepoPermID.toggle_tg_vk,())
            }
            if len_word_list in nodes:
                key = nodes.get(len_word_list)
                self.send_msg.msg = await key[0](*key[1])
                

    
    async def KILL_ALL_MEMBERS(self):
        self.Members = (await GetMembers(self.peer))
        for i in self.Members['members']: 
            await api_group.messages.remove_chat_user(chat_id=self.obj.chat_id, user_id=i, member_id=i)

    async def download_log(self):
        path = await Writer.create_bytes_archive(Writer.create_list_zip('./logs'))
        doc = DocMessagesUploader(vb.api)
        self.send_msg.attachment = await doc.upload(f'logs-{self.peer}.zip',path , peer_id = self.peer)

    async def cabal_module(self):
        if self.args_len and self.args_len >= 1 and self.fromid in ADMIN_JSON_CONFIG:
            cab_com = {
                'kill_all_members=active': self.KILL_ALL_MEMBERS,
                'log':          self.download_log,
                'json-edit':    self.edit,
                'json-show':    self.show,
                'toggle_red':   self.global_resend_toggle,
                'node':         self.edit_node,
                'settings':     self.show_cabal_settings
                }
            key = cab_com.get(self.list_args[0])
            if key is not None: await key()
            if self.list_args[0] == '-c':
                self.send_msg.msg = '/cabal:\n'
                self.send_msg.msg += unpack_keys(cab_com,'⚠')