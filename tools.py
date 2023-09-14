
from functools import reduce
from itertools import chain
import json, random, string, os, aiosqlite, pickledb,re,glob
from PIL import Image
from CONFIG import config_file_json
from zipstream import AioZipStream
############################################################################


class Patterns:
    user_pattern = r"\[id(\d+)\|(@?\w+)\]"
    club_pattern = r"\[club(\d+)\|(@?\w+)\]"

    def pattern_bool(text,patterns,logic="and")-> bool:
        bools = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches: bools.append(matches)
        if logic == "and": return all(bools)
        if logic == "or": return any(bools)

    def get_mentions(text):
        user_matches = re.findall(Patterns.user_pattern, text)
        club_matches = re.findall(Patterns.club_pattern, text)  
        if user_matches == [] and club_matches == []:
            return None
        else:
            dict_users = [{'id': user[0], 'text': user[1]} for user in user_matches]
            dict_clubs = [{'id': club[0], 'text': club[1]} for club in club_matches]
            dict_inverted_clubs = [{'id': -int(club[0]), 'text': club[1]} for club in club_matches]
            return {"users": dict_users,"clubs": dict_clubs,"invert_ids_clubs":dict_inverted_clubs}

################################ TOOLS ##############################################

class Formatter():
    class DictClass:
        def reverse_dict(obj: dict):
            return dict(reversed(obj.items()))

        def join_dict_keys(obj: list):
            """
            вернет все вложенные ключи
            [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}] -> ['a', 'b', 'c', 'd']
            """
            list(chain.from_iterable(obj.keys() for obj in obj))

        def join_dict(obj: list):
            """
            вернет единый словарь [{'a': 1}, {'b': 2}, {'c': 3}] -> {'a': 1, 'b': 2, 'c': 3}
            """
            return reduce(lambda x, y: {**x, **y}, obj)

        def dict_to_str(obj: dict, sep: str , sep_spec: str):
            """
            вернет строку параметров: ключ{sep}значение
            """
            return f'{sep_spec}'.join('{}{}{}'.format(key, sep, val) for key, val in obj.items())

    def reformat_mention(obj):
        return str(obj).replace("@","[").replace("(","|").replace(")","]")

    def to_tuple(obj):  # li
        return str(list(obj)).replace('[', '').replace(']', '')

    def to_list(obj):
        return list(str(list(obj)).replace('[', '').replace(']', '').split(','))

    def text_split(obj, N):
        return [obj[i:i + N] for i in range(0, len(obj) - (len(obj) // N), N)] if obj != 0 else ''
    
############################################################################

class Writer:

    async def find_file(path):
        return glob.glob(path)

    """async def create_archive(file_path: str, output_path: str):
        with await zipfile.ZipFile(output_path, 'w') as zipf:
            for root, _, files in await os.walk(file_path):
                for file in files:
                    file_path = await os.path.join(root, file)
                    await zipf.write(file_path, os.path.relpath(file_path, output_path))"""

    def create_list_zip(dir):
        listzip = []
        for f in os.listdir(dir):
            fp = os.path.join(dir, f)
            if os.path.isfile(fp):
                listzip.append({'file': fp})
        return listzip
    
    async def create_bytes_archive(file_path):#, output_path: str
        #async with asyncio.Lock():
            byte = []
            aiozip = AioZipStream(file_path, chunksize=32768).stream()
            async for z in aiozip: byte.append(z)
            return b"".join(byte)

    async def create_file_archive(zipname,file_path):#, output_path: str      
        #async with asyncio.Lock():
            aiozip = AioZipStream(file_path, chunksize=32768)
            with open(zipname, mode='wb') as z:
                async for chunk in aiozip.stream():
                    z.write(chunk)


    def write_file(name, getfile):
        with open(name, 'bw') as f: f.write(getfile)


    def read_file_json(name):
        try:
            with open(name, "r") as f:  data = json.load(f)
            return data
        except:
            print("Файл отсутствует или поврежден")

    def write_file_json(name, data):
        with open(name, "w") as f:  json.dump(data, f)



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
        #print(new, new.__dict__)
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


######################################################################################################################
class json_config:
    def __init__(self,name=config_file_json):
        self.sys = {
            'idGroupTelegram': 0,
            'PEER_CRUSH_EVENT': 0,
            'CAPTCHA_EVENT': 0,
            'OWNER_ALBUM_PHOTO': 0,
            'users_list_warn': [],
            'EVIL_GODS': []
        }
        self.name = name
        self.db = pickledb.load(location=self.name,auto_dump=True, sig=True)

    def create(self,dir="sys"):
        if not os.path.isfile(self.name):
            self.db.set(dir, self.sys)

    def read_key(self,dir,key):
        return self.db.get(dir)[key]


######################################################################################################################


class FSM(object):

    def __init__(self, obj, target):
        self.obj = str(obj)
        self.target = str(target)
        self.field = f"{self.obj}_{self.target}"

    def get_state(self,obj):
        print(self.field)
        db = pickledb.load("states.db", False)
        try:
            return db[self.field]
        except KeyError:
            return obj.NULL.value

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

############################################################################
class data_msg:
    def __init__(self, msg: str = None, attachment: str = None, _reply: str = None, keyboard: str = None):
        self.msg = msg
        self.attachment = attachment
        self._reply = _reply
        self.keyboard = keyboard

    def check_empty(self) -> bool:
        return self.msg is not None or self.attachment is not None \
            or self._reply is not None or self.keyboard is not None
    
    async def send(self,obj):
        if self.check_empty():
            await obj.answer(
                message = self.msg,
                attachment  = self.attachment,
                random_id = random.Random().randint(0, 1000000000),
                reply_to  = self._reply,
                forward_messages = None,
                forward  = None,
                sticker_id  = None,
                keyboard  = self.keyboard,
                template  = None,
                payload  = None,
                content_source  = None,
                dont_parse_links  = None,
                disable_mentions  = None,
                intent  = None,
                subscribe_id  = None)


############################################################################
class keyboard_params:
    """
    ### параметры для payload ###
    user_sender: str  - id отправителя
    user_recipient: str - id адресата
    conv_msg_id_old: str - запоминает id сообщения с созданной клавиатурой
    pay_dir: str - доп параметры
    """

    def __init__(self, user_sender=False, user_recipient=False,conv_msg_id_old=False, pay_dir=False):
        self.user_sender = user_sender
        self.user_recipient = user_recipient
        self.conv_msg_id_old = conv_msg_id_old
        self.pay_dir = pay_dir

    def build(self): return {"sender":    self.user_sender, 
                             "recipient": self.user_recipient, 
                             "msg_old": self.conv_msg_id_old,
                             "dir":     self.pay_dir}
 