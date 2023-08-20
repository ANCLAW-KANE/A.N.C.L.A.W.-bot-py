import re
import aiosqlite

from CONFIG import config_file_json, ADMIN_JSON_CONFIG
from online_tools import GetMembers
from tools import to_tuple, read_file_json, write_file_json, json_config, data_msg, DB_Manager

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
        self.EVIL_GODS = json_config().cfg_json()['EVIL_GODS']
        self.temp_array = []
        self.mem = None

    ######################################################################################################
    async def word(self):
        self.mem = (await GetMembers(self.peer))
        num = await DB_Manager('peers_words.db', f"SELECT * FROM '{str(self.peer)}' ", on_index=0).BD_COUNT()
        t_m = list(map(to_tuple, [self.word_sep_l[1].splitlines(), self.word_sep_l[2].splitlines()]))
        words = {
            ((3, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{int(max(num) + 1)}, "
                                 f"{t_m[0].lower()},"
                                 f" {t_m[1]})",
                                 "Создано",
                                 1, self.mem[0]),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})",
                                 "Удалено",
                                 1, self.mem[0]),
            ((1, 3), 'kill'): (f"DELETE FROM '{str(self.peer)}'",
                               "Данные уничтожены",
                               1, self.mem[2]),
            ((2, 4), 'update'): (f"UPDATE '{str(self.peer)}' SET"
                                 f" val = {t_m[0]} "
                                 f"where id = '{self.word_sep[3]}'",
                                 "Обновлено",
                                 1, self.mem[0])
        }
        if self.len_word_list in words:
            key = words.get(self.len_word_list)
            await DB_Manager(database='peers_words.db', query=key[0], peer=self.from_, m1=key[1]).exec(key[3])
        elif self.len_word_list == ((1, 3), 'list'):
            data_msg.msg = (await DB_Manager('peers_words.db',
                                             f"SELECT * FROM '{str(self.peer)}' ", sep='-').BD_LIST())

    ######################################################################################################
    async def role(self):
        self.mem = (await GetMembers(self.peer))
        num = await DB_Manager(database='peers_roles.db',
                               query=f"SELECT * FROM '{str(self.peer)}' ", on_index=0).BD_COUNT()
        t_m = list(map(to_tuple, [self.word_sep_l[1].splitlines(), self.word_sep_l[2].splitlines(),
                                  self.word_sep_l[3].splitlines(), self.word_sep_l[4].splitlines()]))
        roles = {
            ((5, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{(int(max(num) + 1))},"
                                 f"{t_m[0].lower()},"
                                 f"{t_m[1]},"
                                 f"{t_m[2]},"
                                 f"{t_m[3]})",
                                 "Создано", 1, self.mem[0]),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})",
                                 "Удалено", 1, self.mem[0]),
            ((1, 3), 'kill'): (f"DELETE FROM '{str(self.peer)}'",
                               "Данные уничтожены", 1, self.mem[2]),
            ((5, 3), 'update'): (f"UPDATE '{str(self.peer)}' SET "
                                 f"emoji_1 = {t_m[1]}, "
                                 f"txt = {t_m[2]}, "
                                 f"emoji_2 = {t_m[3]}"
                                 f" where command = {t_m[0].lower()}",
                                 "Обновлено", 1, self.mem[0]),
        }
        if self.len_word_list in roles:
            key = roles.get(self.len_word_list)
            await DB_Manager(database='peers_roles.db', query=key[0], peer=self.from_, m1=key[1]).exec(key[3])
        elif self.len_word_list == ((1, 3), 'list'):
            data_msg.msg = (await DB_Manager('peers_roles.db',
                                             f"SELECT * FROM '{str(self.peer)}'", sep='-').BD_LIST())

    ######################################################################################################
    async def quote(self):
        self.mem = (await GetMembers(self.peer))
        num = await DB_Manager('peers_quotes.db', f"SELECT * FROM '{str(self.peer)}' ", on_index=0).BD_COUNT()
        quotes = {
            ((2, 3), 'create'): (f"INSERT OR IGNORE INTO '{str(self.peer)}' VALUES("
                                 f"{int(max(num) + 1)},"
                                 f"{to_tuple(self.word_sep_l[1].splitlines()).lower()})",
                                 "Создано", 1, self.mem[0]),
            ((2, 3), 'delete'): (f"DELETE FROM '{str(self.peer)}' where id IN ("
                                 f"{to_tuple(self.word_sep_l[1].split(sep=' '))})",
                                 "Удалено", 1, self.mem[0]),
            ((1, 3), 'kill'): (f"DELETE FROM '{str(self.peer)}'",
                               "Данные уничтожены", 1, self.mem[2]),
            ((2, 4), 'update'): (f"UPDATE '{str(self.peer)}' SET "
                                 f"quote = {to_tuple(self.word_sep_l[1].splitlines())}"
                                 f" where id = {self.word_sep[3]}",
                                 "Обновлено", 1, self.mem[0]),
        }
        if self.len_word_list in quotes:
            key = quotes.get(self.len_word_list)
            await DB_Manager(database='peers_quotes.db', query=key[0], peer=self.from_, m1=key[1]).exec(key[3])
        elif self.len_word_list == ((1, 3), 'list'):
            data_msg.msg = (await DB_Manager('peers_quotes.db',
                                             f"SELECT * FROM '{str(self.peer)}'", '-').BD_LIST())

    ######################################################################################################
    async def node_list(self):
        data_msg.msg = f'|____ вк чат ____|____телеграм чат____||| Разрешения адресации\n' \
                       f'|=============|==================|||=========|==========\n'
        BD = await aiosqlite.connect('peers.db')
        edit = await BD.cursor()
        await edit.execute('SELECT * FROM nodes')
        for z in (await edit.fetchall()): self.temp_array.append(list(z))
        await BD.close()
        for o in range(len(self.temp_array)):
            for q in range(len(self.temp_array[o])):
                if self.temp_array[o][q] == 1: self.temp_array[o][q] = '✅'
                if self.temp_array[o][q] == 0: self.temp_array[o][q] = '⛔'
            data_msg.msg += f"| VK: {self.temp_array[o][0]} | TG: {self.temp_array[o][1]} ||| VK>TG: " \
                            f"{self.temp_array[o][2]}| TG>VK:{self.temp_array[o][3]}\n"

    #################################### менеджер соединений ###################################
    async def edit_node(self):
        if self.from_ in self.EVIL_GODS:
            nodes = {
                ((1, 5), 'create'): (f"INSERT OR IGNORE INTO nodes VALUES("
                                     f"{self.word_sep[3]}, "
                                     f"{self.word_sep[4]},"
                                     f"{1} , {1})",
                                     "Создано", 1),
                ((1, 4), 'delete'): (f"DELETE FROM nodes where peer_id = {self.word_sep[3]}",
                                     "Удалено", 1),
                ((1, 5), 'update'): (f"UPDATE nodes SET tg_id = {self.word_sep[4]} "
                                     f"where peer_id = {self.word_sep[3]}",
                                     "Обновлено", 1)
            }
            cls = DB_Manager(database='peers.db', query="", m1='Разрешено', m2='Запрещено', peer=self.peer, type_=int)
            nodes_perm = {
                ((1, 3), 'allow-vk'):
                    (await cls(query=f"SELECT * FROM nodes where peer_id = {self.peer}",
                               update=f"UPDATE nodes SET vk_tg_allow = ? where peer_id = ?",
                               on_index=2,
                               arg=self.peer)
                     ).key,
                ((1, 3), 'allow-tg'):
                    (await cls(query=f"SELECT * FROM nodes where peer_id = {self.peer}",
                               update=f"UPDATE nodes SET tg_vk_allow = ? where peer_id = ?",
                               on_index=3,
                               arg=self.peer)
                     ).key,
                ((1, 4), 'allow-vk'):
                    (await cls(query=f"SELECT * FROM nodes where peer_id = {self.word_sep[3]}",
                               update=f"UPDATE nodes SET vk_tg_allow = = ? where peer_id = ?",
                               on_index=2,
                               arg=self.word_sep[3])
                     ).key,
                ((1, 4), 'allow-tg'):
                    (await cls(query=f"SELECT * FROM nodes where peer_id = {self.word_sep[3]}",
                               update=f"UPDATE nodes SET tg_vk_allow = = ? where peer_id = ?",
                               on_index=3,
                               arg=self.word_sep[3])
                     ).key,
            }
            arg3 = re.findall("[0-9]{1,10}", self.word_sep[3])[0] if \
                re.findall("[0-9]{1,10}", self.word_sep[3]) else ''
            arg4 = re.findall("-[0-9]{9,13}", self.word_sep[4])[0] if \
                re.findall("-[0-9]{9,13}", self.word_sep[4]) else ''
            if self.word_sep[3] == arg3 and self.word_sep[4] == arg4 and self.len_word_list in nodes:
                key = nodes.get(self.len_word_list)
                await DB_Manager(database='peers.db', query=key[0], m1=key[1]).exec()
            elif self.len_word_list in nodes_perm:
                key = nodes_perm.get(self.len_word_list)
                if key is not None: await key()
            elif self.len_word_list == ((1, 3), 'list'):
                await self.node_list()

    ######################################################################################################
    async def count(self):
        if self.len_fact == 3:
            if self.word_sep[2] == re.search("100|[0-9]{1,2}", self.word_sep[2])[0]:
                await DB_Manager(database='peers.db',
                                 query=f"UPDATE peers SET "
                                       f"count_period = {int(self.word_sep[2])} "
                                       f"where peer_id ='{self.peer}'",
                                 m1=f"Значение установлено на {self.word_sep[2]}").exec()
            else:
                data_msg.msg = f"Значение должно быть 0-100 (%)"

    ######################################################################################################
    async def show_settings(self):
        BD = await aiosqlite.connect('peers.db')
        edit = await BD.cursor()
        if self.len_fact == 3 and self.word_sep[2] == re.findall("[0-9]{1,10}", self.word_sep[2])[0]:
            await edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.word_sep[2]}")
        else:
            await edit.execute(f"SELECT * FROM peers WHERE peer_id = {self.peer}")
        opt = list(await edit.fetchone())
        await BD.close()
        for o in range(len(opt)):
            if opt[o] == '1' or opt[o] == 1: opt[o] = '✅'
            if opt[o] == '0' or opt[o] == 0: opt[o] = '⛔'
        data_msg.msg = f"🆔 : {opt[0]} \n " \
                       f"☢ ️Ультимативный режим(на админки не действует): {opt[1]}\n" \
                       f"🎚 Частота вывода цитат: {opt[2]}\n" \
                       f"☢️ Ультимативный режим(ролевой): {opt[3]}\n" \
                       f"🍆 Режим рандомного изнасилования: {opt[4]}\n" \
                       f"📡 R.E.D.-модуль: {opt[5]}\n" \
                       f"💕💯 полигамные браки: {opt[6]}\n"

    #################################### переключатель для resend ###################################
    async def global_resend_toggle(self):
        cls = DB_Manager(database='peers.db', query="", m1='Разрешено', m2='Запрещено', peer=self.peer,
                         update=f"UPDATE peers SET resend = ? where peer_id = ?", on_index=5, type_=int)
        if self.len_fact == 3:
            if re.findall("[0-9]{1,10}", self.word_sep[2])[0]:
                await (await cls(query=f"SELECT * FROM peers  where peer_id = {self.word_sep[2]}",
                                 arg=self.word_sep[2])).key()
        elif self.len_fact == 2:
            await (await cls(query=f"SELECT * FROM peers where peer_id = {self.peer}", arg=self.peer)).key()

    #################################### переключатель для браков ###################################
    async def marry_toggle(self):
        if self.len_fact == 2:
            await DB_Manager(database='peers.db', query=f"SELECT * FROM peers where peer_id = {self.peer}",
                             m1='Разрешено', m2='Запрещено', peer=self.peer,
                             update=f"UPDATE peers SET poligam_marry = ? where peer_id = ?", on_index=6, type_=int,
                             arg=self.peer).key()


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
        self.data = read_file_json(config_file_json)
        self.string = ''

    ######################################################################################################
    async def edit(self):
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
                data_msg.msg = f"Запрос :\n {self.arg[2]} = {type_} {self.arg_array} \n выполнен успешно."
            else:
                data_msg.msg = f"Данные не корректны."
        else:
            data_msg.msg = f"Ты не администратор."

    ######################################################################################################
    async def show(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            for e in self.data: self.string += f"{e} : {self.data.get(e)}\n"
            data_msg.msg = self.string

    ######################################################################################################
    async def info_param(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            BD = await aiosqlite.connect('peers.db')
            edit = await BD.cursor()
            await edit.execute(f"SELECT * FROM params_info")
            for e in (await edit.fetchall()): self.string += f"{e[0]} - {e[1]}\n"
            await BD.close()
            data_msg.msg = self.string

    ######################################################################################################
    async def add_info(self):
        if self.from_ in ADMIN_JSON_CONFIG:
            edits = {
                (5, 'create'): (f"INSERT OR IGNORE INTO params_info VALUES('"
                                f"{self.arg[3]}',"
                                f" '{self.arg[4]}')",
                                "Описание параметра создано"),
                (5, 'update'): (f"UPDATE params_info SET info = '{self.arg[4]}' "
                                f"WHERE param = '{self.arg[3]}'",
                                "Описание параметра обновлено"),
                (4, 'delete'): (f"DELETE FROM params_info where param = '{self.arg[3]}'",
                                "Описание параметра удалено")
            }
            if self.len_arg in edits:
                edit = edits.get(self.len_arg)
                DB_Manager(database='peers.db', query=edit[0], m1=edit[1])
######################################################################################################################
