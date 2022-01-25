import sqlite3, re

from tools import BD_COUNT, to_tuple, get_BD_list, read_file_json, write_file_json, json_gen
from online_tools import send_to_specific_peer,Invertor,GetMembers
from CONFIG import config_file_json, ADMIN_JSON_CONFIG

types = {
    'int': int,
    'string': str,
    'bool': bool,
    'arr-int': lambda a: [int(a)]
}
######################################################################################################
class manager(object):
    def __init__(self, word_sep_l, word_sep, from_, peer):
        self.peer = peer
        self.from_ = from_
        self.word_sep_l = word_sep_l  # число строк
        self.word_sep = word_sep  # число слов в 1 строке
        self.fact = filter(lambda a: a != '', self.word_sep)  # фактическая длинна слов в 1 строке
        self.fact_l = filter(lambda a: a != '', self.word_sep_l)  # фактическая длинна строк в общем
        self.len_fact = len(list(self.fact))
        self.len_fact_l = len(list(self.fact_l))
        self.len_word_list = ((self.len_fact_l, self.len_fact), word_sep[2])  # фактическая длинна fact + fact_l
        self.EVIL_GODS = json_gen().return_config_file_json()['EVIL_GODS']
        self.temp_array = []
        self.mem = GetMembers(self.peer)

    ######################################################################################################
    def word(self):
        BDWORDS = sqlite3.connect('peers_words.db')
        edit_word = BDWORDS.cursor()
        edit_word.execute(f"SELECT * FROM '{str(self.peer)}' ")
        num = BD_COUNT(edit_word, 0)
        t_m = list(map(to_tuple,[self.word_sep_l[1].splitlines(),self.word_sep_l[2].splitlines()]))
        words = {
            ((3, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{int(max(num) + 1)}, {t_m[0].lower()}, {t_m[1]})", "Создано",1,self.mem[0]),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})", "Удалено",1,self.mem[0]),
            ((1, 3), 'kill'): (f"DELETE FROM '{str(self.peer)}'", "Данные уничтожены", 1,self.mem[2]),
            ((2, 4), 'update'): (f"UPDATE '{str(self.peer)}' SET val = "
                                 f"{t_m[0]} where id = '{self.word_sep[3]}'", "Обновлено",1,self.mem[0]),
            ((1, 3), 'list'): ('', get_BD_list(edit_word, f"SELECT * FROM '{str(self.peer)}'", '-'),0,self.mem[0])
        }
        if self.len_word_list in words:
            key = words.get(self.len_word_list)
            edit_word.execute(key[0])
            if BDWORDS.total_changes >= key[2] :
                if self.from_ in key[3]:
                    BDWORDS.commit()
                    send_to_specific_peer(key[1], self.peer)
                else: send_to_specific_peer("Нет прав", self.peer)
            else:send_to_specific_peer("Не выполнено, проверьте аргументы. (Или данная запись уже есть)", self.peer)
        BDWORDS.close()

    ######################################################################################################
    def role(self):
        BDROLES = sqlite3.connect('peers_roles.db')
        edit_roles = BDROLES.cursor()
        edit_roles.execute(f"SELECT * FROM '{str(self.peer)}' ")
        num = BD_COUNT(edit_roles, 0)
        t_m = list(map(to_tuple,[self.word_sep_l[1].splitlines(),self.word_sep_l[2].splitlines(),
                            self.word_sep_l[3].splitlines(),self.word_sep_l[4].splitlines()]))
        roles = {
            ((5, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                    f"{(int(max(num) + 1))},{t_m[0].lower()},{t_m[1]},{t_m[2]},{t_m[3]})", "Создано",1,self.mem[0]),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})", "Удалено",1,self.mem[0]),
            ((1, 3), 'kill'): (f"DELETE FROM '{str(self.peer)}'", "Данные уничтожены", 1,self.mem[2]),
            ((5, 3), 'update'): (f"UPDATE '{str(self.peer)}' SET emoji_1 = {t_m[1]}, txt = {t_m[2]}, emoji_2 = {t_m[3]}"
                                 f" where command = {t_m[0].lower()}", "Обновлено",1,self.mem[0]),
            ((1, 3), 'list'): ('', get_BD_list(edit_roles, f"SELECT * FROM '{str(self.peer)}'", '-'),0,self.mem[0])
        }
        if self.len_word_list in roles:
            key = roles.get(self.len_word_list)
            edit_roles.execute(key[0])
            if BDROLES.total_changes >= key[2] :
                if self.from_ in key[3]:
                    BDROLES.commit()
                    send_to_specific_peer(key[1], self.peer)
                else: send_to_specific_peer("Нет прав", self.peer)
            else:send_to_specific_peer("Не выполнено, проверьте аргументы. (Или данная запись уже есть)", self.peer)
        BDROLES.close()

    ######################################################################################################
    def quote(self):
        BDQUOTES = sqlite3.connect('peers_quotes.db')
        edit_quotes = BDQUOTES.cursor()
        edit_quotes.execute(f"SELECT * FROM '{str(self.peer)}' ")
        num = BD_COUNT(edit_quotes, 0)
        quotes = {
            ((2, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{int(max(num) + 1)},{to_tuple(self.word_sep_l[1].splitlines()).lower()})",
                                 "Создано",1,self.mem[0]),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})", "Удалено",1,self.mem[0]),
            ((1, 3), 'kill'): (f"DELETE FROM '{str(self.peer)}'", "Данные уничтожены", 1,self.mem[2]),
            ((2, 4), 'update'): (f"UPDATE '{str(self.peer)}' SET quote = "
                                 f"{to_tuple(self.word_sep_l[1].splitlines())} where id = {self.word_sep[3]}",
                                 "Обновлено",1,self.mem[0]),
            ((1, 3), 'list'): ('', get_BD_list(edit_quotes, f"SELECT * FROM '{str(self.peer)}'", '-'),0,self.mem[0])
        }
        if self.len_word_list in quotes:
            key = quotes.get(self.len_word_list)
            edit_quotes.execute(key[0])
            if BDQUOTES.total_changes >= key[2] :
                if self.from_ in key[3]:
                    BDQUOTES.commit()
                    send_to_specific_peer(key[1], self.peer)
                else: send_to_specific_peer("Нет прав", self.peer)
            else: send_to_specific_peer("Не выполнено, проверьте аргументы. (Или данная запись уже есть)", self.peer)
        BDQUOTES.close()

    ######################################################################################################
    def node_list(self):
        m = f'|____ вк чат ____|____телеграм чат____||| Разрешения адресации\n' \
            f'|=============|==================|||=========|==========\n'
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute('SELECT * FROM nodes')
        for z in edit.fetchall():
            self.temp_array.append(list(z))
        for o in range(len(self.temp_array)):
            for q in range(len(self.temp_array[o])):
                if self.temp_array[o][q] == 1: self.temp_array[o][q] = '✅'
                if self.temp_array[o][q] == 0: self.temp_array[o][q] = '⛔'
            m += f"| VK: {self.temp_array[o][0]} | TG: {self.temp_array[o][1]} ||| VK>TG: " \
                      f"{self.temp_array[o][2]}| TG>VK:{self.temp_array[o][3]}\n"
        BD.close()
        return m

    #################################### менеджер соединений ###################################
    def edit_node(self):
        if self.from_ in self.EVIL_GODS:
            BD = sqlite3.connect('peers.db')
            edit = BD.cursor()
            nodes = {
                ((1, 5), 'create'): (f"INSERT OR IGNORE INTO nodes "
                                     f"VALUES({self.word_sep[3]}, {self.word_sep[4]},{1} , {1})", "Создано",1),
                ((1, 4), 'delete'): (f"DELETE FROM nodes where peer_id = {self.word_sep[3]}", "Удалено",1),
                ((1, 5), 'update'): (f"UPDATE nodes SET tg_id = {self.word_sep[4]} "
                                     f"where peer_id = {self.word_sep[3]}", "Обновлено",1),
                ((1, 3), 'list'): ('', self.node_list(),0),
                }
            p = ['Разрешено','Запрещено', self.peer,"SELECT * FROM nodes where peer_id =",
                 "UPDATE nodes SET"," = ? where peer_id = ?"]
            nodes_perm = {
                ((1, 3), 'allow-vk'):
                    Invertor(f"{p[3]} {p[2]}",p[0],p[1], p[2], f"{p[4]} vk_tg_allow {p[5]}", 2,int,p[2]).key,
                ((1, 3), 'allow-tg'):
                    Invertor(f"{p[3]} {p[2]}", p[0],p[1],p[2],f"{p[4]} tg_vk_allow {p[5]}", 3, int, p[2]).key,
                ((1, 4), 'allow-vk'):
                    Invertor( f"{p[3]} {self.word_sep[3]}", p[0],p[1],p[2],f"{p[4]} vk_tg_allow = {p[5]}",2, int, self.word_sep[3]).key,
                ((1, 4), 'allow-tg'):
                    Invertor( f"{p[3]} {self.word_sep[3]}",p[0],p[1],p[2],f"{p[4]} tg_vk_allow = {p[5]}", 3, int, self.word_sep[3]).key,
            }
            arg3 = re.findall("[0-9]{1,10}", self.word_sep[3])[0] if re.findall("[0-9]{1,10}", self.word_sep[3]) else ''
            arg4 = re.findall("-[0-9]{9,13}", self.word_sep[4])[0] if re.findall("-[0-9]{9,13}", self.word_sep[4]) else ''
            if self.word_sep[3] == arg3 and self.word_sep[4] == arg4 and self.len_word_list in nodes:
                key = nodes.get(self.len_word_list)
                edit.execute(key[0])
                if BD.total_changes >= key[2]:
                    BD.commit()
                    send_to_specific_peer(key[1], self.peer)
                else: send_to_specific_peer("Не выполнено, проверьте аргументы.", self.peer)
            elif self.len_word_list in nodes_perm:
                key = nodes_perm.get(self.len_word_list)
                if key is not None: key()
            BD.close()

    ######################################################################################################
    def count(self):
        if self.len_fact == 3 :
            if self.word_sep[2] == re.search("100|[0-9]{1,2}", self.word_sep[2])[0]:
                BD = sqlite3.connect('peers.db')
                edit = BD.cursor()
                edit.execute(f"UPDATE peers SET count_period = {int(self.word_sep[2])} where peer_id ='{self.peer}'")
                BD.commit()
                send_to_specific_peer(f"Значение установлено на {self.word_sep[2]}", self.peer)
                BD.close()
            else: send_to_specific_peer(f"Значение должно быть 0-100 (%)", self.peer)

    ######################################################################################################
    def show_settings(self):
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        if self.len_fact == 3 and self.word_sep[2] == re.findall("[0-9]{1,10}", self.word_sep[2])[0]:
            edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.word_sep[2]}")
        else: edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.peer}")
        opt = list(edit.fetchone())
        BD.close()
        for o in range(len(opt)):
            if opt[o] == '1': opt[o] = '✅'
            if opt[o] == '0': opt[o] = '⛔'
            if opt[o] == 1 : opt[o] = '✅'
            if opt[o] == 0 : opt[o] = '⛔'
        send_to_specific_peer(f"🆔 : {opt[0]} \n "
                              f"☢ ️Ультимативный режим(на админки не действует): {opt[1]}\n"
                              f"🎚 Частота вывода цитат: {opt[2]}\n"
                              f"☢️ Ультимативный режим(ролевой): {opt[3]}\n"
                              f"🍆 Режим рандомного изнасилования: {opt[4]}\n"
                              f"📡 R.E.D.-модуль: {opt[5]}\n"
                              f"💕💯 полигамные браки: {opt[6]}\n"
                              , self.peer)


    #################################### переключатель для resend ###################################
    def global_resend_toggle(self):
        p = ['Разрешено','Запрещено',self.peer]
        if self.len_fact == 3 :
            if re.findall("[0-9]{1,10}", self.word_sep[2])[0]:
                Invertor(f"SELECT * FROM peers  where peer_id = {self.word_sep[2]}", p[0],p[1],p[2],
                         f"UPDATE peers SET resend = ? where peer_id = ?", 5, int, self.word_sep[2]).key()
        elif self.len_fact == 2 :
            Invertor( f"SELECT * FROM peers where peer_id = {self.peer}", p[0],p[1],p[2],
                      f"UPDATE peers SET resend = ? where peer_id = ?", 5, int, p[2]).key()

    #################################### переключатель для браков ###################################
    def marry_toggle(self):
        p = ['Разрешено', 'Запрещено', self.peer]
        if self.len_fact == 2:
            Invertor(f"SELECT * FROM peers where peer_id = {self.peer}", p[0], p[1], p[2],
                     f"UPDATE peers SET poligam_marry = ? where peer_id = ?", 6, int, p[2]).key()


######################################################################################################
class base_config(object):
    def __init__(self, arg, from_, peer):
        self.arg = arg
        self.fact_arg = filter(lambda a: a != '', self.arg)  # фактическая длина arg
        self.len_arg = (len(list(self.fact_arg)), self.arg[2])  # длина списка len_arg + знчение 2 аргумента
        self.arg_array = str(self.arg[4]).split(sep=' ')  # деление поледнего аргумента на подаргументы
        self.from_ = from_
        self.peer = peer
        self.len_arg_array = len(self.arg_array)  # длинна arg_array
        self.BD = sqlite3.connect('peers.db')
        self.data = read_file_json(config_file_json)
        self.string = ''

    ######################################################################################################
    def edit(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            arg4_elements = []
            data_keys = self.data.keys()
            type_ = types.get(self.arg[3])
            if self.arg_array is not '' and self.arg[2] in data_keys and self.arg[3] in types:
                if self.len_arg_array != 0 and self.len_arg_array > 1:
                    for arg4_element in self.arg_array:
                        arg4_elements.append(type_(arg4_element))
                    self.data[self.arg[2]] = arg4_elements
                else:
                    self.data[self.arg[2]] = type_(self.arg_array[0])
                write_file_json(config_file_json, self.data)
                m = f"Запрос :\n {self.arg[2]} = {type_} {self.arg_array} \n выполнен успешно."
            else: m =  f"Данные не корректны."
        else: m =  f"Ты не администратор."
        send_to_specific_peer(m,self.peer)

    ######################################################################################################
    def show(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            for e in self.data:
                self.string += f"{e} : {self.data.get(e)}\n"
            send_to_specific_peer(self.string, self.peer)

    ######################################################################################################
    def info_param(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            edit = self.BD.cursor()
            edit.execute(f"SELECT * FROM params_info")
            for e in edit.fetchall():
                self.string += f"{e[0]} - {e[1]}\n"
            send_to_specific_peer(self.string, self.peer)
            self.BD.close()

    ######################################################################################################
    def add_info(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            edit = self.BD.cursor()
            edits = {
                (5, 'create'): (f"INSERT OR IGNORE INTO params_info VALUES('{self.arg[3]}',"
                                f" '{self.arg[4]}')", "Описание параметра создано"),
                (5, 'update'): (f"UPDATE params_info SET info = '{self.arg[4]}' "
                                f"WHERE param = '{self.arg[3]}'", "Описание параметра обновлено"),
                (4, 'delete'): (f"DELETE FROM params_info where param = '{self.arg[3]}'", "Описание параметра удалено")
            }
            if self.len_arg in edits:
                edit.execute(edits.get(self.len_arg)[0])
                self.BD.commit()
                send_to_specific_peer(edits.get(self.len_arg)[1], self.peer)
######################################################################################################################