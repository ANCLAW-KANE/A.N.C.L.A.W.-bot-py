from database_module.quote_repo import QuoteRepository
from database_module.peer_repo import PeerRepository
from database_module.roles_repo import RoleRepository
from database_module.words_repo import WordRepository
from online_tools import GetMembers
from tools import Formatter, Patterns,  data_msg
from enums import Commands



######################################################################################################
class manager:
    def __init__(self):
        self.len_word_list = False
        if self.args_len and self.args_len >= 1:
            self.len_word_list = (self.list_args[0],(self.len_lines,self.args_len), 
                                  self.list_args[1] if self.args_len >=2 else None)  # проверка кол-ва параметров
        self.send_msg = data_msg()

    ######################################################################################################
    async def builder_data(self):
        if self.list_args and self.args_len >= 1:
            access = await GetMembers(self.peer)
            repoQuote = QuoteRepository(self.peer,self.fromid)
            repoRoles = RoleRepository(self.peer,self.fromid)
            repoWords = WordRepository(self.peer,self.fromid)
            statements = {
                #quotes
                Commands.quote_create.value: (repoQuote.add_quote,(self.lines,"Создано",access['all_members'])),
                Commands.quote_delete.value: (repoQuote.del_quote,(self.lines,"Удалено",access['all_members'])),
                Commands.quote_kill.value  : (repoQuote.clear_data,("Данные уничтожены",access['admins'])),
                Commands.quote_update.value: (repoQuote.update_quote,(self.list_args,self.lines,"Обновлено",access['all_members'])),
                Commands.quote_list.value  : (repoQuote.list_quotes,()),
                #roles
                Commands.role_create.value : (repoRoles.create_role,(self.lines,"Создано",access['all_members'])),
                Commands.role_delete.value : (repoRoles.del_role,(self.lines,"Удалено", access['all_members'])),
                Commands.role_kill.value   : (repoRoles.clear_data,("Данные уничтожены",access['admins'])),
                Commands.role_update.value : (repoRoles.update_role,(self.lines,"Обновлено",access['all_members'])),
                Commands.role_list.value   : (repoRoles.list_roles,()),
                #words
                Commands.words_create.value: (repoWords.add_word,(self.lines,"Создано",access['all_members'])),
                Commands.words_delete.value: (repoWords.del_word,(self.lines,"Удалено",access['all_members'])),
                Commands.words_kill.value  : (repoWords.clear_data,("Очищено",access['admins'])),
                Commands.words_update.value: (repoWords.update_word,(self.lines,self.list_args,"Обновлено",access['all_members'])),
                Commands.words_list.value  : (repoWords.list_words,())
            }
            key = statements.get(self.len_word_list)
            if key : self.send_msg.msg = await key[0](*key[1])

    ######################################################################################################
    async def count(self):
        if self.args_len == 2:
            if Patterns.pattern_bool(self.list_args[1],[Patterns.chance_pattern]):
                await PeerRepository(self.peer).toggle_count(self.list_args[1])
                self.send_msg.msg = f"Значение установлено на {self.list_args[1]}"
            else: self.send_msg.msg = f"Значение должно быть 0-100 (%)"

    ######################################################################################################
    async def show_settings(self):
        opt = await PeerRepository(self.peer).get_params_peer()
        if opt: 
            for key in opt: opt[key] = Formatter.emojy_format(opt[key])
        self.send_msg.msg = f"🆔 : {opt['peer_id']} \n " \
                       f"🎚 Частота вывода цитат: {opt['count_period']}\n"\
                       f"💕💯 полигамные браки: {opt['poligam_marry']}\n"\
                       f"📜 Вывод шаблонов(цитаты): {opt['quotes']}\n"\
                       f"📑 Вывод шаблонов(слова): {opt['words']}\n"\
    
    async def marry_toggle(self):
        self.send_msg.msg = await PeerRepository(self.peer).toggle_marry()

    async def toggle_word(self):
        self.send_msg.msg = await PeerRepository(self.peer).toggle_word()

    async def toggle_quote(self):
        self.send_msg.msg = await PeerRepository(self.peer).toggle_quote()
######################################################################################################


