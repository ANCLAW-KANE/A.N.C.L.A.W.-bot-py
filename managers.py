import sqlite3

from tools import BD_COUNT,to_tuple,get_BD_list,read_file_json,write_file_json
from online_tools import send_to_specific_peer
from CONFIG import config_file_json,ADMIN_JSON_CONFIG

types = {
    'int': int,
    'string': str,
    'bool': bool,
}

class manager(object):
    def __init__(self,word_sep_l,word_sep,peer):
        try:
            self.peer = peer
            self.word_sep_l = word_sep_l #число строк
            self.word_sep = word_sep #число слов в 1 строке
            self.fact = filter(lambda a: a != '',self.word_sep) # фактическая длинна слов в 1 строке
            self.fact_l = filter(lambda a: a != '', self.word_sep_l) # фактическая длинна строк в общем
            self.len_word_list = ((len(list(self.fact_l)), len(list(self.fact))), word_sep[2]) # фактическая длинна fact + fact_l
        except:
            self.peer = peer
            self.word_sep_l = word_sep_l
            self.word_sep = word_sep
            self.len_word_list = None

    def word(self):
        BDWORDS = sqlite3.connect('peers_words.db')
        edit_word = BDWORDS.cursor()
        edit_word.execute(f"SELECT * FROM '{str(self.peer)}' ")
        num = BD_COUNT(edit_word,0)
        words= {
            ((3, 3), 'create'):(f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                              f"{int(max(num)+1)},"
                              f"{to_tuple(self.word_sep_l[1].splitlines()).lower()},"
                              f"{to_tuple(self.word_sep_l[2].splitlines())})","Создано"),

            ((2, 3), 'delete'):(f"DELETE FROM '{str(self.peer)}' where id IN ("
                             f"{to_tuple(self.word_sep_l[1].split(sep=' '))})","Удалено"),

            ((2, 4), 'update'):(f"UPDATE '{str(self.peer)}' SET val = "
                                f"{to_tuple(self.word_sep_l[1].splitlines())} where id = "
                                f"'{self.word_sep[3]}'","Обновлено"),
            ((1, 3), 'list'):('',get_BD_list(edit_word, f"SELECT * FROM '{str(self.peer)}'"))
        }
        if self.len_word_list in words:
            key = words.get(self.len_word_list)
            edit_word.execute(key[0])
            BDWORDS.commit()
            send_to_specific_peer(key[1],self.peer)
        BDWORDS.close()

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
            ((1, 3), 'list'): ('', get_BD_list(edit_roles, f"SELECT * FROM '{str(self.peer)}'"))
        }
        print(self.len_word_list)
        if self.len_word_list in roles:
            key = roles.get(self.len_word_list)
            edit_roles.execute(key[0])
            BDROLES.commit()
            send_to_specific_peer(key[1],self.peer)
        BDROLES.close()

    def quote(self):
        BDQUOTES = sqlite3.connect('peers_quotes.db')
        edit_quotes = BDQUOTES.cursor()
        edit_quotes.execute(f"SELECT * FROM '{str(self.peer)}' ")
        num = BD_COUNT(edit_quotes, 0)
        quotes = {
            ((2, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{int(max(num) + 1)},{to_tuple(self.word_sep_l[1].splitlines()).lower()})", "Создано"),

            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})", "Удалено"),

            ((2, 4), 'update'): (f"UPDATE '{str(self.peer)}' SET quote = "
                                 f"{to_tuple(self.word_sep_l[1].splitlines())} where id = {self.word_sep[3]}","Обновлено"),
            ((1, 3), 'list'): ('', get_BD_list(edit_quotes, f"SELECT * FROM '{str(self.peer)}'"))

        }
        if self.len_word_list in quotes:
            key = quotes.get(self.len_word_list)
            edit_quotes.execute(key[0])
            BDQUOTES.commit()
            send_to_specific_peer(key[1],self.peer)
        BDQUOTES.close()

class base_config(object):
    def __init__(self,arg,from_,peer):
        self.arg = arg
        self.fact_arg = filter(lambda a: a != '',self.arg)
        self.len_arg = (len(list(self.fact_arg)),self.arg[2])
        self.arg_array = str(self.arg[4]).split(sep=' ')
        self.from_ = from_
        self.peer = peer
        self.len_arg_array = len(self.arg_array)
        self.BD = sqlite3.connect('peers.db')
        self.data = read_file_json(config_file_json)

    def edit(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            arg4_elements = []
            data_keys = self.data.keys()
            type_ = types.get(self.arg[3])
            if self.arg_array is not '' and self.arg[2] in data_keys and self.arg[3] in types:
                if  self.len_arg_array != 0 and self.len_arg_array > 1:
                    for arg4_element in self.arg_array:
                        arg4_elements.append(type_(arg4_element))
                    self.data[self.arg[2]] = arg4_elements
                else:
                    self.data[self.arg[2]] = type_(self.arg_array[0])
                write_file_json(config_file_json,self.data)
                send_to_specific_peer(f"Запрос :\n {self.arg[2] } = { type_(self.arg_array[0])} \n выполнен успешно.",self.peer)
            else:
                send_to_specific_peer(f"Данные не корректны.", self.peer)
        else:
            send_to_specific_peer(f"Ты не администратор.", self.peer)

    def show(self):
        s=''
        for e in self.data:
            s+=f"{e} : {self.data.get(e)}\n"
        send_to_specific_peer(s,self.peer)
    def info_param(self):
        edit = self.BD.cursor()
        s = ''
        edit.execute(f"SELECT * FROM params_info")
        for e in edit.fetchall():
            s+=f"{e[0]} - {e[1]}\n"
        send_to_specific_peer(s,self.peer)
        self.BD.close()
    def add_info(self):
        edit = self.BD.cursor()
        edits = {
            (5,'create'):(f"INSERT OR IGNORE INTO params_info VALUES('{self.arg[3]}',"
                          f" '{self.arg[4]}')","Описание параметра создано"),
            (5,'update'):(f"UPDATE params_info SET info = '{self.arg[4]}' "
                          f"WHERE param = '{self.arg[3]}'","Описание параметра обновлено")
        }
        if self.len_arg in edits:
            edit.execute(edits.get(self.len_arg)[0])
            self.BD.commit()
            send_to_specific_peer(edits.get(self.len_arg)[1],self.peer)











