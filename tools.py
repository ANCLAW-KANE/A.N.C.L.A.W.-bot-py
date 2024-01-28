import random, json , pickledb, aiofiles
from datetime import datetime, timedelta
from functools import reduce
from itertools import chain
from os import listdir , path
from re import findall , compile
from glob import glob
from math import floor
from aiohttp import ClientSession
from PIL import Image
from CONFIG import config_file_json
from zipstream.aiozipstream import AioZipStream
from enums import size_values, Timestamp
from loguru import logger
from typing import NamedTuple

############################################################################


    
class Patterns:
    user_pattern =   r"\[id(\d+)\|(@?[^\]]+)\]"
    club_pattern = r"\[club(\d+)\|(@?[^\]]+)\]"
    chat_id_pattern = r"[0-9]{1,10}"
    id_telegram_chat_pattern = r"-[0-9]{9,13}"
    chance_pattern = r"100|\b[0-9]{1,2}\b"
    md5 = r"([0-9a-f]{1,32})"
    
    def pattern_bool(text,patterns,logic="and")-> bool:
        bools = []
        for pattern in patterns:
            matches = findall(pattern, text)
            if matches: bools.append(matches)
        if len(bools) > 0:
            if logic == "and": return all(bools)
            if logic == "or": return any(bools)
        else: return False

    def get_mentions(text):
        user_matches = findall(Patterns.user_pattern, text)
        club_matches = findall(Patterns.club_pattern, text)  
        if user_matches == [] and club_matches == []:
            return None
        else:
            dict_users = [{'id': user[0], 'text': user[1]} for user in user_matches]
            dict_clubs = [{'id': club[0], 'text': club[1]} for club in club_matches]
            dict_inverted_clubs = [{'id': -int(club[0]), 'text': club[1]} for club in club_matches]
            return {"users": dict_users,"clubs": dict_clubs,"invert_ids_clubs":dict_inverted_clubs}
############################################################################

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

    def empty_filter(obj, type_ = 'str-list'):
        if type_ == 'str-list': return list(filter(lambda x: x != '' or x != '\n', obj.split(sep=' ')))
        if type_ == 'str': return obj.replace("\n\n", "\n").replace("\n ", "\n")
        if type_ == 'list': return list(filter(lambda x: x != '' or x != '\n', obj))
        
    def str_to_int_iter(obj):
        return list(map(lambda x: int(x),Formatter.empty_filter(obj)))
    
    def reformat_mention(obj):
        return str(obj).replace("@","[").replace("(","|").replace(")","]")

    def to_tuple(obj):  # li
        return str(list(obj)).replace('[', '').replace(']', '')

    def to_list(obj):
        return list(str(list(obj)).replace('[', '').replace(']', '').split(','))

    def text_split(obj, N):
        return [obj[i:i + N] for i in range(0, len(obj) - (len(obj) // N), N)] if obj != 0 else ''
    
    def emojy_format(obj):
        match obj:
            case 1: obj = '✅'
            case 0: obj = '⛔'
            case _: obj = obj
        return obj
    
    def separator_list(obj,sep):
        return '\n'.join(
            [f' {sep} '.join([str(word[ii]) for ii in range(len(word))]) for word in obj])

############################################################################

class Writer:

    async def find_file(path):
        return glob(path)

    def create_list_zip(dir):
        listzip = []
        for f in listdir(dir):
            fp = path.join(dir, f)
            if path.isfile(fp):
                listzip.append({'file': fp})
        return listzip
    
    async def create_bytes_archive(file_path):
            byte = []
            aiozip = AioZipStream(file_path, chunksize=32768).stream()
            async for z in aiozip: byte.append(z)
            return b"".join(byte)

    async def create_file_archive(zipname,file_path):
            aiozip = AioZipStream(file_path, chunksize=32768)
            with open(zipname, mode='wb') as z:
                async for chunk in aiozip.stream():
                    z.write(chunk)

    def write_file(name, getfile):
        with open(name, 'bw') as f: f.write(getfile)

    def read_file_json(name):
        try:
            with open(name, "r") as f:  
                data = json.load(f)
            return data
        except:
            print("Файл отсутствует или поврежден")

    def write_file_json(name, data):
        with open(name, "w") as f:  json.dump(data, f)

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
        if not path.isfile(self.name):
            self.db.set(dir, self.sys)

    def read_key(self,dir,key):
        return self.db.get(dir)[key]
    
    def input_key(self,key,value,_type,dir='sys'):
        self.db.db[dir][key] = _type(value)
        self.db.dump()
    
    def extend_key_list(self,key,value,_type,dir='sys'):
        self.db.db[dir][key].append(_type(value))
        self.db.dump()
    
    def delete_key_list(self,key,value,_type,dir='sys'):
        self.db.db[dir][key].remove(_type(value))
        self.db.dump()
     
    def get_key_list(self,dir='sys'):
        return list(self.db.db[dir].keys())



######################################################################################################################

class data_msg:
    def __init__(self, msg: str = None, attachment: str = None, _reply: str = None, keyboard: str = None):
        self.msg = msg
        self.attachment = attachment
        self._reply = _reply
        self.keyboard = keyboard

    def check_empty(self) -> bool:
        return (self.msg and str(self.msg).find('None') == -1) or self.attachment or self._reply or self.keyboard 
    
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
                subscribe_id  = None
            )


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

    def build(self): 
        return {
            "sender": self.user_sender, 
            "recipient": self.user_recipient, 
            "msg_old": self.conv_msg_id_old,
            "dir": self.pay_dir
                }
 

 ############################################################################
########################### Functions ######################################
def check_index(obj,index):
    try: return obj[index]
    except: return None

def remove_mention(text):
    txt = text.split()
    return [element for element in txt if Patterns.pattern_bool(element,[Patterns.user_pattern, Patterns.club_pattern]) == False]

def time_media(time):
    hours = time // 3600
    minutes = (time % 3600) // 60
    seconds = time % 60
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return formatted_time

def parse_time(time):
    try:
        now = datetime.now().replace(second=0, microsecond=0)
        data = remove_mention(time)
        years = now.year
        months = now.month
        days = 0
        hours = 0
        minutes = 0
        for i in range(0, len(data), 2):
            value = int(data[i])
            unit = data[i + 1]
            if unit in Timestamp.year.value: 
                if value < 1 or value > 9999 : return 'Недопустимый год.'
                years = now.year + value 
            if unit in Timestamp.month.value: 
                if value < 1 or value > 12 : return'Недопустимый месяц.'
                months = now.month + value 
            if unit in Timestamp.day.value: 
                if value < 1 or value > 31 : return 'Недопустимый день.'
                days = value
            if unit in Timestamp.hour.value:
                if value < 0 or value > 23 : return 'Недопустимый час.'
                hours = value 
            if unit in Timestamp.minute.value:
                if value < 0 or value > 59 : return 'Недопустимое количество минут.'
                minutes = value 

        if years == now.year and months == now.month and days == 0 and hours == 0 and minutes == 0: return 'Вы не указали время или оно менее минуты.'
        else:
            if months > 12:
                quotient, remainder = divmod(months, 12)
                years += quotient
                months = remainder
            calc = datetime(years, months, now.day, now.hour, now.minute) + timedelta(days=days, hours=hours, minutes=minutes)
            return {'calc_time': calc ,'current_time': now}#.strftime('%Y-%m-%d %H:%M')
    except Exception as e: 
        logger.error(e)
        return 'Неверный формат времени'


def unpack_keys(obj,emj):
    result = ''
    for key in obj.keys():
        if isinstance(key, tuple):
            string_tuple = ' | '.join(map(str, key))
            result += f"{emj} - < {string_tuple} >\n"
        else:
            result += f"{emj} - {key}\n"
    return result
            
def check_dict_key(dictonary,keyword):
    matching_keys = [key for key in dictonary.keys() if keyword in key]
    if matching_keys:
        value = dictonary[matching_keys[0]]
        return value
    else: return None

async def convert_img(inpt, output_name, convert_to):
    ipng = await Image.open(inpt).convert()
    await ipng.save(output_name, convert_to)

async def download_image(url: str,path: str = None, peer=None):
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_content = await response.read()
                if path or peer:
                    async with aiofiles.open("{}{}\{}".format(path,peer,random.randrange(1,100000)), "wb") as file:
                        await file.write(image_content)
                else : return image_content


def calc_albums(obj):
    offset_max = 0
    parse_album = str(random.choice(obj)).split(sep='_')
    if int(parse_album[1]) > 50: offset_max = floor(int(parse_album[1]) / 50)
    Albums = NamedTuple('Albums', [('parse_album', list), ('offset_max', int)])
    return Albums(parse_album,offset_max)


async def get_sort_all_albums(api_obj):
    listAlbum = []
    items = api_obj.get('response', api_obj).get('items', None)
    if items:
        for item in items:
            album = str(item['id'])
            size = str(item['size'])
            privacy = str(item['privacy_view'])
            if compile("'all'").search(privacy): listAlbum.append(album + '_' + size)
        return listAlbum

def get_max_photo(obj):
    try:
        urls = [size.url for size in obj.photo.sizes]
        types_ = [size.type.value for size in obj.photo.sizes]
    except:
        urls = [size['url'] for size in obj[0]['sizes']]
        types_ = [size['type'] for size in obj[0]['sizes']]
    max_size = sorted(types_, key=lambda x: size_values.index(x))[-1]
    urldict = dict(zip(types_, urls))
    return urldict.get(max_size)
