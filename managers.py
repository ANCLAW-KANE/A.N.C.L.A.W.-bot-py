import sqlite3, re

from tools import BD_COUNT, to_tuple, get_BD_list, read_file_json, write_file_json, json_gen
from online_tools import send_to_specific_peer,Invertor
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
        self.m = f'| ____ вк чат ____ | ____телеграм чат____ ||| Разрешения адресации\n'\
                 f'| ============= |================== ||| =========|==========\n'

    ######################################################################################################
    def word(self):
        BDWORDS = sqlite3.connect('peers_words.db')
        edit_word = BDWORDS.cursor()
        edit_word.execute(f"SELECT * FROM '{str(self.peer)}' ")
        num = BD_COUNT(edit_word, 0)
        words = {
            ((3, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{int(max(num) + 1)},"
                                 f"{to_tuple(self.word_sep_l[1].splitlines()).lower()},"
                                 f"{to_tuple(self.word_sep_l[2].splitlines())})", "Создано"),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})", "Удалено"),
            ((2, 4), 'update'): (f"UPDATE '{str(self.peer)}' SET val = "
                                 f"{to_tuple(self.word_sep_l[1].splitlines())} where id = "
                                 f"'{self.word_sep[3]}'", "Обновлено"),
            ((1, 3), 'list'): ('', get_BD_list(edit_word, f"SELECT * FROM '{str(self.peer)}'", '-'))
        }
        if self.len_word_list in words:
            key = words.get(self.len_word_list)
            edit_word.execute(key[0])
            BDWORDS.commit()
            send_to_specific_peer(key[1], self.peer)
        BDWORDS.close()

    ######################################################################################################
    def role(self):
        BDROLES = sqlite3.connect('peers_roles.db')
        edit_roles = BDROLES.cursor()
        edit_roles.execute(f"SELECT * FROM '{str(self.peer)}' ")
        num = BD_COUNT(edit_roles, 0)
        roles = {
            ((5, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{(int(max(num) + 1))},{to_tuple(self.word_sep_l[1].splitlines()).lower()},"
                                 f"{to_tuple(self.word_sep_l[2].splitlines())},{to_tuple(self.word_sep_l[3].splitlines())},"
                                 f"{to_tuple(self.word_sep_l[4].splitlines())})", "Создано"),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})", "Удалено"),
            ((5, 3), 'update'): (f"UPDATE '{str(self.peer)}' SET emoji_1 = "
                                 f"{to_tuple(self.word_sep_l[2].splitlines())}, txt = "
                                 f"{to_tuple(self.word_sep_l[3].splitlines())}, emoji_2 = "
                                 f"{to_tuple(self.word_sep_l[4].splitlines())} "
                                 f"where command = {to_tuple(self.word_sep_l[1].splitlines()).lower()}", "Обновлено"),
            ((1, 3), 'list'): ('', get_BD_list(edit_roles, f"SELECT * FROM '{str(self.peer)}'", '-'))
        }
        if self.len_word_list in roles:
            key = roles.get(self.len_word_list)
            edit_roles.execute(key[0])
            BDROLES.commit()
            send_to_specific_peer(key[1], self.peer)
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
                                 "Создано"),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})", "Удалено"),
            ((2, 4), 'update'): (f"UPDATE '{str(self.peer)}' SET quote = "
                                 f"{to_tuple(self.word_sep_l[1].splitlines())} where id = {self.word_sep[3]}",
                                 "Обновлено"),
            ((1, 3), 'list'): ('', get_BD_list(edit_quotes, f"SELECT * FROM '{str(self.peer)}'", '-'))

        }
        if self.len_word_list in quotes:
            key = quotes.get(self.len_word_list)
            edit_quotes.execute(key[0])
            BDQUOTES.commit()
            send_to_specific_peer(key[1], self.peer)
        BDQUOTES.close()

    ######################################################################################################
    def node_list(self):
        list_words = []
        BD = sqlite3.connect('peers.db')
        edit = BD.cursor()
        edit.execute('SELECT * FROM nodes')
        for z in edit.fetchall():
            list_words.append(list(z))
        for o in range(len(list_words)):
            for q in range(len(list_words[o])):
                if list_words[o][q] == 1: list_words[o][q] = '✅'
                if list_words[o][q] == 0: list_words[o][q] = '⛔'
            self.m += f"| VK: {list_words[o][0]} | TG: {list_words[o][1]} ||| VK>TG: " \
                      f"{list_words[o][2]}| TG>VK:{list_words[o][3]}\n"
        return self.m

    def edit_node(self):
        if self.from_ in self.EVIL_GODS:
            BD = sqlite3.connect('peers.db')
            edit = BD.cursor()
            nodes = {
                ((1, 5), 'create'): (f"INSERT OR IGNORE INTO nodes "
                                     f"VALUES({self.word_sep[3]}, {self.word_sep[4]},{1} , {1})", "Создано"),
                ((1, 4), 'delete'): (f"DELETE FROM nodes where peer_id = {self.word_sep[3]}", "Удалено"),
                ((1, 5), 'update'): (f"UPDATE nodes SET tg_id = {self.word_sep[4]} "
                                     f"where peer_id = {self.word_sep[3]}", "Обновлено"),
                ((1, 3), 'list'): ('', self.node_list()),
                }
            nodes_perm = {
                ((1, 3), 'allow-vk'):
                    Invertor(self.from_,self.EVIL_GODS,f"SELECT * FROM nodes where peer_id = {self.peer}",'Разрешено',
                    'Запрещено',self.peer,f"UPDATE nodes SET vk_tg_allow = ? where peer_id = ?",2,int,self.peer).key,
                ((1, 3), 'allow-tg'):
                    Invertor(self.from_, self.EVIL_GODS, f"SELECT * FROM nodes where peer_id = {self.peer}", 'Разрешено',
                    'Запрещено', self.peer,f"UPDATE nodes SET tg_vk_allow = ? where peer_id = ?", 3, int, self.peer).key,
                ((1, 4), 'allow-vk'):
                    Invertor(self.from_, self.EVIL_GODS, f"SELECT * FROM nodes where peer_id = {self.word_sep[3]}", 'Разрешено',
                    'Запрещено', self.peer, f"UPDATE nodes SET vk_tg_allow = ? where peer_id = ?", 2, int, self.word_sep[3]).key,
                ((1, 4), 'allow-tg'):
                    Invertor(self.from_, self.EVIL_GODS, f"SELECT * FROM nodes  where peer_id = {self.word_sep[3]}", 'Разрешено',
                    'Запрещено', self.peer, f"UPDATE nodes SET tg_vk_allow = ? where peer_id = ?", 3, int, self.word_sep[3]).key,
            }
            arg3 = re.findall("[0-9]{1,10}", self.word_sep[3])[0] if re.findall("[0-9]{1,10}", self.word_sep[3]) else ''
            arg4 = re.findall("-[0-9]{9,13}", self.word_sep[4])[0] if re.findall("-[0-9]{9,13}", self.word_sep[4]) else ''
            if self.word_sep[3] == arg3 and self.word_sep[4] == arg4 and self.len_word_list in nodes:
                key = nodes.get(self.len_word_list)
                edit.execute(key[0])
                BD.commit()
                send_to_specific_peer(key[1], self.peer)
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
        edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.peer}")
        opt = list(edit.fetchone())
        for o in range(len(opt)):
            if opt[o] == '1' : opt[o] = '✅'
            if opt[o] == '0' or 0 : opt[o] = '⛔'
        send_to_specific_peer(f"🆔 : {opt[0]} \n "
                              f"☢ ️Ультимативный режим(на админки не действует): {opt[1]}\n"
                              f"🎚 Частота вывода цитат: {opt[2]}\n"
                              f"☢️ Ультимативный режим: {opt[3]}\n"
                              f"🍆 Режим рандомного изнасилования: {opt[4]}\n"
                              f"📡 R.E.D.-модуль: {opt[5]}\n"
                              , self.peer)
        BD.close()


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
                send_to_specific_peer(f"Запрос :\n {self.arg[2]} = {type_} {self.arg_array} \n выполнен успешно.",
                                      self.peer)
            else:
                send_to_specific_peer(f"Данные не корректны.", self.peer)
        else:
            send_to_specific_peer(f"Ты не администратор.", self.peer)

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