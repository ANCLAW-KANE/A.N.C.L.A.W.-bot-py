import json, random, string, logging, sys, psutil, os, aiosqlite, pickledb
from dataclasses import dataclass
from subprocess import check_output
from PIL import Image
from CONFIG import config_file_json
from enums import States_cook


################################ TOOLS ##############################################
def to_tuple(obj):  # li
    return str(list(obj)).replace('[', '').replace(']', '')


def to_list(obj):
    return list(str(list(obj)).replace('[', '').replace(']', '').split(','))


############################################################################
def write_file(name, getfile):
    with open(name, 'bw') as f: f.write(getfile)


############################################################################
def read_file_json(name):
    try:
        with open(name, "r") as f:  data = json.load(f)
        return data
    except:
        print("Файл отсутствует или поврежден")


############################################################################
def write_file_json(name, data):
    with open(name, "w") as f:  json.dump(data, f)


############################################################################
def reverse_dict(get_dict):
    reverse = []
    for key in get_dict.keys(): reverse.append((get_dict[key], key))
    return dict(reverse)


############################################################################
def join_dict_keys(arg):
    args = []
    for a in arg: args += list(a.keys())
    return args


############################################################################
def join_dict(arg):
    args = []
    for a in arg: args += list(a.items())
    return dict(args)


def dict_to_str(d: dict, sep: str):
    return ''.join('{}{}{}'.format(key, sep, val) for key, val in d.items())


############################################################################
def gen_r_s(l):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(l))
    print("Random string of length ", l, " is: ", rand_string)


############################################################################
class DB_Manager(object):

    def __init__(self, database, query, sep=None, on_index=None, type_=None,
                 peer=None, m1=None, m2=None, update=None, arg=None):
        self.database = database
        self.connect = None
        self.cursor = None
        self.query = query
        self.sep = sep
        self.on_index = on_index
        self.type_ = type_
        self.peer = peer
        self.m1 = m1
        self.m2 = m2
        self.update = update
        self.arg = arg

    async def __call__(self, database=None, query=None, sep=None, on_index=None, type_=None,
                       peer=None, m1=None, m2=None, update=None, arg=None):
        new = self.__new__(self.__class__)
        new.database = self.database if database is None else database
        new.query = self.query if query is None else query
        new.sep = self.sep if sep is None else sep
        new.on_index = self.on_index if on_index is None else on_index
        new.type_ = self.type_ if type_ is None else type_
        new.peer = self.peer if peer is None else peer
        new.m1 = self.m1 if m1 is None else m1
        new.m2 = self.m2 if m2 is None else m2
        new.update = self.update if update is None else update
        new.arg = self.arg if arg is None else arg
        print(new, new.__dict__)
        return new

    async def __connect__(self):
        self.connect = await aiosqlite.connect(self.database)
        self.cursor = await self.connect.cursor()

    async def key(self):  # для переключения 0 1 значений в БД
        await self.__connect__()
        str_E_G = list(await (await self.cursor.execute(self.query)).fetchone())
        data_msg.msg = "ERROR"
        if str_E_G[self.on_index] == self.type_('0'):
            str_E_G = self.type_('1')
            data_msg.msg = self.m1
        elif str_E_G[self.on_index] == self.type_('1'):
            str_E_G = self.type_('0')
            data_msg.msg = self.m2
        await self.cursor.execute(self.update, (self.type_(str_E_G), self.arg))
        await self.connect.commit()
        await self.connect.close()

    async def exec(self, access=None, changes=1):
        await self.__connect__()
        await self.cursor.execute(self.query)
        if self.connect.total_changes >= changes:
            if self.peer in access or access is None:
                await self.connect.commit()
                data_msg.msg = self.m1
            else:
                data_msg.msg = "Нет прав"
        else:
            data_msg.msg = "Не выполнено, проверьте аргументы. (Или данная запись уже есть)"
        await self.connect.close()

    async def BD_LIST(self):
        await self.__connect__()
        ss = ''
        s = ''
        words = await (await self.cursor.execute(self.query)).fetchall()
        await self.connect.close()
        for word in words:
            for ii in range(len(word)):
                if ii == 0:
                    s += f"{word[ii]}"
                else:
                    s += f" {self.sep} {word[ii]}"
            ss += f"{s}\n"
            s = ''
        if ss == '': ss = 'Ничего нет'
        return ss

    async def BD_COUNT(self):
        num = []
        await self.__connect__()
        count = await (await self.cursor.execute(self.query)).fetchall()
        await self.connect.close()
        for n in count: num.append(n[self.on_index])
        if not num: num.append(0)
        return num

    async def get_one_col_list(self):
        l = []
        await self.__connect__()
        edit = await (await self.cursor.execute(self.query)).fetchall()
        await self.connect.close()
        for z in edit: l.append(z[0])
        return l


############################################################################
async def convert_img(inpt, output_name, convert_to):
    ipng = await Image.open(inpt).convert()
    await ipng.save(output_name, convert_to)


############################################################################
def logger():
    """file_log = logging.FileHandler(name, 'a', 'utf-8')
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out), format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)
    logging.info(inf)"""
    pass


############################################################################
def TEXT_SPLIT(OBJ, N):
    return [OBJ[i:i + N] for i in range(0, len(OBJ) - (len(OBJ) // N), N)] if OBJ != 0 else ''


############################################################################
############################################################################

class Debug(object):
    def __init__(self, obj=None, pid=None):
        self.obj = sys.getsizeof(obj)
        self.pid = int(check_output(["pidof", "-s", pid])) if pid is not None else os.getpid()
        self.proc = psutil.Process(self.pid)

    ############################################################################
    def obj_size(self):
        return self.obj

    ############################################################################
    def process_mem_size(self):
        return self.proc.memory_info()

    ############################################################################
    def process_mem_map(self):
        return self.proc.memory_maps()


######################################################################################################################
class json_config:
    def __init__(self):
        self.dictionary = {
            'idGroupTelegram': 0,
            'PEER_CRUSH_EVENT': 0,
            'CAPTCHA_EVENT': 0,
            'OWNER_ALBUM_PHOTO': 0,
            'users_list_warn': [],
            'EVIL_GODS': []
        }
        self.reader = read_file_json(config_file_json)
        if self.reader is not None:
            self.config = {
            ################## Целое число ###############################
            'idGroupTelegram': self.reader['idGroupTelegram'],
            # Общий канал для незарегестрированных чатов
            'PEER_CRUSH_EVENT': self.reader['PEER_CRUSH_EVENT'],
            'CAPTCHA_EVENT': self.reader['CAPTCHA_EVENT'],
            'OWNER_ALBUM_PHOTO': self.reader['OWNER_ALBUM_PHOTO'],
            ################## Списки и строки ###############################
            'users_list_warn': self.reader['users_list_warn'],  # теги оповещения в вк о падении
            'EVIL_GODS': self.reader['EVIL_GODS'],
            }
        else:
            self.config = {}

    ############################################################################
    def return_json(self):
        return self.dictionary

    ############################################################################
    def cfg_json(self):
        return self.config


######################################################################################################################


class FSM(object):

    def __init__(self, obj, target):
        self.obj = str(obj)
        self.target = str(target)
        self.field = f"{self.obj}_{self.target}"

    def get_state(self):
        print(self.field)
        db = pickledb.load("states.db", False)
        try:
            return db[self.field]
        except KeyError:
            return States_cook.NULL.value

    def set_state(self, value):
        db = pickledb.load("states.db", False)
        try:
            db[self.field] = str(value)
            db.dump()
            return True
        except:
            return False

    def check_state(self):
        z = self.get_state()
        print(1, z)
        # print(States_cook)
        # if z[0] in States_cook:
        #    print(z[1])
        #    return z[1]


@dataclass()
class data_msg:
    msg: str
    attachment: str
    doc: str
    keyboard: str

    def __init__(self):
        data_msg.msg = None
        data_msg.attachment = None
        data_msg.doc = None
        data_msg.keyboard = None


@dataclass()
class keyboard_params:
    user_sender: str
    user_respond: str
    conv_msg_id_new: str
    conv_msg_id_old: str
    pay_dir: str

    def __init__(self, user_sender=None, user_respond=None, conv_msg_id_new=None,
                 conv_msg_id_old=None, pay_dir=None):
        self.user_sender = user_sender
        self.user_respond = user_respond
        self.conv_msg_id_new = conv_msg_id_new
        self.conv_msg_id_old = conv_msg_id_old
        self.pay_dir = pay_dir

    def build(self): return [self.user_sender, self.user_respond, self.conv_msg_id_new, self.conv_msg_id_old,
                             self.pay_dir]

    def clear(self):
        self.user_sender = ""
        self.user_respond = ""
        self.conv_msg_id_new = ""
        self.conv_msg_id_old = ""
        self.pay_dir = ""
